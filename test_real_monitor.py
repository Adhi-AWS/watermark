#!/usr/bin/env python3
"""
Real-world File Monitor Test
Test with actual protected files in Downloads folder
"""

import os
import time
import shutil
from system_file_monitor import SystemFileMonitor
from datetime import datetime

def test_real_protected_file():
    """Test with actual protected files"""
    print("🧪 Testing with real protected files...")
    
    # Use the existing protected file in Downloads
    downloads_dir = os.path.expanduser("~/Downloads")
    protected_file = os.path.join(downloads_dir, "secure_employee_data.xlsx")
    
    if not os.path.exists(protected_file):
        print(f"❌ Protected file not found: {protected_file}")
        return
    
    print(f"📄 Found protected file: {protected_file}")
    
    # Create a test file monitor
    monitor = SystemFileMonitor()
    
    # Register the existing file as protected
    file_hash = monitor.register_download(protected_file, "employee_data.xlsx", "test_session_real")
    print(f"🔒 Registered protected file with hash: {file_hash[:16]}...")
    
    # Start monitoring
    print("🔍 Starting file monitoring...")
    monitor.start_monitoring()
    
    # Wait a moment for monitoring to start
    time.sleep(2)
    
    # Test: Copy the file to Desktop (this should be detected)
    print("\n🧪 Test: Copying protected file to Desktop...")
    desktop_dir = os.path.expanduser("~/Desktop")
    copy_destination = os.path.join(desktop_dir, "copied_secure_employee_data.xlsx")
    
    try:
        shutil.copy2(protected_file, copy_destination)
        print(f"📋 Copied to: {copy_destination}")
        
        # Wait for detection
        time.sleep(5)
        
        # Get security report
        print("\n📊 Getting security report...")
        report = monitor.get_security_report(hours=1)
        
        print(f"\n🚨 SECURITY REPORT:")
        print(f"Total Incidents: {report['summary']['total_incidents']}")
        print(f"High Severity: {report['summary']['high_severity']}")
        print(f"Medium Severity: {report['summary']['medium_severity']}")
        
        if report['incidents']:
            print(f"\n📋 Recent Incidents:")
            for incident in report['incidents'][:5]:  # Show first 5
                print(f"  • {incident['operation']} at {incident['timestamp']}")
                print(f"    Source: {incident['source']}")
                if incident['destination']:
                    print(f"    Destination: {incident['destination']}")
                print(f"    Severity: {incident['severity']}")
                print()
        else:
            print("  ℹ️ No incidents detected yet")
            print("  This could be because:")
            print("    - File monitoring takes time to detect changes")
            print("    - The file system events haven't been processed yet")
            print("    - The file copy was too fast to be caught")
        
        # Clean up
        if os.path.exists(copy_destination):
            os.remove(copy_destination)
            print(f"🧹 Cleaned up: {copy_destination}")
        
    except Exception as e:
        print(f"❌ Error during file operations: {e}")
    
    finally:
        # Clean up
        print("🛑 Stopping monitor...")
        monitor.stop_monitoring()
        print("✅ Test completed!")

def test_system_monitor_database():
    """Test the database functionality"""
    print("\n🗄️ Testing database functionality...")
    
    monitor = SystemFileMonitor()
    
    # Check what's in the database
    with monitor.tracking_db.db_path as db_path:
        import sqlite3
        conn = sqlite3.connect(monitor.tracking_db.db_path)
        cursor = conn.cursor()
        
        # Check protected files
        cursor.execute("SELECT COUNT(*) FROM protected_files")
        protected_count = cursor.fetchone()[0]
        print(f"📊 Protected files in database: {protected_count}")
        
        # Check file operations
        cursor.execute("SELECT COUNT(*) FROM file_operations")
        operations_count = cursor.fetchone()[0]
        print(f"📊 File operations logged: {operations_count}")
        
        if operations_count > 0:
            cursor.execute("""
                SELECT operation_type, source_path, timestamp, severity 
                FROM file_operations 
                ORDER BY timestamp DESC LIMIT 5
            """)
            recent_ops = cursor.fetchall()
            print("\n📋 Recent operations:")
            for op in recent_ops:
                print(f"  • {op[0]} - {op[1]} ({op[3]}) at {op[2]}")
        
        conn.close()

if __name__ == "__main__":
    try:
        test_real_protected_file()
        test_system_monitor_database()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
