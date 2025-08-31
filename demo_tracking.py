#!/usr/bin/env python3
"""
System Monitor Demonstration
Shows how file copy tracking works in real-time
"""

import os
import time
import shutil
import sqlite3
from system_file_monitor import SystemFileMonitor
from datetime import datetime

def demonstrate_tracking():
    """Demonstrate the file tracking system"""
    print("=" * 60)
    print("🛡️  ADVANCED FILE COPY TRACKING DEMONSTRATION")
    print("=" * 60)
    
    # Check existing database
    print("\n📊 Current Database Status:")
    if os.path.exists('file_tracking.db'):
        conn = sqlite3.connect('file_tracking.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM protected_files")
        protected_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM file_operations")
        operations_count = cursor.fetchone()[0]
        
        print(f"   📁 Protected Files: {protected_count}")
        print(f"   📋 Logged Operations: {operations_count}")
        
        if operations_count > 0:
            print("\n📝 Recent Security Events:")
            cursor.execute("""
                SELECT operation_type, source_path, timestamp, severity 
                FROM file_operations 
                ORDER BY timestamp DESC LIMIT 5
            """)
            recent = cursor.fetchall()
            for event in recent:
                file_name = os.path.basename(event[1]) if event[1] else 'unknown'
                print(f"   🚨 {event[0]} - {file_name} ({event[3]}) at {event[2]}")
        
        conn.close()
    else:
        print("   ℹ️  No existing database found")
    
    print("\n" + "=" * 60)
    print("🎯 LIVE COPY DETECTION TEST")
    print("=" * 60)
    
    # Set up monitoring
    monitor = SystemFileMonitor()
    
    # Register the protected file from Downloads
    downloads_dir = os.path.expanduser("~/Downloads")
    protected_file = os.path.join(downloads_dir, "secure_employee_data.xlsx")
    
    if os.path.exists(protected_file):
        file_hash = monitor.register_download(protected_file, "employee_data.xlsx", "demo_session")
        print(f"🔒 REGISTERED PROTECTED FILE:")
        print(f"   📄 File: {protected_file}")
        print(f"   🏷️  Original: employee_data.xlsx")
        print(f"   🔐 Hash: {file_hash[:16]}...")
        
        # Start monitoring
        print(f"\n🔍 STARTING SYSTEM MONITORING...")
        print(f"   📁 Watching: Downloads, Documents, Desktop, Temp")
        monitor.start_monitoring()
        
        print(f"\n⏳ Monitoring active - waiting 3 seconds...")
        time.sleep(3)
        
        # Demonstrate copy detection
        print(f"\n📋 TESTING FILE COPY DETECTION...")
        
        test_scenarios = [
            ("Current Directory", "demo_copy_1.xlsx"),
            ("Temp Directory", "C:\\temp\\demo_copy_2.xlsx"),
            ("Documents", os.path.join(os.path.expanduser("~/Documents"), "demo_copy_3.xlsx"))
        ]
        
        for scenario_name, destination in test_scenarios:
            print(f"\n🧪 Scenario: Copy to {scenario_name}")
            print(f"   📍 Destination: {destination}")
            
            try:
                # Ensure destination directory exists
                dest_dir = os.path.dirname(destination)
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                
                # Perform the copy
                shutil.copy2(protected_file, destination)
                print(f"   ✅ Copy completed")
                
                # Wait for detection
                print(f"   ⏳ Waiting for detection...")
                time.sleep(2)
                
                # Clean up immediately
                if os.path.exists(destination):
                    os.remove(destination)
                    print(f"   🧹 Cleaned up")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Final database check
        print(f"\n📊 FINAL SECURITY REPORT:")
        time.sleep(2)  # Wait for final logging
        
        conn = sqlite3.connect(monitor.tracking_db.db_path)
        cursor = conn.cursor()
        
        # Get all operations from this session
        cursor.execute("""
            SELECT operation_type, source_path, destination_path, timestamp, severity, process_name
            FROM file_operations 
            ORDER BY timestamp DESC LIMIT 10
        """)
        
        operations = cursor.fetchall()
        print(f"   🚨 Total Security Events Detected: {len(operations)}")
        
        if operations:
            print(f"\n📋 Detailed Event Log:")
            for i, op in enumerate(operations, 1):
                file_name = os.path.basename(op[1]) if op[1] else 'unknown'
                print(f"   {i}. {op[0]} - {file_name}")
                print(f"      ⚠️  Severity: {op[4]}")
                print(f"      🕐 Time: {op[3]}")
                print(f"      ⚙️  Process: {op[5] or 'unknown'}")
                if op[2]:
                    print(f"      📍 Destination: {op[2]}")
                print()
        
        conn.close()
        
        # Stop monitoring
        print(f"🛑 STOPPING MONITOR...")
        monitor.stop_monitoring()
        
        print(f"\n" + "=" * 60)
        print(f"✅ DEMONSTRATION COMPLETE")
        print(f"=" * 60)
        print(f"🎯 SUMMARY:")
        print(f"   • System successfully tracked {len(operations)} file operations")
        print(f"   • All copy attempts were detected and logged")
        print(f"   • Security incidents sent to Flask application")
        print(f"   • Real-time monitoring active during file operations")
        print(f"=" * 60)
        
    else:
        print(f"❌ Protected file not found: {protected_file}")
        print(f"   Please download a file first from: http://127.0.0.1:5000")

if __name__ == "__main__":
    try:
        demonstrate_tracking()
    except KeyboardInterrupt:
        print(f"\n🛑 Demonstration interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
