# File System Monitoring & Security Tracking System

## Overview

This comprehensive security monitoring system tracks **file copying, deleting, and alteration attempts** from the destination side (client-side) for downloaded Excel files. The system provides real-time monitoring and historical audit capabilities to detect unauthorized file manipulation.

## 🛡️ Security Features Implemented

### 1. **Client-Side Monitoring (JavaScript)**
- **File Operations**: Tracks drag/drop, copy/cut operations
- **Clipboard Monitoring**: Detects copy, cut, and paste attempts
- **Keyboard Surveillance**: Monitors suspicious key combinations (Ctrl+C, Ctrl+X, Ctrl+V, Ctrl+S, PrintScreen, F12)
- **Window Focus Tracking**: Detects when users switch applications (potential copying behavior)
- **Developer Tools Detection**: Identifies when browser dev tools are opened
- **Text Selection Monitoring**: Tracks large text selections that may indicate copying intent
- **Context Menu Blocking**: Prevents right-click operations with security warnings
- **Screenshot Prevention**: Detects PrintScreen attempts and logs them

### 2. **Server-Side Event Processing**
- **Real-time Event Logging**: All client events are immediately sent to server
- **Threat Level Analysis**: Automatic classification of events as HIGH/MEDIUM/LOW threat
- **Database Storage**: Persistent storage in SQLite for historical analysis
- **IP and Session Tracking**: Links events to specific users and sessions

### 3. **Enhanced Excel Protection**
- **Worksheet Protection**: Maximum Excel protection settings applied
- **VBA Macro Monitoring**: (Framework ready for macro-based monitoring)
- **File Format Security**: Uses standard .xlsx format for maximum compatibility
- **Download Tracking**: Every download is logged with user details

## 📊 Monitoring Dashboard Features

### Security Monitor Dashboard (`/security/monitor`)
- **Real-time Event Timeline**: Live display of security events as they occur
- **Threat Level Statistics**: Visual counters for HIGH/MEDIUM/LOW threats
- **Advanced Filtering**: Filter by file name, threat level, date range
- **Auto-refresh**: Automatic updates every 30 seconds
- **Export Capabilities**: CSV export of security events
- **Event Details**: Detailed view of each security incident

### Admin Audit Dashboard (`/admin/audit`)
- **Historical Analysis**: Long-term trends and patterns
- **File-specific Tracking**: Activity logs per Excel file
- **Session Management**: Track user sessions and behavior patterns
- **Statistical Reports**: Comprehensive usage and security statistics

## 🔍 Event Types Tracked

### HIGH Threat Events
- `CLIPBOARD_COPY_ATTEMPT` - User attempted to copy content
- `CLIPBOARD_CUT_ATTEMPT` - User attempted to cut content
- `SUSPICIOUS_KEYPRESS` - Dangerous key combinations detected
- `FILE_DRAG_ATTEMPT` - User dragged files (potential copying)
- `PRINT_ATTEMPT` - User attempted to print the document
- `SAVE_ATTEMPT` - User attempted to save the file

### MEDIUM Threat Events
- `WINDOW_FOCUS_LOST` - User switched to another application
- `VISIBILITY_CHANGE` - Page became hidden (potential screen capture)
- `FILE_DROP_DETECTED` - Files were dropped onto the page
- `DEVELOPER_TOOLS_DETECTED` - Browser developer tools opened

### LOW Threat Events
- `MONITORING_HEARTBEAT` - Regular system health check
- `TEXT_SELECTION_STARTED` - User selected text
- `PAGE_UNLOAD_ATTEMPT` - User attempted to leave the page
- `FILE_MONITORING_INITIALIZED` - Monitoring system started

## 🚨 Security Alerts & Prevention

### Real-time Warnings
- **Security Alerts**: Pop-up warnings for blocked actions
- **Context Menu Blocking**: Right-click disabled with security notice
- **Action Prevention**: Critical operations (copy/paste) can be blocked
- **Console Warnings**: Bold security warnings in browser console

### Audit Trail
- **Complete Event Log**: Every action is recorded with timestamp, IP, and session
- **User Identification**: Tracks session IDs and user agents
- **File Tracking**: Links all events to specific downloaded files
- **Historical Analysis**: Long-term pattern detection for repeat offenders

