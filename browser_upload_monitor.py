"""
🌐 BROWSER UPLOAD DETECTION SYSTEM
==================================

Advanced monitoring system to detect when protected files are being uploaded
through web browsers or cloud services.
"""

import os
import time
import sqlite3
import hashlib
import psutil
import requests
import threading
from datetime import datetime
from pathlib import Path
import win32gui
import win32process
import win32api
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BrowserUploadMonitor:
    def __init__(self, flask_api_url="http://127.0.0.1:5000"):
        self.flask_api_url = flask_api_url
        self.protected_files = {}
        self.browser_processes = {}
        self.upload_indicators = [
            'upload', 'file', 'attach', 'drag', 'drop', 'browse',
            'select', 'choose', 'gmail', 'drive', 'dropbox', 'onedrive'
        ]
        self.browser_names = [
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe',
            'opera.exe', 'brave.exe', 'vivaldi.exe', 'safari.exe'
        ]
        self.temp_directories = [
            os.path.expanduser("~/AppData/Local/Temp"),
            os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/Recent"),
            "C:/temp", "C:/tmp"
        ]
        
    def load_protected_files(self):
        """Load protected files from tracking database"""
        try:
            conn = sqlite3.connect('file_tracking.db')
            cursor = conn.cursor()
            cursor.execute('SELECT file_hash, file_path, file_name FROM protected_files')
            
            for row in cursor.fetchall():
                file_hash, file_path, file_name = row
                self.protected_files[file_hash] = {
                    'path': file_path,
                    'name': file_name,
                    'registered_time': datetime.now()
                }
            
            conn.close()
            print(f"🔍 Loaded {len(self.protected_files)} protected files for upload monitoring")
        except Exception as e:
            print(f"❌ Error loading protected files: {e}")

    def calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of a file"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            return None

    def is_browser_process(self, process_name):
        """Check if process is a web browser"""
        return any(browser in process_name.lower() for browser in self.browser_names)

    def get_browser_window_title(self, pid):
        """Get window title of browser process"""
        def enum_windows_callback(hwnd, titles):
            if win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid:
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        titles.append(title)
            return True
        
        titles = []
        try:
            win32gui.EnumWindows(enum_windows_callback, titles)
            return titles
        except:
            return []

    def detect_upload_context(self, window_titles):
        """Analyze window titles for upload indicators"""
        upload_score = 0
        detected_services = []
        
        for title in window_titles:
            title_lower = title.lower()
            for indicator in self.upload_indicators:
                if indicator in title_lower:
                    upload_score += 1
                    
            # Detect specific cloud services
            if any(service in title_lower for service in ['gmail', 'google drive']):
                detected_services.append('Google Services')
            elif any(service in title_lower for service in ['dropbox']):
                detected_services.append('Dropbox')
            elif any(service in title_lower for service in ['onedrive', 'outlook']):
                detected_services.append('Microsoft OneDrive/Outlook')
            elif any(service in title_lower for service in ['facebook', 'instagram']):
                detected_services.append('Social Media')
            elif any(service in title_lower for service in ['linkedin', 'twitter']):
                detected_services.append('Professional Networks')
                
        return upload_score, detected_services

    def monitor_browser_file_access(self):
        """Monitor browser processes for file access patterns"""
        while True:
            try:
                current_browsers = {}
                
                for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                    try:
                        if self.is_browser_process(proc.info['name']):
                            pid = proc.info['pid']
                            current_browsers[pid] = {
                                'name': proc.info['name'],
                                'open_files': proc.info['open_files'] or []
                            }
                            
                            # Check for protected file access
                            for file_info in proc.info['open_files']:
                                if file_info.path:
                                    file_hash = self.calculate_file_hash(file_info.path)
                                    if file_hash in self.protected_files:
                                        self.handle_browser_file_access(pid, file_info.path, proc.info['name'])
                                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                self.browser_processes = current_browsers
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"❌ Error in browser monitoring: {e}")
                time.sleep(5)

    def handle_browser_file_access(self, browser_pid, file_path, browser_name):
        """Handle detection of browser accessing protected file"""
        try:
            # Get browser window titles
            window_titles = self.get_browser_window_title(browser_pid)
            upload_score, detected_services = self.detect_upload_context(window_titles)
            
            # Calculate threat level
            if upload_score >= 2 or detected_services:
                threat_level = "HIGH"
            elif upload_score >= 1:
                threat_level = "MEDIUM"
            else:
                threat_level = "LOW"
            
            # Create security incident
            incident_data = {
                'incident_type': 'BROWSER_UPLOAD_ATTEMPT',
                'file_path': file_path,
                'browser_name': browser_name,
                'browser_pid': browser_pid,
                'window_titles': window_titles,
                'upload_score': upload_score,
                'detected_services': detected_services,
                'threat_level': threat_level,
                'timestamp': datetime.now().isoformat(),
                'severity': 'HIGH' if threat_level == "HIGH" else 'MEDIUM'
            }
            
            self.send_security_alert(incident_data)
            
        except Exception as e:
            print(f"❌ Error handling browser file access: {e}")

    def monitor_temp_file_uploads(self):
        """Monitor temporary directories for upload patterns"""
        class TempFileHandler(FileSystemEventHandler):
            def __init__(self, parent_monitor):
                self.parent = parent_monitor
                
            def on_created(self, event):
                if not event.is_directory:
                    self.check_temp_file_upload(event.src_path)
                    
            def on_modified(self, event):
                if not event.is_directory:
                    self.check_temp_file_upload(event.src_path)
                    
            def check_temp_file_upload(self, file_path):
                """Check if temp file is related to protected file upload"""
                try:
                    if os.path.exists(file_path):
                        file_hash = self.parent.calculate_file_hash(file_path)
                        if file_hash in self.parent.protected_files:
                            self.parent.handle_temp_upload_attempt(file_path, file_hash)
                except Exception as e:
                    pass
        
        observer = Observer()
        handler = TempFileHandler(self)
        
        for temp_dir in self.temp_directories:
            if os.path.exists(temp_dir):
                observer.schedule(handler, temp_dir, recursive=True)
                print(f"📁 Monitoring temp directory: {temp_dir}")
        
        observer.start()
        return observer

    def handle_temp_upload_attempt(self, temp_file_path, file_hash):
        """Handle detection of protected file in temp directory"""
        protected_file = self.protected_files[file_hash]
        
        incident_data = {
            'incident_type': 'TEMP_FILE_UPLOAD_STAGING',
            'original_file': protected_file['path'],
            'temp_file_path': temp_file_path,
            'file_hash': file_hash,
            'file_name': protected_file['name'],
            'timestamp': datetime.now().isoformat(),
            'severity': 'HIGH',
            'description': f"Protected file {protected_file['name']} detected in temporary upload staging area"
        }
        
        self.send_security_alert(incident_data)

    def monitor_clipboard_uploads(self):
        """Monitor clipboard for protected file data"""
        try:
            import win32clipboard
            
            last_clipboard_hash = None
            
            while True:
                try:
                    win32clipboard.OpenClipboard()
                    
                    # Check for file paths in clipboard
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
                        data = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                        if data:
                            for file_path in data:
                                if os.path.exists(file_path):
                                    file_hash = self.calculate_file_hash(file_path)
                                    if file_hash in self.protected_files:
                                        self.handle_clipboard_upload_attempt(file_path, file_hash)
                    
                    # Check for text content that might be file data
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                        text_data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                        if text_data and len(text_data) > 1000:  # Large text might be file content
                            current_hash = hashlib.md5(text_data.encode()).hexdigest()
                            if current_hash != last_clipboard_hash:
                                self.handle_clipboard_data_detection(text_data)
                                last_clipboard_hash = current_hash
                    
                    win32clipboard.CloseClipboard()
                    
                except Exception as e:
                    try:
                        win32clipboard.CloseClipboard()
                    except:
                        pass
                
                time.sleep(1)  # Check every second
                
        except ImportError:
            print("⚠️  Clipboard monitoring requires pywin32 package")
        except Exception as e:
            print(f"❌ Error in clipboard monitoring: {e}")

    def handle_clipboard_upload_attempt(self, file_path, file_hash):
        """Handle detection of protected file in clipboard"""
        protected_file = self.protected_files[file_hash]
        
        incident_data = {
            'incident_type': 'CLIPBOARD_UPLOAD_ATTEMPT',
            'file_path': file_path,
            'file_hash': file_hash,
            'file_name': protected_file['name'],
            'timestamp': datetime.now().isoformat(),
            'severity': 'HIGH',
            'description': f"Protected file {protected_file['name']} detected in clipboard - potential upload attempt"
        }
        
        self.send_security_alert(incident_data)

    def handle_clipboard_data_detection(self, clipboard_data):
        """Analyze clipboard data for protected content"""
        incident_data = {
            'incident_type': 'SUSPICIOUS_CLIPBOARD_DATA',
            'data_size': len(clipboard_data),
            'data_preview': clipboard_data[:100] + "..." if len(clipboard_data) > 100 else clipboard_data,
            'timestamp': datetime.now().isoformat(),
            'severity': 'MEDIUM',
            'description': "Large data block detected in clipboard - potential file content copy"
        }
        
        self.send_security_alert(incident_data)

    def send_security_alert(self, incident_data):
        """Send security alert to Flask API"""
        try:
            response = requests.post(
                f"{self.flask_api_url}/api/file-security-incident",
                json=incident_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"🚨 BROWSER UPLOAD ALERT: {incident_data['incident_type']}")
                print(f"   📁 File: {incident_data.get('file_name', 'Unknown')}")
                print(f"   ⚠️  Severity: {incident_data['severity']}")
                if 'detected_services' in incident_data:
                    print(f"   🌐 Services: {', '.join(incident_data['detected_services'])}")
            else:
                print(f"❌ Failed to send alert: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error sending security alert: {e}")

    def start_monitoring(self):
        """Start all monitoring threads"""
        print("🚀 Starting Browser Upload Monitor...")
        
        # Load protected files
        self.load_protected_files()
        
        # Start browser process monitoring
        browser_thread = threading.Thread(target=self.monitor_browser_file_access, daemon=True)
        browser_thread.start()
        print("✅ Browser process monitoring started")
        
        # Start temp file monitoring
        temp_observer = self.monitor_temp_file_uploads()
        print("✅ Temporary file monitoring started")
        
        # Start clipboard monitoring
        clipboard_thread = threading.Thread(target=self.monitor_clipboard_uploads, daemon=True)
        clipboard_thread.start()
        print("✅ Clipboard monitoring started")
        
        print("🛡️  Browser upload monitoring is now active!")
        print("   👀 Watching for upload attempts to:")
        print("      • Gmail & Google Drive")
        print("      • Dropbox & OneDrive") 
        print("      • Social Media platforms")
        print("      • File sharing services")
        print("      • Any web-based upload interface")
        
        return temp_observer

def main():
    """Main function to run browser upload monitor"""
    monitor = BrowserUploadMonitor()
    
    try:
        temp_observer = monitor.start_monitoring()
        
        # Keep monitoring running
        while True:
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping browser upload monitor...")
        if 'temp_observer' in locals():
            temp_observer.stop()
            temp_observer.join()
        print("✅ Browser upload monitor stopped")

if __name__ == "__main__":
    main()
