"""
File System Monitoring for Downloaded Secure Files
This module provides client-side monitoring capabilities for downloaded files
"""

def generate_monitoring_script(file_id, server_url):
    """Generate JavaScript code for file system monitoring"""
    
    monitoring_script = f"""
// File System Monitoring Script for Secure File: {file_id}
// This script monitors attempts to copy, delete, or alter the downloaded file

class SecureFileMonitor {{
    constructor(fileId, serverUrl) {{
        this.fileId = fileId;
        this.serverUrl = serverUrl;
        this.sessionId = this.generateSessionId();
        this.monitoringActive = true;
        this.lastActivity = Date.now();
        
        this.init();
    }}
    
    generateSessionId() {{
        return 'monitor_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }}
    
    init() {{
        // Monitor various file system events
        this.setupFileSystemMonitoring();
        this.setupClipboardMonitoring();
        this.setupKeyboardMonitoring();
        this.setupWindowMonitoring();
        this.setupPeriodicChecks();
        
        // Send initial monitoring start event
        this.logEvent('MONITORING_STARTED', {{
            fileId: this.fileId,
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            timestamp: new Date().toISOString()
        }});
    }}
    
    setupFileSystemMonitoring() {{
        // Monitor file drag events (potential copying)
        document.addEventListener('dragstart', (e) => {{
            this.logEvent('FILE_DRAG_ATTEMPT', {{
                fileType: e.dataTransfer.files.length > 0 ? 'file_drag' : 'element_drag',
                timestamp: new Date().toISOString()
            }});
        }});
        
        // Monitor file drop events
        document.addEventListener('drop', (e) => {{
            if (e.dataTransfer.files.length > 0) {{
                this.logEvent('FILE_DROP_DETECTED', {{
                    fileCount: e.dataTransfer.files.length,
                    timestamp: new Date().toISOString()
                }});
            }}
        }});
        
        // Monitor file input changes (potential file operations)
        document.addEventListener('change', (e) => {{
            if (e.target.type === 'file') {{
                this.logEvent('FILE_INPUT_CHANGE', {{
                    hasFiles: e.target.files.length > 0,
                    timestamp: new Date().toISOString()
                }});
            }}
        }});
    }}
    
    setupClipboardMonitoring() {{
        // Monitor clipboard operations
        document.addEventListener('copy', (e) => {{
            this.logEvent('CLIPBOARD_COPY_ATTEMPT', {{
                hasSelection: window.getSelection().toString().length > 0,
                timestamp: new Date().toISOString()
            }});
        }});
        
        document.addEventListener('cut', (e) => {{
            this.logEvent('CLIPBOARD_CUT_ATTEMPT', {{
                hasSelection: window.getSelection().toString().length > 0,
                timestamp: new Date().toISOString()
            }});
        }});
        
        document.addEventListener('paste', (e) => {{
            this.logEvent('CLIPBOARD_PASTE_ATTEMPT', {{
                timestamp: new Date().toISOString()
            }});
        }});
    }}
    
    setupKeyboardMonitoring() {{
        // Monitor suspicious keyboard combinations
        document.addEventListener('keydown', (e) => {{
            const suspiciousKeys = [
                {{ ctrl: true, key: 'c' }}, // Copy
                {{ ctrl: true, key: 'x' }}, // Cut
                {{ ctrl: true, key: 'v' }}, // Paste
                {{ ctrl: true, key: 's' }}, // Save
                {{ ctrl: true, key: 'a' }}, // Select All
                {{ key: 'F12' }}, // Developer Tools
                {{ ctrl: true, shift: true, key: 'I' }}, // Developer Tools
                {{ ctrl: true, shift: true, key: 'C' }}, // Developer Tools
                {{ ctrl: true, shift: true, key: 'J' }}, // Console
                {{ key: 'PrintScreen' }}, // Screenshot
                {{ alt: true, key: 'PrintScreen' }} // Alt + Screenshot
            ];
            
            const currentKey = {{
                ctrl: e.ctrlKey,
                shift: e.shiftKey,
                alt: e.altKey,
                key: e.key
            }};
            
            const isSuspicious = suspiciousKeys.some(suspicious => {{
                return Object.keys(suspicious).every(prop => {{
                    if (prop === 'key') {{
                        return suspicious[prop].toLowerCase() === currentKey[prop].toLowerCase();
                    }}
                    return suspicious[prop] === currentKey[prop];
                }});
            }});
            
            if (isSuspicious) {{
                this.logEvent('SUSPICIOUS_KEYPRESS', {{
                    key: e.key,
                    ctrlKey: e.ctrlKey,
                    shiftKey: e.shiftKey,
                    altKey: e.altKey,
                    timestamp: new Date().toISOString()
                }});
                
                // Optionally prevent the action (for security)
                if (this.shouldBlockAction(e)) {{
                    e.preventDefault();
                    this.showSecurityWarning('This action is blocked for security reasons.');
                }}
            }}
        }});
    }}
    
    setupWindowMonitoring() {{
        // Monitor window focus/blur (potential app switching for copying)
        window.addEventListener('blur', () => {{
            this.logEvent('WINDOW_FOCUS_LOST', {{
                timestamp: new Date().toISOString(),
                timeInFocus: Date.now() - this.lastActivity
            }});
        }});
        
        window.addEventListener('focus', () => {{
            this.logEvent('WINDOW_FOCUS_GAINED', {{
                timestamp: new Date().toISOString()
            }});
            this.lastActivity = Date.now();
        }});
        
        // Monitor page visibility changes
        document.addEventListener('visibilitychange', () => {{
            this.logEvent('VISIBILITY_CHANGE', {{
                hidden: document.hidden,
                timestamp: new Date().toISOString()
            }});
        }});
        
        // Monitor before unload (potential file operations)
        window.addEventListener('beforeunload', (e) => {{
            this.logEvent('PAGE_UNLOAD_ATTEMPT', {{
                timestamp: new Date().toISOString()
            }});
        }});
    }}
    
    setupPeriodicChecks() {{
        // Check for suspicious activities every 30 seconds
        setInterval(() => {{
            this.performSecurityCheck();
        }}, 30000);
        
        // Heartbeat to server every 60 seconds
        setInterval(() => {{
            this.sendHeartbeat();
        }}, 60000);
    }}
    
    performSecurityCheck() {{
        const checks = {{
            developerToolsOpen: this.checkDeveloperTools(),
            suspiciousExtensions: this.checkBrowserExtensions(),
            memoryUsage: this.getMemoryInfo(),
            networkRequests: this.checkNetworkActivity()
        }};
        
        this.logEvent('SECURITY_CHECK', {{
            checks: checks,
            timestamp: new Date().toISOString()
        }});
    }}
    
    checkDeveloperTools() {{
        const threshold = 160;
        return (window.outerHeight - window.innerHeight > threshold) || 
               (window.outerWidth - window.innerWidth > threshold);
    }}
    
    checkBrowserExtensions() {{
        // Check for common extensions that might interfere
        return {{
            extensionsDetected: navigator.plugins.length,
            userAgent: navigator.userAgent
        }};
    }}
    
    getMemoryInfo() {{
        if (performance.memory) {{
            return {{
                usedJSHeapSize: performance.memory.usedJSHeapSize,
                totalJSHeapSize: performance.memory.totalJSHeapSize,
                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
            }};
        }}
        return null;
    }}
    
    checkNetworkActivity() {{
        // Monitor for unusual network requests
        return {{
            navigationEntries: performance.getEntriesByType('navigation').length,
            resourceEntries: performance.getEntriesByType('resource').length
        }};
    }}
    
    shouldBlockAction(event) {{
        // Define which actions should be blocked
        const blockableActions = [
            {{ ctrl: true, key: 'c' }}, // Block copying
            {{ ctrl: true, key: 'x' }}, // Block cutting
            {{ ctrl: true, key: 's' }}, // Block saving
            {{ key: 'F12' }}, // Block developer tools
            {{ key: 'PrintScreen' }} // Block screenshots
        ];
        
        return blockableActions.some(action => {{
            return Object.keys(action).every(prop => {{
                if (prop === 'key') {{
                    return action[prop].toLowerCase() === event.key.toLowerCase();
                }}
                return action[prop] === event[prop];
            }});
        }});
    }}
    
    showSecurityWarning(message) {{
        // Show security warning to user
        if (!document.getElementById('securityWarning')) {{
            const warning = document.createElement('div');
            warning.id = 'securityWarning';
            warning.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #ff4444;
                color: white;
                padding: 15px;
                border-radius: 5px;
                z-index: 10000;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                max-width: 300px;
            `;
            warning.innerHTML = `
                <strong>🛡️ Security Alert</strong><br>
                ${{message}}
            `;
            document.body.appendChild(warning);
            
            setTimeout(() => {{
                if (document.getElementById('securityWarning')) {{
                    document.body.removeChild(warning);
                }}
            }}, 5000);
        }}
    }}
    
    sendHeartbeat() {{
        this.logEvent('MONITORING_HEARTBEAT', {{
            timestamp: new Date().toISOString(),
            sessionDuration: Date.now() - this.sessionStartTime || Date.now()
        }});
    }}
    
    logEvent(eventType, eventData) {{
        if (!this.monitoringActive) return;
        
        const logData = {{
            fileId: this.fileId,
            sessionId: this.sessionId,
            eventType: eventType,
            eventData: eventData,
            timestamp: new Date().toISOString(),
            url: window.location.href
        }};
        
        // Send to server
        this.sendToServer('/api/file-monitoring', logData);
        
        // Also log to console for debugging
        console.log('[SecureFileMonitor]', eventType, eventData);
    }}
    
    sendToServer(endpoint, data) {{
        fetch(this.serverUrl + endpoint, {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify(data)
        }}).catch(error => {{
            console.error('Failed to send monitoring data:', error);
        }});
    }}
    
    stopMonitoring() {{
        this.monitoringActive = false;
        this.logEvent('MONITORING_STOPPED', {{
            timestamp: new Date().toISOString()
        }});
    }}
}}

// Initialize monitoring when DOM is ready
document.addEventListener('DOMContentLoaded', function() {{
    window.secureFileMonitor = new SecureFileMonitor('{file_id}', '{server_url}');
}});

// Export for external use
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = SecureFileMonitor;
}}
"""
    
    return monitoring_script

