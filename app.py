"""
Secure Excel File Viewer with Activity Tracking
This application serves Excel files through a web interface without allowing downloads
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_cors import CORS
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import uuid
import hashlib
import tempfile
import openpyxl
from cryptography.fernet import Fernet
import base64
from excel_protection import create_macro_protected_excel, create_encrypted_excel
from activity_database import ActivityDatabase
from file_monitoring import generate_monitoring_script
from system_file_monitor import start_file_monitoring, stop_file_monitoring

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
CORS(app)

# Start system-level file monitoring
print("🔍 Starting system-level file monitoring...")
system_monitor = start_file_monitoring()
print("✅ System file monitoring active")# Configuration
EXCEL_FILES_DIR = 'secure_files'
ACTIVITY_LOG_FILE = 'activity_logs.json'

# Ensure directories exist
os.makedirs(EXCEL_FILES_DIR, exist_ok=True)

# Initialize database
db = ActivityDatabase()

# Activity tracking storage (for backward compatibility)
activity_logs = []

def log_activity(user_session, activity_type, file_name, additional_info=None):
    """Log user activity with timestamp to both JSON and database"""
    activity = {
        'timestamp': datetime.now().isoformat(),
        'session_id': user_session,
        'activity': activity_type,
        'file_name': file_name,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'additional_info': additional_info or {}
    }
    
    # Add to memory (for real-time display)
    activity_logs.append(activity)
    
    # Add to database (for historical tracking)
    db.add_activity(
        timestamp=activity['timestamp'],
        session_id=activity['session_id'],
        activity=activity['activity'],
        file_name=activity['file_name'],
        ip_address=activity['ip_address'],
        user_agent=activity['user_agent'],
        additional_info=activity['additional_info']
    )
    
    # Save to file for persistence
    try:
        with open(ACTIVITY_LOG_FILE, 'w') as f:
            json.dump(activity_logs, f, indent=2)
    except Exception as e:
        print(f"Error saving activity log: {e}")
    
    print(f"Activity logged: {activity_type} for {file_name} by session {user_session}")

def generate_session_id():
    """Generate unique session ID"""
    return str(uuid.uuid4())

@app.route('/')
def index():
    """Main page showing available files"""
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()
    
    # List available Excel files with metadata
    excel_files = []
    if os.path.exists(EXCEL_FILES_DIR):
        for file in os.listdir(EXCEL_FILES_DIR):
            if file.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(EXCEL_FILES_DIR, file)
                try:
                    # Get file stats
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Get sheet count
                    sheets_count = 0
                    try:
                        wb = openpyxl.load_workbook(file_path, read_only=True)
                        sheets_count = len(wb.sheetnames)
                        wb.close()
                    except:
                        sheets_count = 1  # Default to 1 if can't read
                    
                    # Format file size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    
                    excel_files.append({
                        'name': file,
                        'filename': file,
                        'modified': modified_time.strftime('%Y-%m-%d %H:%M'),
                        'size': size_str,
                        'sheets_count': sheets_count
                    })
                except Exception as e:
                    # If there's an error reading file metadata, add basic info
                    excel_files.append({
                        'name': file,
                        'filename': file,
                        'modified': 'Unknown',
                        'size': 'Unknown',
                        'sheets_count': 1
                    })
    
    log_activity(session['session_id'], 'PAGE_VISIT', 'index', {'files_available': len(excel_files)})
    
    return render_template('index.html', files=excel_files)

@app.route('/view/<filename>')
def view_file(filename):
    """Secure file viewer"""
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()
    
    file_path = os.path.join(EXCEL_FILES_DIR, filename)
    
    if not os.path.exists(file_path):
        log_activity(session['session_id'], 'FILE_NOT_FOUND', filename)
        return "File not found", 404
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
        
        # Convert to JSON format for the template
        sheets_data = {}
        for sheet_name, sheet_data in df.items():
            # Convert DataFrame to list of dictionaries
            sheets_data[sheet_name] = sheet_data.to_dict('records')
        
        log_activity(session['session_id'], 'FILE_OPENED', filename, {
            'sheets_count': len(sheets_data),
            'sheet_names': list(sheets_data.keys())
        })
        
        # Convert to JSON string for template
        import json
        excel_data_json = json.dumps(sheets_data)
        
        print(f"DEBUG: Sending data for {filename} with {len(sheets_data)} sheets")
        print(f"DEBUG: Sheet names: {list(sheets_data.keys())}")
        
        return render_template('viewer.html', 
                             filename=filename, 
                             excel_data=excel_data_json,
                             session_id=session['session_id'])
    
    except Exception as e:
        log_activity(session['session_id'], 'FILE_ERROR', filename, {'error': str(e)})
        return f"Error reading file: {str(e)}", 500

@app.route('/track', methods=['POST'])
def track_activity():
    """Endpoint for client-side activity tracking"""
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    activity_type = data.get('activity')
    filename = data.get('filename')
    additional_info = data.get('info', {})
    
    log_activity(session['session_id'], activity_type, filename, additional_info)
    
    return jsonify({'status': 'logged'})

@app.route('/print/<filename>')
def print_file(filename):
    """Generate print-friendly version"""
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()
    
    file_path = os.path.join(EXCEL_FILES_DIR, filename)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    try:
        df = pd.read_excel(file_path, sheet_name=None)
        sheets_html = {}
        
        for sheet_name, sheet_data in df.items():
            sheets_html[sheet_name] = sheet_data.to_html(classes='print-table', 
                                                        table_id=f'print-sheet-{sheet_name}',
                                                        escape=False)
        
        log_activity(session['session_id'], 'PRINT_REQUESTED', filename, {
            'sheets_count': len(sheets_html)
        })
        
        return render_template('print.html', 
                             filename=filename, 
                             sheets=sheets_html)
    
    except Exception as e:
        log_activity(session['session_id'], 'PRINT_ERROR', filename, {'error': str(e)})
        return f"Error preparing file for print: {str(e)}", 500

@app.route('/admin/logs')
def admin_logs():
    """View activity logs (admin only)"""
    return render_template('admin.html', logs=activity_logs)

@app.route('/download-secure/<filename>')
def download_secure(filename):
    """Generate encrypted, edit-only Excel file for download"""
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()
    
    file_path = os.path.join(EXCEL_FILES_DIR, filename)
    
    if not os.path.exists(file_path):
        log_activity(session['session_id'], 'DOWNLOAD_FILE_NOT_FOUND', filename)
        return "File not found", 404
    
    try:
        # Create a protected version of the Excel file with enhanced tracking
        protected_filename = create_macro_protected_excel(
            file_path, 
            filename, 
            session_id=session['session_id'], 
            enhanced_tracking=True
        )
        
        # Debug: Check file creation
        if protected_filename and os.path.exists(protected_filename):
            file_size = os.path.getsize(protected_filename)
            print(f"DEBUG: Protected file created: {protected_filename}")
            print(f"DEBUG: File size: {file_size} bytes")
        else:
            print(f"DEBUG: Failed to create protected file")
            return "Error: Could not create protected file", 500
        
        log_activity(session['session_id'], 'SECURE_DOWNLOAD', filename, {
            'download_type': 'protected_excel',
            'protection_enabled': True,
            'file_format': 'xlsx',
            'file_size': file_size,
            'protected_path': protected_filename
        })
        
        # Register the protected file with the system monitor for tracking
        if system_monitor:
            try:
                system_monitor.register_download(protected_filename, filename, session['session_id'])
                print(f"📋 Registered protected file for system monitoring: {filename}")
            except Exception as e:
                print(f"Warning: Could not register file with system monitor: {e}")
        
        # Get the proper filename for download - use .xlsx for compatibility
        base_name = os.path.splitext(filename)[0]  # Remove any extension
        download_name = f"secure_{base_name}.xlsx"
        
        print(f"DEBUG: Original filename: {filename}")
        print(f"DEBUG: Base name: {base_name}")
        print(f"DEBUG: Download name: {download_name}")
        print(f"DEBUG: Protected file path: {protected_filename}")
        
        # Use send_file for proper file serving
        response = send_file(
            protected_filename,
            as_attachment=True,
            download_name=download_name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Add headers for better compatibility
        response.headers['Content-Length'] = str(file_size)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        print(f"DEBUG: Response headers: {dict(response.headers)}")
        
        return response
    
    except Exception as e:
        log_activity(session['session_id'], 'DOWNLOAD_ERROR', filename, {'error': str(e)})
        return f"Error creating secure file: {str(e)}", 500

@app.route('/test-download/<filename>')
def test_download(filename):
    """Simple test download route"""
    file_path = os.path.join(EXCEL_FILES_DIR, filename)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    # Send original file directly
    return send_file(file_path, as_attachment=True)

@app.route('/test-protected/<filename>')
def test_protected_download(filename):
    """Test protected file creation and download"""
    file_path = os.path.join(EXCEL_FILES_DIR, filename)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    try:
        # Create protected version
        protected_file = create_macro_protected_excel(file_path, filename)
        
        if protected_file and os.path.exists(protected_file):
            file_size = os.path.getsize(protected_file)
            base_name = os.path.splitext(filename)[0]
            download_name = f"test_secure_{base_name}.xlsx"
            
            print(f"TEST: Created {protected_file}, size: {file_size}, download as: {download_name}")
            
            return send_file(
                protected_file,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return "Error creating protected file", 500
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/logs')
def api_logs():
    """API endpoint for activity logs (real-time)"""
    return jsonify(activity_logs)

@app.route('/api/historical-logs')
def api_historical_logs():
    """API endpoint for historical activity logs with filtering"""
    file_name = request.args.get('file_name')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    activity_type = request.args.get('activity_type')
    session_id = request.args.get('session_id')
    limit = int(request.args.get('limit', 1000))
    
    activities = db.get_activities(
        file_name=file_name,
        start_date=start_date,
        end_date=end_date,
        activity_type=activity_type,
        session_id=session_id,
        limit=limit
    )
    
    return jsonify(activities)

@app.route('/api/file-names')
def api_file_names():
    """API endpoint to get available file names"""
    file_names = db.get_file_names()
    return jsonify(file_names)

@app.route('/api/files')
def api_files():
    """API endpoint to get available files with metadata"""
    excel_files = []
    if os.path.exists(EXCEL_FILES_DIR):
        for file in os.listdir(EXCEL_FILES_DIR):
            if file.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(EXCEL_FILES_DIR, file)
                try:
                    stat = os.stat(file_path)
                    excel_files.append({
                        'name': file,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception as e:
                    excel_files.append({
                        'name': file,
                        'size': 0,
                        'modified': datetime.now().isoformat()
                    })
    return jsonify(excel_files)

@app.route('/api/activity-types')
def api_activity_types():
    """API endpoint to get available activity types"""
    activity_types = db.get_activity_types()
    return jsonify(activity_types)

@app.route('/api/statistics')
def api_statistics():
    """API endpoint for activity statistics"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    stats = db.get_statistics(start_date=start_date, end_date=end_date)
    return jsonify(stats)