## 📈 Usage Analytics

### Real-time Statistics
```
High Threats: 15    Medium Threats: 8    Low Threats: 45    Total Events: 68
```

### File Access Patterns
- Most accessed files
- Peak usage times
- User behavior patterns
- Security incident frequency

## 🔧 Technical Implementation

### File Structure
```
/file_monitoring.py          # Client-side monitoring script generator
/templates/security_monitor.html  # Security dashboard interface
/activity_database.py        # Database backend for event storage
/app.py                     # Flask routes for monitoring APIs
/templates/viewer.html      # Enhanced viewer with monitoring
```

### API Endpoints
- `POST /api/file-monitoring` - Receive client security events
- `GET /api/security-events` - Retrieve security events with filtering
- `GET /monitoring-script/<file_id>` - Generate monitoring script for specific file
- `GET /security/monitor` - Security monitoring dashboard

### Database Schema
```sql
activities (
    id, timestamp, session_id, activity, file_name, 
    ip_address, user_agent, additional_info, 
    created_date, created_time
)
```

## 🎯 Threat Detection Examples

### Example 1: Copy Attempt Detection
```json
{
  "eventType": "CLIPBOARD_COPY_ATTEMPT",
  "threatLevel": "HIGH",
  "eventData": {
    "hasSelection": true,
    "selectionLength": 156,
    "timestamp": "2025-08-29T18:25:36Z"
  }
}
```

### Example 2: Application Switching
```json
{
  "eventType": "WINDOW_FOCUS_LOST",
  "threatLevel": "MEDIUM",
  "eventData": {
    "timeInFocus": 30000,
    "timestamp": "2025-08-29T18:26:15Z"
  }
}
```

### Example 3: Screenshot Attempt
```json
{
  "eventType": "SUSPICIOUS_KEYPRESS",
  "threatLevel": "HIGH",
  "eventData": {
    "key": "PrintScreen",
    "blocked": true,
    "timestamp": "2025-08-29T18:27:02Z"
  }
}
```

## 🔒 Security Considerations

### Client-Side Limitations
- **JavaScript Dependence**: Can be disabled by determined users
- **Browser Restrictions**: Some file system operations are limited by browser security
- **Network Dependence**: Requires connection to send events to server

### Mitigation Strategies
- **Fallback Monitoring**: Multiple detection methods for critical events
- **Server-side Validation**: All events are validated and analyzed server-side
- **Behavior Pattern Analysis**: Long-term tracking identifies suspicious patterns
- **Excel Protection**: Native Excel protection as additional security layer

## 🚀 Advanced Features

### Future Enhancements
1. **Machine Learning**: Pattern recognition for advanced threat detection
2. **Real-time Alerts**: Email/SMS notifications for high-threat events
3. **Geographic Tracking**: IP-based location monitoring
4. **Device Fingerprinting**: Unique device identification
5. **File Watermarking**: Embedded tracking in downloaded files

### Integration Options
- **Enterprise SSO**: Integration with corporate authentication
- **SIEM Integration**: Export events to enterprise security systems
- **Compliance Reporting**: Automated compliance and audit reports

## 📋 Getting Started

### 1. Start the Application
```bash
python app.py
```

### 2. Access Dashboards
- **Main Application**: http://localhost:5000
- **Security Monitor**: http://localhost:5000/security/monitor
- **Admin Audit**: http://localhost:5000/admin/audit

### 3. Test the System
```bash
python test_monitoring.py
```

### 4. Monitor Events
- Open any Excel file in the viewer
- Perform actions (copy, right-click, switch windows)
- Watch real-time events in the Security Monitor dashboard

## 📞 Support & Maintenance

### Logs Location
- **Database**: `activity_audit.db`
- **Application Logs**: Console output during Flask execution
- **Error Logs**: Browser console for client-side issues

### Performance Monitoring
- **Database Size**: Monitor SQLite database growth
- **Event Volume**: Track events per minute/hour
- **Response Times**: Monitor API endpoint performance

---

**🛡️ This system provides comprehensive protection against unauthorized file copying, deletion, and alteration attempts while maintaining detailed audit trails for security compliance.**
