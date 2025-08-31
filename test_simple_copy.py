#!/usr/bin/env python3
"""
Simple Copy Detection Test
"""

import os
import time
import shutil
from system_file_monitor import SystemFileMonitor
import sqlite3

def test_copy_detection():
    """Simple test to verify copy detection"""
    print("🧪 Testing Copy Detection...")
    
    # Use the existing protected file in Downloads
    downloads_dir = os.path.expanduser("~/Downloads")
    protected_file = os.path.join(downloads_dir, "secure_employee_data.xlsx")
    
    if not os.path.exists(protected_file):
        print(f"❌ Protected file not found: {protected_file}")
        return
    
    # Create monitor and register file
    monitor = SystemFileMonitor()
    file_hash = monitor.register_download(protected_file, "employee_data.xlsx", "test_session")
    print(f"📄 Registered: {protected_file}")
    print(f"🔒 Hash: {file_hash[:16]}...")
    
    # Start monitoring
    monitor.start_monitoring()
    time.sleep(2)
    
    # Test copy to current directory
    copy_destination = "test_copy.xlsx"
    print(f"\n📋 Copying to: {copy_destination}")
    
    try:
        shutil.copy2(protected_file, copy_destination)
        print("✅ Copy completed")
        
        # Wait for detection
        time.sleep(3)
        
        # Check database directly
        print("\n📊 Checking database...")
        conn = sqlite3.connect(monitor.tracking_db.db_path)
        cursor = conn.cursor()
        
        # Get recent operations
        cursor.execute("""
            SELECT operation_type, source_path, destination_path, timestamp, severity 
            FROM file_operations 
            ORDER BY timestamp DESC LIMIT 10
        """)
        
        operations = cursor.fetchall()
        print(f"Found {len(operations)} operations in database:")
        
        for op in operations:
            print(f"  • {op[0]} | {op[4]} | {op[3]}")
            print(f"    Source: {op[1]}")
            if op[2]:
                print(f"    Dest: {op[2]}")
        
        conn.close()
        
        # Clean up
        if os.path.exists(copy_destination):
            os.remove(copy_destination)
            print(f"🧹 Removed: {copy_destination}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        monitor.stop_monitoring()
        print("✅ Test completed")

if __name__ == "__main__":
    test_copy_detection()
