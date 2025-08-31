import requests
import json
from datetime import datetime, timedelta
import time

# Test multiple security events
base_url = 'http://localhost:5000/api/file-monitoring'

# High threat events
high_threat_events = [
    {'eventType': 'CLIPBOARD_CUT_ATTEMPT', 'eventData': {'hasSelection': True}},
    {'eventType': 'SUSPICIOUS_KEYPRESS', 'eventData': {'key': 'PrintScreen'}},
    {'eventType': 'FILE_DRAG_ATTEMPT', 'eventData': {'fileType': 'file_drag'}},
    {'eventType': 'PRINT_ATTEMPT', 'eventData': {'userInitiated': True}},
    {'eventType': 'SAVE_ATTEMPT', 'eventData': {'saveAsUI': True}}
]

# Medium threat events
medium_threat_events = [
    {'eventType': 'WINDOW_FOCUS_LOST', 'eventData': {'timeInFocus': 30000}},
    {'eventType': 'VISIBILITY_CHANGE', 'eventData': {'hidden': True}},
    {'eventType': 'FILE_DROP_DETECTED', 'eventData': {'fileCount': 2}},
    {'eventType': 'DEVELOPER_TOOLS_DETECTED', 'eventData': {'toolsOpen': True}}
]

# Low threat events
low_threat_events = [
    {'eventType': 'MONITORING_HEARTBEAT', 'eventData': {'sessionDuration': 120000}},
    {'eventType': 'TEXT_SELECTION_STARTED', 'eventData': {'selectionLength': 10}},
    {'eventType': 'PAGE_UNLOAD_ATTEMPT', 'eventData': {'userInitiated': False}}
]

all_events = high_threat_events + medium_threat_events + low_threat_events

print('Adding test security events...')
for i, event in enumerate(all_events):
    data = {
        'fileId': f'employee_data_{i % 3 + 1}.xlsx',
        'sessionId': f'session_{i % 5 + 1}',
        'eventType': event['eventType'],
        'eventData': event['eventData'],
        'timestamp': (datetime.now() - timedelta(minutes=i*2)).isoformat() + 'Z'
    }
    
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            result = response.json()
            event_name = event['eventType']
            threat_level = result['threat_level']
            print(f'✅ {event_name} - Threat Level: {threat_level}')
        else:
            print(f'❌ Failed: {response.status_code}')
    except Exception as e:
        print(f'Error: {e}')
    
    time.sleep(0.1)

print('\nTest events added! Check the security monitor dashboard.')
print('Dashboard URL: http://localhost:5000/security/monitor')
