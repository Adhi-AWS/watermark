#!/usr/bin/env python3
"""
System File Monitor Test
Test the file copy tracking functionality
"""

import os
import time
import shutil
from system_file_monitor import SystemFileMonitor
from datetime import datetime

def test_file_tracking():
    """Test file copy tracking"""
    print("🧪 Testing System File Monitor...")
    
    # Create a test file monitor
    monitor = SystemFileMonitor()
    
    # Create a test protected file
    test_file = "test_protected_file.xlsx"
    with open(test_file, 'w') as f:
        f.write("Test Excel Content")
    
    print(f"📄 Created test file: {test_file}")
    
    # Register it as a protected file
    file_hash = monitor.register_download(test_file, "original_test_file.xlsx", "test_session_123")
    print(f"🔒 Registered protected file with hash: {file_hash[:16]}...")
    
    # Start monitoring
    print("🔍 Starting file monitoring...")
    monitor.start_monitoring()
    
    # Wait a moment for monitoring to start
    time.sleep(2)
    
    # Test 1: Copy the file (this should be detected)
    print("\n🧪 Test 1: Copying protected file...")
    copy_destination = "copied_test_file.xlsx"
    shutil.copy2(test_file, copy_destination)
    print(f"📋 Copied {test_file} to {copy_destination}")
    
    # Wait for detection
    time.sleep(3)
    
    # Test 2: Move the copied file (this should be detected)
    print("\n🧪 Test 2: Moving copied file...")
    move_destination = "moved_test_file.xlsx"
    shutil.move(copy_destination, move_destination)
    print(f"📁 Moved {copy_destination} to {move_destination}")
    
    # Wait for detection
    time.sleep(3)
    
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
        print("  No incidents detected")
    
    # Clean up
    print("🧹 Cleaning up...")
    monitor.stop_monitoring()
    
    # Remove test files
    for file in [test_file, move_destination]:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Removed: {file}")
    
    print("✅ Test completed!")

if __name__ == "__main__":
    try:
        test_file_tracking()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
