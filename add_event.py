import requests
from datetime import datetime
import time

# Simple test to add events
base_url = 'http://localhost:5000/api/file-monitoring'

event_data = {
    'fileId': 'employee_data.xlsx',
    'sessionId': f'live_session_{int(time.time())}',
    'eventType': 'LIVE_TEST_EVENT',
    'eventData': {
        'message': 'Testing real-time monitoring',
        'timestamp': datetime.now().isoformat()
    },
    'timestamp': datetime.now().isoformat() + 'Z'
}

try:
    response = requests.post(base_url, json=event_data)
    print(f'Event added - Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print(f'Threat Level: {result["threat_level"]}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Error: {e}')

print('Check security monitor for the new event!')
