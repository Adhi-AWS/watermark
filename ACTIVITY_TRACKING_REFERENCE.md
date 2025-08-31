# Secure Excel Viewer - Activity Tracking Events Reference

## 📊 Complete Event Catalog

This document provides a comprehensive reference of all activity tracking events captured by the Secure Excel Viewer system.

## 🎯 Event Categories

### 1. File Operations
Events related to file access and lifecycle management.

### 2. User Interactions
Events capturing user behavior and engagement patterns.

### 3. Security Events
Events related to security violations and protection mechanisms.

### 4. System Events
Events related to system state and technical operations.

### 5. Print Operations
Events specifically related to printing functionality.

---

## 📁 File Operations Events

### HOMEPAGE_LOADED
**Description**: User accessed the main file listing page
**Trigger**: When user visits the root URL (`/`)
**Data Captured**:
```json
{
  "activity": "HOMEPAGE_LOADED",
  "file_name": "index",
  "additional_info": {
    "files_available": 3,
    "screen_resolution": "1920x1080",
    "browser": "Mozilla/5.0..."
  }
}
```

### FILE_SELECTED
**Description**: User clicked on a file to view it
**Trigger**: Click on file card in main interface
**Data Captured**:
```json
{
  "activity": "FILE_SELECTED",
  "file_name": "employee_data.xlsx",
  "additional_info": {
    "timestamp": "2025-08-29T10:30:45.123Z"
  }
}
```

### FILE_OPENED
**Description**: File successfully loaded in viewer
**Trigger**: Successful Excel file processing and display
**Data Captured**:
```json
{
  "activity": "FILE_OPENED",
  "file_name": "financial_report.xlsx",
  "additional_info": {
    "sheets_count": 3,
    "sheet_names": ["Summary", "Details", "Charts"]
  }
}
```

### FILE_VIEWED
**Description**: File content displayed to user
**Trigger**: When viewer page renders successfully
**Data Captured**:
```json
{
  "activity": "FILE_VIEWED",
  "file_name": "project_status.xlsx",
  "additional_info": {
    "screen_resolution": "1920x1080",
    "browser": "Chrome/91.0.4472.124",
    "sheets_count": 2
  }
}
```

### FILE_CLOSED
**Description**: User closed the file viewer
**Trigger**: Window/tab close or navigation away
**Data Captured**:
```json
{
  "activity": "FILE_CLOSED",
  "file_name": "confidential_data.xlsx",
  "additional_info": {
    "total_time_spent": 480,
    "total_clicks": 15,
    "total_scrolls": 8
  }
}
```

### FILE_NOT_FOUND
**Description**: Attempted to access non-existent file
**Trigger**: Request for file that doesn't exist
**Data Captured**:
```json
{
  "activity": "FILE_NOT_FOUND",
  "file_name": "missing_file.xlsx",
  "additional_info": {
    "error": "File does not exist"
  }
}
```

### FILE_ERROR
**Description**: Error occurred while processing file
**Trigger**: Exception during Excel file reading/conversion
**Data Captured**:
```json
{
  "activity": "FILE_ERROR",
  "file_name": "corrupted_file.xlsx",
  "additional_info": {
    "error": "Excel file is corrupted or invalid format"
  }
}
```

---

## 👤 User Interactions Events

### CLICK_EVENT
**Description**: User clicked on content within the viewer
**Trigger**: Mouse click on any element in the viewer
**Data Captured**:
```json
{
  "activity": "CLICK_EVENT",
  "file_name": "data_sheet.xlsx",
  "additional_info": {
    "click_count": 5,
    "element": "TD",
    "x": 450,
    "y": 320
  }
}
```

### SCROLL_ACTIVITY
**Description**: User scrolled through the document
**Trigger**: Scroll events (debounced to every 2 seconds)
**Data Captured**:
```json
{
  "activity": "SCROLL_ACTIVITY",
  "file_name": "large_dataset.xlsx",
  "additional_info": {
    "scroll_count": 12,
    "scroll_position": 1200
  }
}
```

### SHEET_SWITCHED
**Description**: User switched between Excel sheets
**Trigger**: Click on sheet tab navigation
**Data Captured**:
```json
{
  "activity": "SHEET_SWITCHED",
  "file_name": "multi_sheet_report.xlsx",
  "additional_info": {
    "sheet_name": "Q4 Results"
  }
}
```

### TIME_TRACKING
**Description**: Periodic time spent tracking
**Trigger**: Every 30 seconds while file is open
**Data Captured**:
```json
{
  "activity": "TIME_TRACKING",
  "file_name": "annual_report.xlsx",
  "additional_info": {
    "seconds_spent": 180
  }
}
```

