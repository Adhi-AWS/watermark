#!/usr/bin/env python3
"""
System Restoration Test Script
Tests all components of the Excel Encryption System after corruption fix
"""

import os
import sys
import requests
import time
import threading
from datetime import datetime

def test_database():
    """Test database functionality"""
    print("🗄️  Testing Database...")
    try:
        from activity_database import ActivityDatabase
        db = ActivityDatabase()
        
        # Test basic operations
        test_timestamp = datetime.now().isoformat()
        db.add_activity(
            timestamp=test_timestamp,
            session_id="test_session",
            activity="SYSTEM_TEST",
            file_name="test_file.xlsx",
            ip_address="127.0.0.1",
            additional_info={"test": True}
        )
        
        # Verify the record exists
        activities = db.get_activities()
        if activities:
            print("   ✅ Database operations working")
            return True
        else:
            print("   ❌ Database operations failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_file_structure():
    """Test file structure"""
    print("📁 Testing File Structure...")
    
    required_files = [
        'app.py',
        'activity_database.py',
        'excel_protection.py',
        'file_monitoring.py',
        'templates/index.html',
        'templates/viewer.html',
        'templates/security_monitor.html',
        'secure_files/employee_data.xlsx',
        'secure_files/financial_report.xlsx',
        'secure_files/project_status.xlsx'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def start_flask_app():
    """Start Flask app in a separate thread"""
    import subprocess
    import sys
    
    def run_app():
        try:
            subprocess.run([sys.executable, 'app.py'], check=True)
        except Exception as e:
            print(f"Flask app error: {e}")
    
    thread = threading.Thread(target=run_app, daemon=True)
    thread.start()
    
    # Wait for app to start
    time.sleep(3)
    return thread

def test_flask_endpoints():
    """Test Flask endpoints"""
    print("🌐 Testing Flask Endpoints...")
    
    base_url = "http://127.0.0.1:5000"
    endpoints = [
        "/",
        "/api/files",
        "/security/monitor",
        "/admin/audit"
    ]
    
    all_working = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {endpoint} - Status {response.status_code}")
            else:
                print(f"   ⚠️  {endpoint} - Status {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
            all_working = False
    
    return all_working

def test_api_functionality():
    """Test API functionality"""
    print("🔧 Testing API Functionality...")
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test file monitoring API
        monitoring_data = {
            'fileId': 'test.xlsx',
            'sessionId': 'test_session',
            'eventType': 'API_TEST',
            'eventData': {'test': True},
            'timestamp': datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{base_url}/api/file-monitoring",
            json=monitoring_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print("   ✅ File monitoring API working")
        else:
            print(f"   ❌ File monitoring API failed - Status {response.status_code}")
            return False
            
        # Test security events API
        response = requests.get(f"{base_url}/api/security-events", timeout=5)
        if response.status_code == 200:
            events = response.json()
            print(f"   ✅ Security events API working - {len(events)} events found")
            return True
        else:
            print(f"   ❌ Security events API failed - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ API test error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Excel Encryption System - Restoration Test")
    print("=" * 50)
    
    # Test file structure
    file_structure_ok = test_file_structure()
    
    # Test database
    database_ok = test_database()
    
    # Start Flask app
    print("🌐 Starting Flask Application...")
    flask_thread = start_flask_app()
    
    # Test Flask endpoints
    endpoints_ok = test_flask_endpoints()
    
    # Test API functionality
    api_ok = test_api_functionality()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    tests = [
        ("File Structure", file_structure_ok),
        ("Database Operations", database_ok),
        ("Flask Endpoints", endpoints_ok),
        ("API Functionality", api_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} : {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("\n🌟 Access your application at:")
        print("   • Main App: http://127.0.0.1:5000")
        print("   • Security Monitor: http://127.0.0.1:5000/security/monitor")
        print("   • Audit Log: http://127.0.0.1:5000/admin/audit")
    else:
        print("\n⚠️  SOME ISSUES DETECTED - Check failed tests above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
