import requests
from datetime import datetime
import time

def test_issues():
    print('🔍 Testing Download and Monitoring Issues...')
    
    # Test 1: Download functionality
    print('\n📥 Testing Download Endpoints...')
    try:
        # Test secure download
        response = requests.get('http://localhost:5000/download-secure/employee_data.xlsx')
        print(f'✅ Secure download: Status {response.status_code}')
        if response.status_code == 200:
            print(f'   File size: {len(response.content)} bytes')
            print(f'   Content-Type: {response.headers.get("Content-Type", "Unknown")}')
        else:
            print(f'   Error: {response.text[:200]}')
    except Exception as e:
        print(f'❌ Download error: {e}')
    
    # Test 2: Add fresh monitoring events
    print('\n🛡️ Adding Fresh Security Events...')
    current_time = datetime.now()
    
    events = [
        {
            'fileId': 'employee_data.xlsx',
            'sessionId': f'test_session_{int(current_time.timestamp())}',
            'eventType': 'FILE_OPENED_FOR_VIEWING',
            'eventData': {
                'timestamp': current_time.isoformat(),
                'browser': 'Test Browser',
                'viewport': {'width': 1920, 'height': 1080}
            },
            'timestamp': current_time.isoformat() + 'Z'
        },
        {
            'fileId': 'employee_data.xlsx',
            'sessionId': f'test_session_{int(current_time.timestamp())}',
            'eventType': 'DOWNLOAD_BUTTON_CLICKED',
            'eventData': {
                'timestamp': current_time.isoformat(),
                'buttonType': 'secure_download'
            },
            'timestamp': current_time.isoformat() + 'Z'
        },
        {
            'fileId': 'employee_data.xlsx', 
            'sessionId': f'test_session_{int(current_time.timestamp())}',
            'eventType': 'CLIPBOARD_COPY_ATTEMPT',
            'eventData': {
                'timestamp': current_time.isoformat(),
                'hasSelection': True,
                'selectionLength': 156
            },
            'timestamp': current_time.isoformat() + 'Z'
        }
    ]
    
    for event in events:
        try:
            response = requests.post('http://localhost:5000/api/file-monitoring', json=event)
            if response.status_code == 200:
                result = response.json()
                print(f'✅ Event logged: {event["eventType"]} - Threat: {result["threat_level"]}')
            else:
                print(f'❌ Failed to log {event["eventType"]}: {response.status_code}')
        except Exception as e:
            print(f'❌ Error logging {event["eventType"]}: {e}')
        
        time.sleep(0.2)
    
    # Test 3: Check if events are retrievable
    print('\n📊 Testing Security Events Retrieval...')
    try:
        response = requests.get('http://localhost:5000/api/security-events?limit=10')
        if response.status_code == 200:
            events = response.json()
            print(f'✅ Found {len(events)} security events')
            
            # Show recent events
            if events:
                print('   Recent events:')
                for event in events[:3]:
                    activity = event.get('activity', 'Unknown')
                    file_name = event.get('file_name', 'Unknown')
                    timestamp = event.get('timestamp', 'Unknown')
                    print(f'   - {activity} on {file_name} at {timestamp[:19]}')
            else:
                print('   No events found in database')
        else:
            print(f'❌ Failed to retrieve events: {response.status_code}')
    except Exception as e:
        print(f'❌ Error retrieving events: {e}')
    
    # Test 4: Check main pages
    print('\n🌐 Testing Page Accessibility...')
    pages = [
        ('Main Page', 'http://localhost:5000/'),
        ('Security Monitor', 'http://localhost:5000/security/monitor'),
        ('File Viewer', 'http://localhost:5000/view/employee_data.xlsx')
    ]
    
    for name, url in pages:
        try:
            response = requests.get(url)
            print(f'✅ {name}: Status {response.status_code}')
        except Exception as e:
            print(f'❌ {name} error: {e}')
    
    print('\n🎯 Summary:')
    print('1. Download buttons should be visible in file viewer')
    print('2. Security events should show in the monitoring dashboard')
    print('3. Check these URLs:')
    print('   📊 Security Monitor: http://localhost:5000/security/monitor')
    print('   📂 File Viewer: http://localhost:5000/view/employee_data.xlsx')
    print('   🏠 Main App: http://localhost:5000/')

if __name__ == '__main__':
    test_issues()
