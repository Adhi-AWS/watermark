import os
import hashlib
import time
import json
import threading
import sqlite3
import requests
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32file
import win32con
import psutil
import logging

# Import browser upload monitor
try:
    from browser_upload_monitor import BrowserUploadMonitor
    BROWSER_MONITOR_AVAILABLE = True
except ImportError:
    BROWSER_MONITOR_AVAILABLE = False
    print("⚠️  Browser upload monitoring not available - install pywin32 for full functionality")

class FileTrackingDatabase:
    def __init__(self, db_path='file_tracking.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the file tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table for tracking protected files
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS protected_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT UNIQUE NOT NULL,
                    original_name TEXT NOT NULL,
                    download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    download_session TEXT,
                    file_size INTEGER,
                    fingerprint TEXT
                )
            ''')
            
            # Table for tracking file copies and movements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    source_path TEXT,
                    destination_path TEXT,
                    file_hash TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    detected_by TEXT,
                    process_name TEXT,
                    severity TEXT DEFAULT 'MEDIUM'
                )
            ''')
            
            # Table for file access attempts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    file_hash TEXT,
                    access_type TEXT NOT NULL,
                    process_name TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    blocked BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
    
    def register_protected_file(self, file_path, original_name, session_id, file_hash=None):
        """Register a newly downloaded protected file"""
        if not file_hash:
            file_hash = self.calculate_file_hash(file_path)
        
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        fingerprint = self.generate_file_fingerprint(file_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO protected_files 
                (file_hash, original_name, download_session, file_size, fingerprint)
                VALUES (?, ?, ?, ?, ?)
            ''', (file_hash, original_name, session_id, file_size, fingerprint))
            conn.commit()
        
        return file_hash
    
    def log_file_operation(self, operation_type, source_path, destination_path=None, 
                          detected_by='FILE_MONITOR', process_name=None, severity='MEDIUM'):
        """Log file copy, move, or access operations"""
        file_hash = self.calculate_file_hash(source_path) if os.path.exists(source_path) else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO file_operations 
                (operation_type, source_path, destination_path, file_hash, detected_by, process_name, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (operation_type, source_path, destination_path, file_hash, detected_by, process_name, severity))
            conn.commit()
    
    def is_protected_file(self, file_path):
        """Check if a file is a protected file based on hash"""
        file_hash = self.calculate_file_hash(file_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT original_name FROM protected_files WHERE file_hash = ?', (file_hash,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of a file"""
        if not os.path.exists(file_path):
            return None
        
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return None
    
    def generate_file_fingerprint(self, file_path):
        """Generate a unique fingerprint for the file"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        fingerprint_data = {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'hash_preview': self.calculate_file_hash(file_path)[:16]  # First 16 chars
        }
        return json.dumps(fingerprint_data, sort_keys=True)

class ProtectedFileHandler(FileSystemEventHandler):
    def __init__(self, tracking_db, server_url='http://127.0.0.1:5000', logger=None):
        self.tracking_db = tracking_db
        self.server_url = server_url
        self.monitored_directories = set()
        self.logger = logger or logging.getLogger(__name__)

        # Add common directories to monitor
        user_profile = os.environ.get('USERPROFILE', '')
        self.monitored_directories.update([
            os.path.join(user_profile, 'Downloads'),
            os.path.join(user_profile, 'Desktop'),
            os.path.join(user_profile, 'Documents'),
            'C:\\temp',
            'C:\\tmp'
        ])

    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            if self.tracking_db.is_protected_file(event.src_path):
                self.check_and_log_file_operation('FILE_COPIED', event.src_path)
            else:
                self.check_and_log_file_operation('FILE_CREATED', event.src_path)
    
    def on_moved(self, event):
        """Handle file move/rename events"""
        if not event.is_directory:
            self.check_and_log_file_operation('FILE_MOVED', event.src_path, event.dest_path)
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            self.check_and_log_file_operation('FILE_MODIFIED', event.src_path)
    
    def check_and_log_file_operation(self, operation_type, source_path, dest_path=None):
        """Check if the file is protected and log the operation"""
        try:
            # Check if this is a protected file
            original_name = self.tracking_db.is_protected_file(source_path)
            
            if original_name:
                # Get current process information
                current_process = psutil.Process()
                process_name = current_process.name()
                
                # Determine severity
                severity = self.determine_severity(operation_type, source_path, dest_path)
                
                # Log to database
                self.tracking_db.log_file_operation(
                    operation_type=operation_type,
                    source_path=source_path,
                    destination_path=dest_path,
                    detected_by='SYSTEM_MONITOR',
                    process_name=process_name,
                    severity=severity
                )

                # Send security incident to server
                self.send_security_incident({
                    'eventType': 'PROTECTED_FILE_OPERATION',
                    'operation': operation_type,
                    'originalFile': original_name,
                    'sourcePath': source_path,
                    'destinationPath': dest_path,
                    'processName': process_name,
                    'severity': severity,
                    'timestamp': datetime.now().isoformat()
                })
                self.logger.warning(
                    f"{operation_type} on protected file '{original_name}' | "
                    f"Source: {source_path} | "
                    f"Destination: {dest_path if dest_path else 'N/A'} | "
                    f"Process: {process_name} | Severity: {severity}"
                )
        
        except Exception as e:
            print(f"Error checking file operation: {e}")
    
    def determine_severity(self, operation_type, source_path, dest_path=None):
        """Determine the severity of the file operation"""
        # High severity operations
        if operation_type in ['FILE_MOVED', 'FILE_COPIED']:
            if dest_path:
                # Check if file is being moved to removable media or network drives
                if any(dest_path.startswith(drive) for drive in ['D:', 'E:', 'F:', 'G:', 'H:']):
                    return 'HIGH'
                # Check if file is being moved to cloud sync folders
                cloud_indicators = ['onedrive', 'dropbox', 'googledrive', 'icloud']
                if any(indicator in dest_path.lower() for indicator in cloud_indicators):
                    return 'HIGH'
        
        # Medium severity for most operations
        return 'MEDIUM'
    
    def send_security_incident(self, incident_data):
        """Send security incident to the Flask server"""
        try:
            requests.post(
                f"{self.server_url}/api/file-security-incident",
                json=incident_data,
                timeout=5
            )
        except:
            pass  # Fail silently if server is not available

class SystemFileMonitor:
    def __init__(self, server_url='http://127.0.0.1:5000'):
        self.tracking_db = FileTrackingDatabase()
        self.server_url = server_url
        self.observer = Observer()
        self.running = False

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('file_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # File system handler with logger
        self.handler = ProtectedFileHandler(self.tracking_db, server_url, logger=self.logger)

        # Initialize browser upload monitor if available
        if BROWSER_MONITOR_AVAILABLE:
            self.browser_monitor = BrowserUploadMonitor(server_url)
            self.browser_observer = None
        else:
            self.browser_monitor = None
    
    def start_monitoring(self, directories=None):
        """Start monitoring file system for protected file operations"""
        if directories is None:
            directories = self.handler.monitored_directories
        
        self.logger.info("🔍 Starting system-level file monitoring...")
        
        for directory in directories:
            if os.path.exists(directory):
                self.observer.schedule(self.handler, directory, recursive=True)
                self.logger.info(f"📁 Monitoring directory: {directory}")
        
        self.observer.start()
        self.running = True
        
        # Start background processes scanning
        threading.Thread(target=self.monitor_processes, daemon=True).start()
        
        # Start browser upload monitoring if available
        if self.browser_monitor:
            self.logger.info("🌐 Starting browser upload monitoring...")
            try:
                self.browser_observer = self.browser_monitor.start_monitoring()
                self.logger.info("✅ Browser upload monitoring started")
            except Exception as e:
                self.logger.error(f"❌ Failed to start browser monitoring: {e}")
        
        self.logger.info("✅ File monitoring system started")
    
    def monitor_processes(self):
        """Monitor running processes for suspicious file operations"""
        while self.running:
            try:
                # Look for processes that might be copying or moving files
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        proc_info = proc.info
                        cmdline_data = proc_info.get('cmdline', [])
                        
                        # Handle case where cmdline might not be a list
                        if isinstance(cmdline_data, list):
                            cmdline = ' '.join(cmdline_data)
                        else:
                            cmdline = str(cmdline_data) if cmdline_data else ''
                        
                        # Check for copy/move operations
                        suspicious_commands = ['copy', 'xcopy', 'robocopy', 'move', 'mv', 'cp']
                        if any(cmd in cmdline.lower() for cmd in suspicious_commands):
                            # Check if any protected files are involved
                            self.check_command_for_protected_files(proc_info, cmdline)
                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                time.sleep(5)  # Check every 5 seconds
            
            except Exception as e:
                self.logger.error(f"Error in process monitoring: {e}")
                time.sleep(10)
    
    def check_command_for_protected_files(self, proc_info, cmdline):
        """Check if a command line operation involves protected files"""
        try:
            # Extract file paths from command line
            words = cmdline.split()
            for word in words:
                if word.endswith(('.xlsx', '.xlsm')) and os.path.exists(word):
                    original_name = self.tracking_db.is_protected_file(word)
                    if original_name:
                        self.tracking_db.log_file_operation(
                            operation_type='COMMAND_LINE_ACCESS',
                            source_path=word,
                            detected_by='PROCESS_MONITOR',
                            process_name=proc_info.get('name', 'unknown'),
                            severity='HIGH'
                        )
                        
                        self.handler.send_security_incident({
                            'eventType': 'COMMAND_LINE_FILE_ACCESS',
                            'originalFile': original_name,
                            'commandLine': cmdline,
                            'processName': proc_info.get('name', 'unknown'),
                            'processId': proc_info.get('pid'),
                            'severity': 'HIGH',
                            'timestamp': datetime.now().isoformat()
                        })

                        self.logger.warning(
                            f"COMMAND_LINE_ACCESS on protected file '{original_name}' | "
                            f"Command: {cmdline} | Process: {proc_info.get('name', 'unknown')}"
                        )
        
        except Exception as e:
            self.logger.debug(f"Error checking command for protected files: {e}")
    
    def register_download(self, file_path, original_name, session_id):
        """Register a newly downloaded protected file for monitoring"""
        file_hash = self.tracking_db.register_protected_file(file_path, original_name, session_id)
        # Log the download as an operation for complete audit trail
        try:
            self.tracking_db.log_file_operation(
                operation_type='FILE_DOWNLOADED',
                source_path=file_path,
                detected_by='DOWNLOAD',
                process_name='SYSTEM',
                severity='LOW'
            )
        except Exception as e:
            self.logger.debug(f"Failed to log download operation: {e}")

        self.logger.info(
            f"Protected file downloaded: {original_name} | Path: {file_path} | Session: {session_id}"
        )
        return file_hash
    
    def stop_monitoring(self):
        """Stop the file monitoring system"""
        self.running = False
        self.observer.stop()
        self.observer.join()
        
        # Stop browser monitoring if it's running
        if self.browser_observer:
            try:
                self.browser_observer.stop()
                self.browser_observer.join()
                self.logger.info("🛑 Browser upload monitoring stopped")
            except Exception as e:
                self.logger.error(f"❌ Error stopping browser monitoring: {e}")
        
        self.logger.info("🛑 File monitoring system stopped")
    
    def get_security_report(self, hours=24):
        """Get security incidents from the last N hours"""
        with sqlite3.connect(self.tracking_db.db_path) as conn:
            cursor = conn.cursor()
            
            since_time = datetime.now() - timedelta(hours=hours)
            cursor.execute('''
                SELECT operation_type, source_path, destination_path, 
                       timestamp, detected_by, process_name, severity
                FROM file_operations 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (since_time,))
            
            operations = cursor.fetchall()
            
            cursor.execute('''
                SELECT COUNT(*) as total_incidents,
                       COUNT(CASE WHEN severity = 'HIGH' THEN 1 END) as high_severity,
                       COUNT(CASE WHEN severity = 'MEDIUM' THEN 1 END) as medium_severity
                FROM file_operations 
                WHERE timestamp > ?
            ''', (since_time,))
            
            summary = cursor.fetchone()
            
            return {
                'summary': {
                    'total_incidents': summary[0],
                    'high_severity': summary[1],
                    'medium_severity': summary[2]
                },
                'incidents': [
                    {
                        'operation': op[0],
                        'source': op[1],
                        'destination': op[2],
                        'timestamp': op[3],
                        'detected_by': op[4],
                        'process': op[5],
                        'severity': op[6]
                    }
                    for op in operations
                ]
            }

# Global monitor instance
file_monitor = None

def start_file_monitoring():
    """Start the global file monitoring system"""
    global file_monitor
    if file_monitor is None:
        file_monitor = SystemFileMonitor()
        file_monitor.start_monitoring()
    return file_monitor

def stop_file_monitoring():
    """Stop the global file monitoring system"""
    global file_monitor
    if file_monitor:
        file_monitor.stop_monitoring()
        file_monitor = None

if __name__ == "__main__":
    # Run the monitor as a standalone service
    monitor = SystemFileMonitor()
    try:
        monitor.start_monitoring()
        print("🔍 System File Monitor is running...")
        print("Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping file monitor...")
        monitor.stop_monitoring()
        print("✅ Monitor stopped")
