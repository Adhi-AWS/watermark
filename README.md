# Secure Excel Viewer with Activity Tracking

This application provides a secure way to share Excel files with comprehensive activity tracking, preventing downloads while allowing viewing and controlled printing.

## Features

🔒 **Security Features:**
- Files viewed in browser only (no downloads)
- Disabled right-click, copy, save shortcuts
- Print tracking and watermarking
- Developer tools detection
- Session-based access control

📊 **Activity Tracking:**
- File access logging
- Time spent tracking
- User interactions (clicks, scrolls)
- Print requests monitoring
- Security violation attempts
- Real-time dashboard

🛡️ **Copy Protection:**
- Text selection disabled
- Keyboard shortcuts blocked
- Drag-and-drop prevention
- Context menu disabled
- Watermarked content

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Excel Files
Place your Excel files in the `secure_files/` directory:
```
secure_files/
├── confidential_data.xlsx
├── financial_report.xlsx
└── employee_list.xlsx
```

### 3. Run the Application
```bash
python app.py
```

### 4. Access the Application
- **Main Interface:** http://localhost:5000
- **Admin Dashboard:** http://localhost:5000/admin/logs
- **API Logs:** http://localhost:5000/api/logs

## How It Works

### User Experience:
1. User clicks "download" link (from your main application)
2. Instead of downloading, file opens in controlled browser window
3. User can view and print (with tracking) but cannot save locally
4. All activities are logged in real-time

### Admin Monitoring:
- Real-time activity dashboard
- Detailed logs with timestamps
- Security event alerts
- Session tracking
- Print monitoring

## Integration with Your Main Application

### Option 1: Direct Link Integration
```html
<!-- Replace regular download links with secure viewer links -->
<a href="http://your-server:5000/view/filename.xlsx" target="_blank">
    View Secure Document
</a>
```

### Option 2: API Integration
```python
# In your main application
import requests

def create_secure_link(filename):
    # Upload file to secure server
    response = requests.post('http://your-server:5000/api/upload', 
                           files={'file': open(filename, 'rb')})
    
    # Return secure viewing link
    return f"http://your-server:5000/view/{filename}"
```

### Option 3: Redirect Method
```python
# In your download handler
@app.route('/download/<filename>')
def download_file(filename):
    # Instead of serving file, redirect to secure viewer
    return redirect(f"http://secure-server:5000/view/{filename}")
```

## Activity Tracking Data

The system tracks comprehensive user activities:

```json
{
  "timestamp": "2025-08-29T10:30:45.123Z",
  "session_id": "uuid-string",
  "activity": "FILE_OPENED",
  "file_name": "confidential_data.xlsx",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "additional_info": {
    "screen_resolution": "1920x1080",
    "browser": "Chrome",
    "sheets_count": 3
  }
}
```

## Tracked Activities

- `HOMEPAGE_LOADED` - User accessed main page
- `FILE_SELECTED` - User clicked on file
- `FILE_OPENED` - File successfully loaded
- `FILE_VIEWED` - File content displayed
- `SHEET_SWITCHED` - User changed Excel sheet
- `SCROLL_ACTIVITY` - User scrolled content
- `CLICK_EVENT` - User clicked on content
- `TIME_TRACKING` - Periodic time spent updates
- `PRINT_INITIATED` - User requested print
- `PRINT_COMPLETED` - Print job finished
- `BLOCKED_SHORTCUT` - Security: Blocked copy/save attempt
- `RIGHT_CLICK_ATTEMPT` - Security: Right-click blocked
- `DRAG_ATTEMPT` - Security: Drag attempt blocked
- `DEVTOOLS_OPENED` - Security: Developer tools detected
- `WINDOW_FOCUSED/BLURRED` - Window focus changes
- `FILE_CLOSED` - User closed file

## Security Measures

### Client-Side Protection:
- Text selection disabled
- Right-click context menu blocked
- Keyboard shortcuts (Ctrl+C, Ctrl+S, F12) prevented
- Drag and drop disabled
- Developer tools detection

### Server-Side Protection:
- Session-based access
- Activity logging
- File access control
- Print watermarking

### Network Security:
- CORS configuration
- Session management
- Request logging

## Deployment Options

### Development (Local)
```bash
python app.py
# Access at http://localhost:5000
```

### Production (Server)
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t secure-excel-viewer .
docker run -p 5000:5000 secure-excel-viewer
```

### Cloud Deployment
- Deploy on AWS EC2, Azure VM, or Google Cloud
- Use HTTPS with SSL certificate
- Configure firewall rules
- Set up domain name

## Limitations

⚠️ **Important Notes:**
- Users must have internet connection for tracking
- Requires modern browser with JavaScript enabled
- Cannot prevent screenshots or photos of screen
- Cannot track activities outside the browser
- Advanced users might bypass some protections

## Customization

### Modify Tracking Events
Edit the JavaScript in `templates/viewer.html` to add custom tracking:

```javascript
// Add custom tracking
function trackCustomEvent() {
    trackActivity('CUSTOM_EVENT', {
        custom_data: 'your_value'
    });
}
```

### Customize UI
- Modify templates in `templates/` directory
- Update CSS styles for branding
- Add company logos and watermarks

### Add Authentication
```python
# Add login requirement
@app.before_request
def require_auth():
    if request.endpoint in ['view_file', 'print_file']:
        if not session.get('authenticated'):
            return redirect('/login')
```

## API Endpoints

- `GET /` - Main file listing page
- `GET /view/<filename>` - Secure file viewer
- `GET /print/<filename>` - Print-friendly version
- `POST /track` - Activity tracking endpoint
- `GET /admin/logs` - Admin dashboard
- `GET /api/logs` - JSON logs API

## Troubleshooting

### Common Issues:

1. **Files not showing up**
   - Check files are in `secure_files/` directory
   - Verify file extensions (.xlsx, .xls)

2. **Tracking not working**
   - Check network connectivity
   - Verify JavaScript is enabled
   - Check browser console for errors

3. **Print not working**
   - Check popup blocker settings
   - Verify browser print permissions

## Support

For issues or customization requests, check the activity logs in `/admin/logs` for debugging information.
