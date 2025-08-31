import requests
import time
from datetime import datetime

def test_system():
    print('🔍 Testing Flask app functionality...')
    
    # Test basic connectivity
    try:
        response = requests.get('http://localhost:5000/')
        print(f'✅ Main page: Status {response.status_code}')
    except Exception as e:
        print(f'❌ Main page error: {e}')
        return
    
    # Test security monitor page
    try:
        response = requests.get('http://localhost:5000/security/monitor')
        print(f'✅ Security monitor: Status {response.status_code}')
    except Exception as e:
        print(f'❌ Security monitor error: {e}')
    
    # Test download functionality
    try:
        response = requests.get('http://localhost:5000/test-download/employee_data.xlsx')
        print(f'✅ Download test: Status {response.status_code}, Size: {len(response.content)} bytes')
    except Exception as e:
        print(f'❌ Download test error: {e}')
    
    print('\n🛡️ Adding live security monitoring events...')
    
    # Simulate real-time security events
    events = [
        {
            'eventType': 'FILE_MONITORING_INITIALIZED', 
            'eventData': {
                'filename': 'employee_data.xlsx', 
                'viewport': {'width': 1920, 'height': 1080}
            }
        },
        {
            'eventType': 'CLIPBOARD_COPY_ATTEMPT', 
            'eventData': {
                'hasSelection': True, 
                'selectionLength': 156
            }
        },
        {
            'eventType': 'SUSPICIOUS_KEYPRESS', 
            'eventData': {
                'key': 'c', 
                'ctrlKey': True
            }
        },
        {
            'eventType': 'CONTEXT_MENU_BLOCKED', 
            'eventData': {
                'x': 450, 
                'y': 300
            }
        },
        {
            'eventType': 'WINDOW_FOCUS_LOST', 
            'eventData': {
                'timeInFocus': 25000
            }
        }
    ]
    
    for i, event in enumerate(events):
        data = {
            'fileId': 'employee_data.xlsx',
            'sessionId': f'live_demo_{int(time.time())}',
            'eventType': event['eventType'],
            'eventData': event['eventData'],
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        try:
            response = requests.post('http://localhost:5000/api/file-monitoring', json=data)
            if response.status_code == 200:
                result = response.json()
                event_name = event['eventType']
                threat_level = result['threat_level']
                print(f'✅ {event_name} - Threat Level: {threat_level}')
            else:
                print(f'❌ Failed to log event: Status {response.status_code}')
        except Exception as e:
            print(f'❌ Error logging event: {e}')
        
        time.sleep(0.5)
    
    print('\n🎯 System is now active! Check these URLs:')
    print('📊 Security Monitor: http://localhost:5000/security/monitor')
    print('📈 Admin Audit: http://localhost:5000/admin/audit')
    print('🏠 Main App: http://localhost:5000/')
    print('📂 View File: http://localhost:5000/view/employee_data.xlsx')

if __name__ == '__main__':
    test_system()