@app.route('/admin/audit')
def admin_audit():
    """Enhanced admin audit page with historical data"""
    return render_template('admin_audit.html')

@app.route('/security/monitor')
def security_monitor():
    """Security monitoring dashboard for file system events"""
    return render_template('security_monitor.html')

@app.route('/api/file-monitoring', methods=['POST'])
def api_file_monitoring():
    """API endpoint to receive file monitoring events from client-side"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract monitoring data
        file_id = data.get('fileId', 'unknown')
        session_id = data.get('sessionId', 'unknown')
        event_type = data.get('eventType', 'UNKNOWN_EVENT')
        event_data = data.get('eventData', {})
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Log the monitoring event to database
        db.add_activity(
            timestamp=timestamp,
            session_id=session_id,
            activity=f"CLIENT_MONITOR_{event_type}",
            file_name=file_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            additional_info={
                'monitoring_event': True,
                'event_type': event_type,
                'event_data': event_data,
                'client_timestamp': timestamp
            }
        )
        
        # Analyze for security threats
        threat_level = analyze_threat_level(event_type, event_data)
        
        if threat_level == 'HIGH':
            # Log high-priority security event
            db.add_activity(
                timestamp=datetime.now().isoformat(),
                session_id=session_id,
                activity="SECURITY_THREAT_DETECTED",
                file_name=file_id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                additional_info={
                    'threat_level': threat_level,
                    'threat_type': event_type,
                    'threat_data': event_data
                }
            )
        
        return jsonify({
            'status': 'logged',
            'threat_level': threat_level,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error processing monitoring data: {e}")
        return jsonify({'error': 'Failed to process monitoring data'}), 500

@app.route('/api/security-events')
def api_security_events():
    """API endpoint to get security-related monitoring events"""
    try:
        # Get parameters for filtering
        file_name = request.args.get('file_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        threat_level = request.args.get('threat_level', 'ALL')
        limit = int(request.args.get('limit', 500))
        
        # Get monitoring events from database
        activities = db.get_activities(
            file_name=file_name,
            start_date=start_date,
            end_date=end_date,
            activity_type="CLIENT_MONITOR_%",  # SQL LIKE pattern
            limit=limit
        )
        
        # Filter by threat level if specified
        if threat_level != 'ALL':
            activities = [
                activity for activity in activities 
                if activity.get('additional_info', {}).get('threat_level') == threat_level
            ]
        
        # Add threat analysis
        for activity in activities:
            if activity.get('additional_info', {}).get('monitoring_event'):
                event_type = activity['additional_info'].get('event_type', '')
                event_data = activity['additional_info'].get('event_data', {})
                activity['threat_analysis'] = analyze_threat_level(event_type, event_data)
        
        return jsonify(activities)
        
    except Exception as e:
        print(f"Error retrieving security events: {e}")
        return jsonify({'error': 'Failed to retrieve security events'}), 500

@app.route('/monitoring-script/<file_id>')
def get_monitoring_script(file_id):
    """Generate and serve client-side monitoring script for specific file"""
    try:
        server_url = request.host_url.rstrip('/')
        script_content = generate_monitoring_script(file_id, server_url)
        
        # Log script request
        log_activity(
            session.get('user_id', 'anonymous'),
            'MONITORING_SCRIPT_REQUESTED',
            file_id,
            {'server_url': server_url}
        )
        
        response = app.response_class(
            response=script_content,
            status=200,
            mimetype='application/javascript'
        )
        response.headers['Content-Disposition'] = f'inline; filename="monitoring_{file_id}.js"'
        return response
        
    except Exception as e:
        print(f"Error generating monitoring script: {e}")
        return jsonify({'error': 'Failed to generate monitoring script'}), 500

def analyze_threat_level(event_type, event_data):
    """Analyze the threat level of a monitoring event"""
    
    # High threat events
    high_threat_events = [
        'CLIPBOARD_COPY_ATTEMPT',
        'CLIPBOARD_CUT_ATTEMPT',
        'SUSPICIOUS_KEYPRESS',
        'FILE_DRAG_ATTEMPT',
        'PRINT_ATTEMPT',
        'SAVE_ATTEMPT'
    ]
    
    # Medium threat events
    medium_threat_events = [
        'WINDOW_FOCUS_LOST',
        'VISIBILITY_CHANGE',
        'FILE_DROP_DETECTED',
        'DEVELOPER_TOOLS_DETECTED'
    ]
    
    # Check for specific high-risk activities
    if event_type in high_threat_events:
        return 'HIGH'
    elif event_type in medium_threat_events:
        return 'MEDIUM'
    elif 'ATTEMPT' in event_type or 'BLOCKED' in event_type:
        return 'MEDIUM'
    else:
        return 'LOW'

@app.route('/api/log-activity', methods=['POST'])
def api_log_activity():
    """API endpoint for logging user activities from frontend"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        session_id = session.get('session_id', 'unknown')
        action = data.get('action', 'unknown')
        page = data.get('page', 'unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Log the activity
        log_activity(session_id, action.upper(), page, data)
        
        return jsonify({'status': 'logged', 'timestamp': timestamp})
        
    except Exception as e:
        print(f"Error logging activity: {e}")
        return jsonify({'error': 'Failed to log activity'}), 500

@app.route('/api/security-metrics')
def api_security_metrics():
    """API endpoint for security dashboard metrics"""
    try:
        # Get recent activities for metrics
        activities = db.get_activities(limit=1000)
        
        # Calculate metrics
        total_views = len([a for a in activities if a.get('activity') == 'FILE_OPENED'])
        download_attempts = len([a for a in activities if 'DOWNLOAD' in a.get('activity', '')])
        security_alerts = len([a for a in activities if a.get('activity') == 'SECURITY_THREAT_DETECTED'])
        
        # Get unique sessions for active sessions count
        unique_sessions = len(set(a.get('session_id') for a in activities if a.get('session_id')))
        
        # Prepare timeline data (last 24 hours)
        now = datetime.now()
        hours = []
        views_data = []
        events_data = []
        
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            hours.append(hour_start.strftime('%H:00'))
            
            hour_views = len([a for a in activities 
                            if a.get('activity') == 'FILE_OPENED' 
                            and hour_start <= datetime.fromisoformat(a.get('timestamp', '')) < hour_end])
            hour_events = len([a for a in activities 
                             if hour_start <= datetime.fromisoformat(a.get('timestamp', '')) < hour_end])
            
            views_data.append(hour_views)
            events_data.append(hour_events)
        
        # Reverse to show chronological order
        hours.reverse()
        views_data.reverse()
        events_data.reverse()
        
        # Get recent events
        recent_events = []
        for activity in activities[:10]:
            recent_events.append({
                'type': activity.get('activity', 'Unknown'),
                'description': f"User accessed {activity.get('file_name', 'system')}",
                'timestamp': activity.get('timestamp', ''),
                'user': activity.get('session_id', 'unknown')[:8],
                'ip': '127.0.0.1',  # Placeholder
                'severity': 'info'
            })
        
        # Get alerts (high threat activities)
        alerts = []
        for activity in activities:
            if activity.get('activity') == 'SECURITY_THREAT_DETECTED':
                alerts.append({
                    'title': 'Security Threat Detected',
                    'message': f"Threat detected in {activity.get('file_name', 'unknown file')}",
                    'timestamp': activity.get('timestamp', ''),
                    'severity': 'danger'
                })
        
        # Get file access summary
        file_access = {}
        for activity in activities:
            if activity.get('activity') == 'FILE_OPENED':
                filename = activity.get('file_name', 'unknown')
                if filename not in file_access:
                    file_access[filename] = {
                        'name': filename,
                        'views': 0,
                        'lastAccess': activity.get('timestamp', '')
                    }
                file_access[filename]['views'] += 1
                if activity.get('timestamp', '') > file_access[filename]['lastAccess']:
                    file_access[filename]['lastAccess'] = activity.get('timestamp', '')
        
        return jsonify({
            'totalViews': total_views,
            'downloadAttempts': download_attempts,
            'securityAlerts': security_alerts,
            'activeSessions': unique_sessions,
            'timeline': {
                'labels': hours,
                'views': views_data,
                'events': events_data
            },
            'events': recent_events,
            'alerts': alerts[:5],  # Limit to 5 most recent
            'fileAccess': list(file_access.values())[:10]  # Limit to 10 most accessed
        })
        
    except Exception as e:
        print(f"Error getting security metrics: {e}")
        return jsonify({'error': 'Failed to get security metrics'}), 500

@app.route('/api/file-security-incident', methods=['POST'])
def api_file_security_incident():
    """API endpoint to receive security incidents from protected Excel files and system monitor"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if this is from the system monitor (new format) or VBA (old format)
        if 'eventType' in data:
            # New format from system monitor
            return handle_system_monitor_incident(data)
        else:
            # Old format from VBA
            return handle_vba_incident(data)
        
    except Exception as e:
        print(f"Error processing security incident: {e}")
        return jsonify({'error': 'Failed to process security incident'}), 500

def handle_system_monitor_incident(data):
    """Handle security incidents from the system monitor"""
    try:
        event_type = data.get('eventType', 'UNKNOWN_EVENT')
        operation = data.get('operation', 'UNKNOWN_OPERATION')
        original_file = data.get('originalFile', 'unknown')
        source_path = data.get('sourcePath', '')
        destination_path = data.get('destinationPath', '')
        process_name = data.get('processName', 'unknown')
        severity = data.get('severity', 'MEDIUM')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Create activity data
        activity_data = {
            'event_type': event_type,
            'operation': operation,
            'source_path': source_path,
            'destination_path': destination_path,
            'process_name': process_name,
            'source': 'SYSTEM_MONITOR',
            'severity': severity
        }
        
        # Determine activity type
        activity_type = f"SYSTEM_{operation}" if operation != 'UNKNOWN_OPERATION' else 'SYSTEM_FILE_OPERATION'
        
        # Log to database
        db.add_activity(
            timestamp=timestamp,
            session_id='SYSTEM_MONITOR',
            activity=activity_type,
            file_name=original_file,
            additional_info=activity_data
        )
        
        # Print alert
        print(f"🚨 SYSTEM SECURITY ALERT: {event_type} - {operation}")
        print(f"   File: {original_file} | Process: {process_name}")
        print(f"   Source: {source_path}")
        if destination_path:
            print(f"   Destination: {destination_path}")
        print(f"   Severity: {severity}")
        
        return jsonify({
            'status': 'logged',
            'event_type': event_type,
            'operation': operation,
            'severity': severity,
            'timestamp': timestamp
        })
        
    except Exception as e:
        print(f"Error processing system monitor incident: {e}")
        return jsonify({'error': 'Failed to process system monitor incident'}), 500

def handle_vba_incident(data):
    """Handle security incidents from VBA macros (original format)"""
    try:
        log_data = data.get('logData', '')
        if not log_data:
            return jsonify({'error': 'No log data provided'}), 400
        
        # Parse the log data
        log_parts = log_data.split('|')
        incident_info = {}
        
        for part in log_parts:
            if ':' in part:
                key, value = part.split(':', 1)
                incident_info[key] = value
        
        # Extract key information
        tracking_id = incident_info.get('TRACKING_ID', 'unknown')
        session_id = incident_info.get('SESSION_ID', 'unknown')
        incident_type = incident_info.get('INCIDENT', 'UNKNOWN_INCIDENT')
        details = incident_info.get('DETAILS', '')
        timestamp = incident_info.get('TIMESTAMP', datetime.now().isoformat())
        filename = incident_info.get('FILE', 'unknown')
        
        # Log as high-priority security event
        activity_data = {
            'tracking_id': tracking_id,
            'incident_type': incident_type,
            'details': details,
            'source': 'PROTECTED_FILE_VBA',
            'severity': 'HIGH',
            'file_origin': filename
        }
        # Determine the appropriate activity type based on incident
        activity_type = map_incident_to_activity(incident_type)
        
        # Log to database
        db.add_activity(
            timestamp=timestamp,
            session_id=session_id,
            activity=activity_type,
            file_name=filename,
            additional_info=activity_data
        )
        
        # Print for monitoring
        print(f"🚨 SECURITY INCIDENT: {incident_type} | File: {filename} | Details: {details}")
        print(f"   Tracking ID: {tracking_id} | Session: {session_id}")
        
        return jsonify({
            'status': 'logged',
            'incident_type': incident_type,
            'tracking_id': tracking_id,
            'timestamp': timestamp,
            'severity': 'HIGH'
        })
        
    except Exception as e:
        print(f"Error processing VBA incident: {e}")
        return jsonify({'error': 'Failed to process VBA incident'}), 500

def map_incident_to_activity(incident_type):
    """Map incident types to appropriate activity categories"""
    incident_mapping = {
        'SAVE_AS_ATTEMPT': 'UNAUTHORIZED_SAVE_ATTEMPT',
        'LOCATION_CHANGE_SAVE': 'FILE_LOCATION_CHANGE',
        'PRINT_ATTEMPT': 'UNAUTHORIZED_PRINT_ATTEMPT',
        'REMOVABLE_DRIVE_DETECTED': 'REMOVABLE_DRIVE_ACCESS',
        'CLOUD_STORAGE_DETECTED': 'CLOUD_STORAGE_ACCESS',
        'FILE_COPY_DETECTED': 'UNAUTHORIZED_FILE_COPY',
        'CLIPBOARD_ACCESS': 'DATA_COPY_ATTEMPT',
        'LARGE_SELECTION_COPY': 'BULK_DATA_SELECTION',
        'SCREEN_CAPTURE_ATTEMPT': 'SCREEN_CAPTURE_DETECTED',
        'BROWSER_DETECTED': 'POTENTIAL_UPLOAD_RISK',
        'NETWORK_ACTIVITY': 'SUSPICIOUS_NETWORK_ACTIVITY',
        'OFF_HOURS_ACCESS': 'OFF_HOURS_FILE_ACCESS',
        'PASSWORD_REMOVED': 'SECURITY_TAMPERING',
        'FILE_ACCESS': 'PROTECTED_FILE_ACCESS'
    }
    
    return incident_mapping.get(incident_type, 'UNKNOWN_SECURITY_INCIDENT')

@app.route('/api/system-monitor-report')
def api_system_monitor_report():
    """Get system monitor security report"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        if system_monitor:
            report = system_monitor.get_security_report(hours=hours)
            return jsonify(report)
        else:
            return jsonify({
                'summary': {
                    'total_incidents': 0,
                    'high_severity': 0,
                    'medium_severity': 0
                },
                'incidents': [],
                'message': 'System monitor not available'
            })
    
    except Exception as e:
        print(f"Error getting system monitor report: {e}")
        return jsonify({'error': 'Failed to get system monitor report'}), 500

if __name__ == '__main__':
    # Migrate existing JSON logs to database on startup
    if os.path.exists(ACTIVITY_LOG_FILE):
        try:
            db.migrate_json_logs(ACTIVITY_LOG_FILE)
            print("[SUCCESS] Migrated existing logs to database")
        except Exception as e:
            print(f"[WARNING] Could not migrate logs: {e}")
    
    print("Starting Secure Excel Viewer...")
    print("Upload your Excel files to the 'secure_files' directory")
    print("Access the application at: http://localhost:5000")
    print("Admin audit: http://localhost:5000/admin/audit")
    print("Security monitor: http://localhost:5000/security/monitor")
    
    try:
        app.run(debug=False, host='127.0.0.1', port=5000, threaded=True)
    except Exception as e:
        print(f"Error starting server: {e}")
    finally:
        # Clean up system monitor on shutdown
        if system_monitor:
            print("🛑 Stopping system file monitor...")
            stop_file_monitoring()
            print("✅ System monitor stopped")
        input("Press Enter to exit...")