### WINDOW_FOCUSED
**Description**: Browser window gained focus
**Trigger**: User returned to the viewer window
**Data Captured**:
```json
{
  "activity": "WINDOW_FOCUSED",
  "file_name": "current_file.xlsx",
  "additional_info": {
    "timestamp": "2025-08-29T10:35:15.456Z"
  }
}
```

### WINDOW_BLURRED
**Description**: Browser window lost focus
**Trigger**: User switched to another application/window
**Data Captured**:
```json
{
  "activity": "WINDOW_BLURRED",
  "file_name": "current_file.xlsx",
  "additional_info": {
    "timestamp": "2025-08-29T10:35:10.123Z"
  }
}
```

### PAGE_HIDDEN
**Description**: Page/tab became hidden
**Trigger**: Browser tab switched or minimized
**Data Captured**:
```json
{
  "activity": "PAGE_HIDDEN",
  "file_name": "active_file.xlsx",
  "additional_info": {
    "timestamp": "2025-08-29T10:40:00.789Z"
  }
}
```

### PAGE_VISIBLE
**Description**: Page/tab became visible again
**Trigger**: User returned to the viewer tab
**Data Captured**:
```json
{
  "activity": "PAGE_VISIBLE",
  "file_name": "active_file.xlsx",
  "additional_info": {
    "timestamp": "2025-08-29T10:40:30.456Z"
  }
}
```

---

## 🔒 Security Events

### BLOCKED_SHORTCUT
**Description**: Keyboard shortcut was blocked
**Trigger**: User attempted restricted keyboard combination
**Data Captured**:
```json
{
  "activity": "BLOCKED_SHORTCUT",
  "file_name": "secure_document.xlsx",
  "additional_info": {
    "key": "c",
    "ctrlKey": true,
    "shiftKey": false,
    "timestamp": "2025-08-29T10:45:12.345Z"
  }
}
```

### RIGHT_CLICK_ATTEMPT
**Description**: Right-click context menu was blocked
**Trigger**: User attempted to right-click
**Data Captured**:
```json
{
  "activity": "RIGHT_CLICK_ATTEMPT",
  "file_name": "protected_file.xlsx",
  "additional_info": {
    "x": 300,
    "y": 250,
    "element": "TABLE"
  }
}
```

### DRAG_ATTEMPT
**Description**: Drag operation was blocked
**Trigger**: User attempted to drag content
**Data Captured**:
```json
{
  "activity": "DRAG_ATTEMPT",
  "file_name": "confidential.xlsx",
  "additional_info": {
    "element": "IMG",
    "timestamp": "2025-08-29T10:50:20.789Z"
  }
}
```

### DEVTOOLS_OPENED
**Description**: Developer tools were detected as opened
**Trigger**: Browser developer tools access detected
**Data Captured**:
```json
{
  "activity": "DEVTOOLS_OPENED",
  "file_name": "sensitive_data.xlsx",
  "additional_info": {
    "detection_method": "screen_size_change",
    "timestamp": "2025-08-29T10:55:45.123Z"
  }
}
```

### DEVTOOLS_CLOSED
**Description**: Developer tools were detected as closed
**Trigger**: Developer tools closed detection
**Data Captured**:
```json
{
  "activity": "DEVTOOLS_CLOSED",
  "file_name": "sensitive_data.xlsx",
  "additional_info": {
    "detection_method": "screen_size_change",
    "timestamp": "2025-08-29T10:56:00.456Z"
  }
}
```

### CONSOLE_ACCESSED
**Description**: Browser console was accessed
**Trigger**: Console object property access
**Data Captured**:
```json
{
  "activity": "CONSOLE_ACCESSED",
  "file_name": "protected_document.xlsx",
  "additional_info": {
    "timestamp": "2025-08-29T11:00:15.789Z"
  }
}
```

---

## 🖨️ Print Operations Events

### PRINT_INITIATED
**Description**: User clicked the print button
**Trigger**: Print button click in viewer
**Data Captured**:
```json
{
  "activity": "PRINT_INITIATED",
  "file_name": "report_to_print.xlsx",
  "additional_info": {
    "timestamp": "2025-08-29T11:05:30.123Z"
  }
}
```

### PRINT_DIALOG_OPENED
**Description**: Print dialog was displayed
**Trigger**: Browser print dialog shown
**Data Captured**:
```json
{
  "activity": "PRINT_DIALOG_OPENED",
  "file_name": "document_for_print.xlsx",
  "additional_info": {
    "timestamp": "2025-08-29T11:05:35.456Z"
  }
}
```

