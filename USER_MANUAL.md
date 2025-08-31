# Secure Excel Viewer - User Manual & Setup Guide

## 📚 Table of Contents
1. [Overview](#overview)
2. [Installation Guide](#installation-guide)
3. [Configuration](#configuration)
4. [User Guide](#user-guide)
5. [Admin Guide](#admin-guide)
6. [Integration Guide](#integration-guide)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## 🔍 Overview

### What is Secure Excel Viewer?
The Secure Excel Viewer is a web-based application that allows users to view Excel files securely in their browser without the ability to download, copy, or save the original files. Every user interaction is tracked and logged for security and compliance purposes.

### Key Benefits
- ✅ **No Downloads**: Users view files in browser only
- ✅ **Complete Tracking**: Every action is monitored and logged
- ✅ **Copy Protection**: Users cannot save or copy content
- ✅ **Print Control**: Printing is allowed but tracked and watermarked
- ✅ **Real-time Monitoring**: Admin dashboard shows live activity
- ✅ **Easy Integration**: Simple to integrate with existing applications

### Use Cases
- **Confidential Document Sharing**: Share sensitive Excel files without risk of unauthorized copying
- **Compliance Monitoring**: Track who accessed what documents and when
- **Audit Trails**: Maintain detailed logs for regulatory compliance
- **Internal Document Control**: Control access to internal company data
- **Client Data Protection**: Share client data securely with tracking

## 🚀 Installation Guide

### Prerequisites
- **Python 3.8+** installed on your system
- **Web browser** (Chrome, Firefox, Safari, Edge)
- **Network access** for tracking functionality
- **Administrator rights** for installation (if deploying on server)

### Step 1: Download and Setup
```bash
# Clone or download the project files
cd /path/to/your/project

# Install required Python packages
pip install -r requirements.txt
```

### Step 2: Verify Installation
```bash
# Test the installation
python app.py
```

You should see:
```
Starting Secure Excel Viewer...
Upload your Excel files to the 'secure_files' directory
Access the application at: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

### Step 3: Add Your Excel Files
1. Place your Excel files in the `secure_files/` directory
2. Supported formats: `.xlsx`, `.xls`
3. File names should not contain special characters

### Step 4: Access the Application
Open your web browser and go to: `http://localhost:5000`

## ⚙️ Configuration

### Basic Configuration

#### File Storage Location
Edit `app.py` to change where Excel files are stored:
```python
# Change this line in app.py
EXCEL_FILES_DIR = 'secure_files'  # Change to your preferred directory
```

#### Server Port
Change the port number:
```python
# At the bottom of app.py
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port here
```

#### Activity Log Storage
Change where activity logs are saved:
```python
# Change this line in app.py
ACTIVITY_LOG_FILE = 'activity_logs.json'  # Change filename/path
```

### Advanced Configuration

#### Security Settings
```python
# Add to app.py for enhanced security
app.config.update(
    SECRET_KEY='your-very-secure-secret-key-here',
    SESSION_COOKIE_SECURE=True,  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # Prevent JS access
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2)  # Session timeout
)
```

#### Custom Watermarks
Edit `templates/viewer.html` and `templates/print.html`:
```css
.watermark {
    /* Change watermark text */
    content: "YOUR COMPANY NAME";
    font-size: 6rem;
    color: rgba(0,0,0,0.05);
}
```

#### Custom Branding
Update templates with your company branding:
```html
<!-- In templates/index.html -->
<h1 class="mb-0">🔒 Your Company Secure Viewer</h1>
<p class="mb-0">Your custom message here</p>
```

## 👤 User Guide

### Accessing Files

#### Step 1: Open the Application
1. Click on the secure link provided by your administrator
2. You'll see the main page with available files
3. Files are displayed as cards with file names

#### Step 2: View a File
1. Click on any file card to open it
2. The file will open in a new browser window
3. You'll see the Excel content converted to web format

### Using the Viewer

#### Navigation
- **Sheet Tabs**: If the Excel file has multiple sheets, you'll see tabs at the top
- **Scrolling**: Use mouse wheel or scrollbar to navigate content
- **Zoom**: Use browser zoom (Ctrl + / Ctrl -)

#### Available Actions
- **View Content**: Read all data in the spreadsheet
- **Print**: Click the 🖨️ Print button for a print-friendly version
- **Close**: Click the ✕ Close button or close the browser tab

#### Restrictions
- ❌ **No Copy/Paste**: Text selection and copying is disabled
- ❌ **No Right-Click**: Context menu is blocked
- ❌ **No Downloads**: Cannot save the file to your computer
- ❌ **No Screenshots**: Attempts are detected and logged
- ❌ **No Developer Tools**: Access is detected and logged

### Print Functionality

#### How to Print
1. Click the 🖨️ Print button in the viewer
2. A new print window will open
3. Use your browser's print dialog (Ctrl+P)
4. Select your printer and print settings

#### Print Features
- **Watermarked**: All prints include security watermarks
- **Tracked**: All print attempts are logged
- **Formatted**: Optimized layout for printing
- **Header/Footer**: Includes document info and timestamps

### Understanding Tracking

#### What is Tracked
Your activity is monitored for security purposes:
- When you open and close files
- How long you spend viewing
- Your scroll and click patterns
- Print requests
- Any attempts to copy or save content

#### Privacy Information
- **Session-based**: You're identified by a session ID, not personal info
- **IP Address**: Your IP address is logged for security
- **Browser Info**: Basic browser information is recorded
- **No Personal Data**: No personal information is collected beyond what's necessary for security

## 🛠️ Admin Guide

### Admin Dashboard

#### Accessing the Dashboard
1. Go to: `http://your-server:5000/admin/logs`
2. You'll see the real-time activity monitoring dashboard

#### Dashboard Features

##### Statistics Cards
- **Total Sessions**: Number of unique user sessions
- **Files Opened**: Count of file access events
- **Print Requests**: Number of print attempts
- **Security Events**: Count of blocked actions

##### Activity Log
- **Real-time Updates**: Automatically refreshes every 5 seconds
- **Color Coding**: Different colors for different activity types
  - 🟢 Green: File operations (open, close)
  - 🟡 Yellow: Print actions
  - 🔴 Red: Security violations

##### Filtering Options
- **Activity Filter**: Filter by specific activity types
- **Session Filter**: Find activities by session ID
- **File Filter**: Filter by filename

### Managing Files

#### Adding New Files
1. Copy Excel files to the `secure_files/` directory
2. Ensure files have `.xlsx` or `.xls` extensions
3. Restart the application if files don't appear immediately

#### Removing Files
1. Delete files from the `secure_files/` directory
2. Files will no longer be accessible to users

### Monitoring User Activity

#### Key Metrics to Watch
- **Time Spent**: How long users spend viewing documents
- **Print Frequency**: How often documents are printed
- **Security Events**: Any attempts to bypass security
- **Access Patterns**: Which files are accessed most frequently

#### Security Alerts
Watch for these red flags:
- Multiple `BLOCKED_SHORTCUT` events from same session
- `DEVTOOLS_OPENED` events (users trying to inspect code)
- High frequency of `RIGHT_CLICK_ATTEMPT` events
- Sessions with very short view times (possible automated access)

### Log Management

#### Log File Location
Activity logs are stored in: `activity_logs.json`

#### Log Rotation
For production use, implement log rotation:
```python
# Add to app.py
import logging.handlers

def setup_log_rotation():
    handler = logging.handlers.RotatingFileHandler(
        'activity_logs.log', maxBytes=10485760, backupCount=5)
    # Configure handler...
```

#### Exporting Logs
Use the API endpoint to export logs:
```bash
# Export all logs
curl http://your-server:5000/api/logs > exported_logs.json

# Export filtered logs
curl "http://your-server:5000/api/logs?activity=FILE_OPENED" > file_access_logs.json
```

## 🔗 Integration Guide

### Integration Methods

#### Method 1: Direct Link Replacement
Replace your existing download links:

**Before:**
```html
<a href="/download/confidential_report.xlsx">Download Report</a>
```

**After:**
```html
<a href="http://secure-viewer:5000/view/confidential_report.xlsx" target="_blank">
    View Secure Report
</a>
```

#### Method 2: Server-Side Redirect
Update your download endpoint:

**Flask Example:**
```python
@app.route('/download/<filename>')
def download_file(filename):
    # Instead of serving file, redirect to secure viewer
    return redirect(f'http://secure-viewer:5000/view/{filename}')
```

**Django Example:**
```python
from django.shortcuts import redirect

def download_file(request, filename):
    return redirect(f'http://secure-viewer:5000/view/{filename}')
```

#### Method 3: API Integration
Programmatically manage files:

```python
import requests

class SecureFileManager:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def upload_file(self, file_path, filename):
        """Upload file to secure viewer"""
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f)}
            response = requests.post(f'{self.base_url}/api/upload', files=files)
        return response.json()
    
    def get_view_link(self, filename):
        """Get secure viewing link"""
        return f'{self.base_url}/view/{filename}'
    
    def get_activity_logs(self, filename=None):
        """Get activity logs for a file"""
        params = {'filename': filename} if filename else {}
        response = requests.get(f'{self.base_url}/api/logs', params=params)
        return response.json()

# Usage
manager = SecureFileManager('http://secure-viewer:5000')
link = manager.get_view_link('confidential_report.xlsx')
```

### Integration Examples

#### WordPress Plugin
```php
<?php
// WordPress shortcode for secure file links
function secure_file_shortcode($atts) {
    $atts = shortcode_atts(array(
        'file' => '',
        'title' => 'View File'
    ), $atts);
    
    $secure_url = 'http://secure-viewer:5000/view/' . $atts['file'];
    return sprintf('<a href="%s" target="_blank">%s</a>', $secure_url, $atts['title']);
}
add_shortcode('secure_file', 'secure_file_shortcode');

// Usage: [secure_file file="report.xlsx" title="View Report"]
?>
```

#### React Component
```jsx
import React from 'react';

const SecureFileLink = ({ filename, title, className }) => {
    const secureUrl = `http://secure-viewer:5000/view/${filename}`;
    
    return (
        <a 
            href={secureUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className={className}
        >
            🔒 {title}
        </a>
    );
};

// Usage: <SecureFileLink filename="report.xlsx" title="View Report" />
```

## 🔧 Troubleshooting

### Common Issues

#### Files Not Showing Up
**Problem**: Files placed in `secure_files/` directory don't appear on the main page

**Solutions:**
1. Check file extensions (must be `.xlsx` or `.xls`)
2. Ensure no special characters in filenames
3. Restart the application
4. Check file permissions (read access required)

#### Tracking Not Working
**Problem**: User activities are not being logged

**Solutions:**
1. Check network connectivity
2. Verify JavaScript is enabled in browser
3. Check browser console for errors (F12)
4. Ensure cookies are enabled
5. Check if requests are being blocked by firewall

#### Print Function Not Working
**Problem**: Print button doesn't work or print window doesn't open

**Solutions:**
1. Check popup blocker settings
2. Enable popups for the secure viewer domain
3. Try different browser
4. Check browser print permissions

#### Performance Issues
**Problem**: Slow loading or viewing of Excel files

**Solutions:**
1. Reduce file size (large Excel files take time to process)
2. Limit number of rows/columns
3. Split large files into smaller ones
4. Increase server memory allocation

### Error Messages

#### "File not found"
- File doesn't exist in `secure_files/` directory
- Filename mismatch (check spelling and case)
- File permissions issue

#### "Error reading file"
- Excel file is corrupted
- Unsupported Excel format
- File is password protected
- Insufficient memory to process large file

#### "No session"
- Cookies are disabled
- Session expired
- Browser privacy settings blocking session cookies

### Browser Compatibility

#### Supported Browsers
- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

#### Known Issues
- **Internet Explorer**: Not supported (lacks modern JavaScript features)
- **Mobile Browsers**: Limited functionality on small screens
- **Older Browsers**: Some security features may not work

### Network Issues

#### CORS Errors
If accessing from different domain, configure CORS:
```python
from flask_cors import CORS
CORS(app, origins=['http://your-main-app.com'])
```

#### SSL/HTTPS Issues
For production, use HTTPS:
```python
app.run(ssl_context='adhoc', port=443)  # Self-signed certificate
# Or use proper SSL certificate
```

## ❓ FAQ

### General Questions

**Q: Can users download the Excel files?**
A: No, users can only view files in the browser. The original Excel files are never sent to the user's computer.

**Q: What happens if a user takes a screenshot?**
A: Screenshots cannot be prevented by software, but such actions can be detected when the window loses focus, and this is logged for audit purposes.

**Q: Can users print the documents?**
A: Yes, but all prints are tracked, logged, and include security watermarks. The print function can be disabled if needed.

**Q: How accurate is the activity tracking?**
A: Very accurate for digital interactions (clicks, scrolls, time spent). Physical actions like screenshots or photos cannot be prevented or tracked.

### Technical Questions

**Q: What Excel features are supported?**
A: Basic spreadsheet data, multiple sheets, and formatting. Complex features like macros, pivot tables, and charts are converted to static content.

**Q: Can the system handle large Excel files?**
A: Files up to ~50MB work well. Larger files may take longer to process or cause performance issues.

**Q: Is the tracking data secure?**
A: Yes, tracking data includes session IDs and IP addresses but no personal information. Data is stored locally on your server.

**Q: Can the system be integrated with authentication?**
A: Yes, you can add authentication by modifying the Flask routes to check user login status before allowing access.

### Security Questions

**Q: How secure is this solution?**
A: It provides good protection against casual copying and unauthorized access. However, determined users with technical knowledge may find ways to bypass some protections.

**Q: Can users bypass the security measures?**
A: Some client-side protections can be bypassed by advanced users, but all bypass attempts are detected and logged.

**Q: Is this suitable for highly classified documents?**
A: This solution is best for internal business documents and moderate security needs. For highly classified documents, consider enterprise DRM solutions.

**Q: What about mobile devices?**
A: The system works on mobile devices but with limited security features. Mobile browsers have different capabilities than desktop browsers.

### Deployment Questions

**Q: Can this run on a cloud server?**
A: Yes, it can be deployed on AWS, Azure, Google Cloud, or any VPS with Python support.

**Q: What are the server requirements?**
A: Minimum: 1GB RAM, 1 CPU core. Recommended: 2GB+ RAM for handling multiple concurrent users and large files.

**Q: Can multiple users access files simultaneously?**
A: Yes, the system supports multiple concurrent users. Each user gets their own session with independent tracking.

**Q: How do I backup the activity logs?**
A: Copy the `activity_logs.json` file regularly, or implement database storage for automatic backups.

---

## 📞 Support

For additional support or customization requests:

1. **Check Logs**: Review `activity_logs.json` and browser console for error details
2. **Documentation**: Refer to `TECHNICAL_DOCUMENTATION.md` for advanced configuration
3. **Community**: Share issues and solutions with other users
4. **Professional Support**: Contact for custom implementations and enterprise features

Remember: This solution provides good protection for most use cases, but no software-only solution can prevent all forms of data theft. Use appropriate classification levels for your documents.