def generate_file_protection_vba():
    """Generate VBA code for file protection (for actual Excel files)"""
    
    vba_code = """
Private Declare PtrSafe Function GetUserName Lib "advapi32.dll" Alias "GetUserNameA" (ByVal lpBuffer As String, nSize As Long) As Long
Private Declare PtrSafe Function GetComputerName Lib "kernel32" Alias "GetComputerNameA" (ByVal lpBuffer As String, nSize As Long) As Long

Private Sub Workbook_Open()
    ' Log file opening
    LogFileEvent "FILE_OPENED", GetUserInfo()
    
    ' Set up protection
    Call ProtectWorkbook
    
    ' Set up monitoring
    Call SetupFileMonitoring
    
    ' Show security notice
    Call ShowSecurityNotice
End Sub

Private Sub Workbook_BeforeClose(Cancel As Boolean)
    LogFileEvent "FILE_CLOSING", GetUserInfo()
End Sub

Private Sub Workbook_BeforeSave(ByVal SaveAsUI As Boolean, Cancel As Boolean)
    ' Log save attempts
    LogFileEvent "SAVE_ATTEMPT", "SaveAsUI: " & SaveAsUI
    
    ' Optionally block saves
    If SaveAsUI Then
        MsgBox "Save As is disabled for this secure document.", vbExclamation, "Security Policy"
        Cancel = True
        LogFileEvent "SAVE_BLOCKED", "Save As blocked"
    End If
End Sub

Private Sub Workbook_BeforePrint(Cancel As Boolean)
    ' Log print attempts
    LogFileEvent "PRINT_ATTEMPT", GetUserInfo()
    
    ' Optionally block printing
    MsgBox "Printing is monitored and logged for this secure document.", vbInformation, "Security Notice"
    LogFileEvent "PRINT_ALLOWED", "Print allowed with notice"
End Sub

Private Sub ProtectWorkbook()
    Dim ws As Worksheet
    
    ' Protect all worksheets
    For Each ws In ThisWorkbook.Worksheets
        ws.Protect Password:="SecureDoc2025", _
                   DrawingObjects:=True, _
                   Contents:=True, _
                   Scenarios:=True, _
                   UserInterfaceOnly:=False, _
                   AllowFormattingCells:=False, _
                   AllowFormattingColumns:=False, _
                   AllowFormattingRows:=False, _
                   AllowInsertingColumns:=False, _
                   AllowInsertingRows:=False, _
                   AllowInsertingHyperlinks:=False, _
                   AllowDeletingColumns:=False, _
                   AllowDeletingRows:=False, _
                   AllowSorting:=False, _
                   AllowFiltering:=False, _
                   AllowUsingPivotTables:=False
    Next ws
    
    ' Protect workbook structure
    ThisWorkbook.Protect Password:="SecureDoc2025", Structure:=True, Windows:=True
End Sub

Private Sub SetupFileMonitoring()
    ' Enable events for monitoring
    Application.EnableEvents = True
    
    ' Set up periodic monitoring
    Application.OnTime Now + TimeValue("00:01:00"), "MonitoringCheck"
End Sub

Private Sub MonitoringCheck()
    ' Periodic security check
    LogFileEvent "MONITORING_CHECK", GetSystemInfo()
    
    ' Schedule next check
    Application.OnTime Now + TimeValue("00:01:00"), "MonitoringCheck"
End Sub

Private Function GetUserInfo() As String
    Dim userName As String
    Dim computerName As String
    Dim buffer As String
    Dim size As Long
    
    ' Get username
    buffer = Space(255)
    size = Len(buffer)
    Call GetUserName(buffer, size)
    userName = Left(buffer, size - 1)
    
    ' Get computer name
    buffer = Space(255)
    size = Len(buffer)
    Call GetComputerName(buffer, size)
    computerName = Left(buffer, size - 1)
    
    GetUserInfo = "User: " & userName & ", Computer: " & computerName
End Function

Private Function GetSystemInfo() As String
    GetSystemInfo = "Excel: " & Application.Version & _
                   ", OS: " & Application.OperatingSystem & _
                   ", Time: " & Now()
End Function

Private Sub LogFileEvent(eventType As String, eventData As String)
    ' Log events to a hidden worksheet or external service
    Dim logEntry As String
    logEntry = Now() & " | " & eventType & " | " & eventData
    
    ' Try to log to server (if network available)
    On Error Resume Next
    Call SendToServer(eventType, eventData)
    On Error GoTo 0
    
    ' Local logging (in case server is unavailable)
    Call LogToHiddenSheet(logEntry)
End Sub

Private Sub SendToServer(eventType As String, eventData As String)
    ' This would require additional setup for HTTP requests in VBA
    ' For now, we'll log locally
End Sub

Private Sub LogToHiddenSheet(logEntry As String)
    Dim logSheet As Worksheet
    Dim lastRow As Long
    
    ' Create or get hidden log sheet
    On Error Resume Next
    Set logSheet = ThisWorkbook.Worksheets("SecurityLog")
    On Error GoTo 0
    
    If logSheet Is Nothing Then
        Set logSheet = ThisWorkbook.Worksheets.Add
        logSheet.Name = "SecurityLog"
        logSheet.Visible = xlSheetVeryHidden
        logSheet.Cells(1, 1).Value = "Security Event Log"
        logSheet.Cells(2, 1).Value = "Timestamp | Event Type | Event Data"
    End If
    
    ' Add log entry
    lastRow = logSheet.Cells(logSheet.Rows.Count, 1).End(xlUp).Row + 1
    logSheet.Cells(lastRow, 1).Value = logEntry
End Sub

Private Sub ShowSecurityNotice()
    MsgBox "🛡️ SECURE DOCUMENT NOTICE" & vbCrLf & vbCrLf & _
           "This document is protected and monitored." & vbCrLf & _
           "All activities are logged for security purposes." & vbCrLf & _
           "Unauthorized copying, printing, or modification " & _
           "may violate security policies." & vbCrLf & vbCrLf & _
           "By continuing to use this document, you agree " & _
           "to comply with all security requirements.", _
           vbInformation, "Security Policy Agreement"
End Sub
"""
    
    return vba_code