### PRINT_COMPLETED
**Description**: Print operation was completed
**Trigger**: Print dialog closed with print
**Data Captured**:
```json
{
  "activity": "PRINT_COMPLETED",
  "file_name": "printed_document.xlsx",
  "additional_info": {
    "timestamp": "2025-08-29T11:06:00.789Z",
    "print_time": "8/29/2025, 11:06:00 AM"
  }
}
```

### PRINT_ERROR
**Description**: Error occurred during print operation
**Trigger**: Print process failure
**Data Captured**:
```json
{
  "activity": "PRINT_ERROR",
  "file_name": "failed_print.xlsx",
  "additional_info": {
    "error": "Print dialog cancelled by user",
    "timestamp": "2025-08-29T11:07:15.123Z"
  }
}
```

---

## 🔧 Event Data Structure

### Standard Event Format
All events follow this consistent structure:

```json
{
  "timestamp": "ISO-8601 formatted timestamp",
  "session_id": "UUID v4 session identifier",
  "activity": "EVENT_TYPE_NAME",
  "file_name": "filename.xlsx or 'index'",
  "ip_address": "User's IP address",
  "user_agent": "Browser user agent string",
  "additional_info": {
    "event_specific_data": "varies by event type"
  }
}
```

### Common Additional Info Fields

#### User Environment
- `screen_resolution`: "1920x1080"
- `browser`: "Chrome/91.0.4472.124"
- `timestamp`: "2025-08-29T10:30:45.123Z"

#### File Information
- `sheets_count`: 3
- `sheet_names`: ["Sheet1", "Summary", "Data"]
- `file_size`: 1024000

#### Interaction Data
- `x`, `y`: Mouse coordinates
- `element`: HTML element tag name
- `click_count`, `scroll_count`: Interaction counters

#### Time Tracking
- `seconds_spent`: Time in seconds
- `total_time_spent`: Total session time
- `duration`: Event duration

#### Security Context
- `key`: Keyboard key pressed
- `ctrlKey`, `shiftKey`, `altKey`: Modifier keys
- `detection_method`: How security event was detected

---

## 📈 Event Analytics

### Key Performance Indicators (KPIs)

#### Engagement Metrics
- **Average Session Duration**: Mean time spent per file
- **Interaction Rate**: Clicks and scrolls per minute
- **Sheet Navigation**: Multi-sheet engagement patterns
- **Return Rate**: Users accessing same file multiple times

#### Security Metrics
- **Violation Attempts**: Count of blocked actions per session
- **Risk Score**: Weighted score based on security events
- **Bypass Attempts**: Advanced security violation patterns
- **Compliance Rate**: Sessions without security violations

#### Operational Metrics
- **File Access Frequency**: Most and least accessed files
- **Peak Usage Times**: Time-based access patterns
- **Error Rate**: File access errors and failures
- **Print Volume**: Document printing frequency

### Sample Analytics Queries

#### Most Accessed Files
```sql
SELECT file_name, COUNT(*) as access_count
FROM activity_logs 
WHERE activity = 'FILE_OPENED'
GROUP BY file_name
ORDER BY access_count DESC;
```

#### Security Violations by Session
```sql
SELECT session_id, COUNT(*) as violation_count
FROM activity_logs 
WHERE activity LIKE '%BLOCKED%' OR activity LIKE '%ATTEMPT%'
GROUP BY session_id
ORDER BY violation_count DESC;
```

#### Average Session Duration
```sql
SELECT file_name, AVG(
  EXTRACT(EPOCH FROM 
    (SELECT timestamp FROM activity_logs al2 
     WHERE al2.session_id = al1.session_id 
     AND al2.activity = 'FILE_CLOSED' 
     LIMIT 1) -
    (SELECT timestamp FROM activity_logs al3 
     WHERE al3.session_id = al1.session_id 
     AND al3.activity = 'FILE_OPENED' 
     LIMIT 1)
  )
) as avg_duration_seconds
FROM activity_logs al1
WHERE activity = 'FILE_OPENED'
GROUP BY file_name;
```

---

## 🔍 Event Monitoring Best Practices

### Real-time Monitoring
1. **Set up alerts** for high-frequency security events
2. **Monitor session patterns** for unusual behavior
3. **Track file access trends** for capacity planning
4. **Watch for error spikes** indicating system issues

### Historical Analysis
1. **Weekly usage reports** showing file access patterns
2. **Monthly security summaries** highlighting violations
3. **Quarterly trend analysis** for business insights
4. **Annual compliance reports** for audit purposes

### Anomaly Detection
1. **Unusual access times** (outside business hours)
2. **High-frequency violations** from single sessions
3. **Rapid file switching** indicating automated access
4. **Geographic anomalies** (unexpected IP locations)

This comprehensive event reference enables administrators to fully understand and leverage the tracking capabilities of the Secure Excel Viewer system.
