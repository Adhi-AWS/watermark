# Secure Excel Viewer - Deployment & Production Guide

## 🎯 Deployment Overview

This guide covers deploying the Secure Excel Viewer from development to production environments, including security hardening, performance optimization, and maintenance procedures.

## 🏗️ Production Architecture

### Recommended Production Setup
```
[Load Balancer] → [Web Server (Nginx)] → [Application Server (Gunicorn)] → [Database (PostgreSQL)]
                                       ↓
                              [File Storage (NFS/S3)]
                                       ↓
                              [Log Management (ELK Stack)]
```

### Infrastructure Components

#### Web Server Layer
- **Nginx**: Reverse proxy and static file serving
- **SSL/TLS**: Certificate management and encryption
- **Rate Limiting**: DDoS protection and traffic control

#### Application Layer
- **Gunicorn**: WSGI HTTP Server for Python
- **Multiple Workers**: Concurrent request handling
- **Health Checks**: Monitoring and auto-restart

#### Database Layer
- **PostgreSQL**: Production-grade database
- **Connection Pooling**: Efficient database connections
- **Backup Strategy**: Automated backups and recovery

#### Storage Layer
- **Secure File Storage**: Encrypted file storage
- **Log Management**: Centralized logging and analytics
- **Monitoring**: System and application monitoring

## 🚀 Production Deployment Steps

### Step 1: Server Preparation

#### System Requirements
```bash
# Minimum Production Requirements
CPU: 2 cores
RAM: 4GB
Storage: 50GB SSD
Network: 100Mbps
OS: Ubuntu 20.04 LTS / CentOS 8 / Amazon Linux 2
```

#### Initial Server Setup
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3.9 python3.9-venv python3-pip nginx postgresql postgresql-contrib supervisor

# Create application user
sudo useradd -m -s /bin/bash secureviewer
sudo usermod -aG sudo secureviewer

# Create application directory
sudo mkdir -p /var/www/secure-excel-viewer
sudo chown secureviewer:secureviewer /var/www/secure-excel-viewer
```

### Step 2: Application Setup

#### Create Production Environment
```bash
# Switch to application user
sudo su - secureviewer

# Create virtual environment
cd /var/www/secure-excel-viewer
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

#### Production Requirements File
```text
# requirements-production.txt
Flask==2.3.3
pandas==2.1.1
openpyxl==3.1.2
flask-cors==4.0.0
xlsxwriter==3.1.9
gunicorn==21.2.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
redis==4.6.0
celery==5.3.1
```

### Step 3: Database Configuration

#### PostgreSQL Setup
```bash
# Switch to postgres user
sudo su - postgres

# Create database and user
createdb secure_excel_viewer
createuser --interactive secureviewer
psql -c "ALTER USER secureviewer WITH PASSWORD 'your_secure_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE secure_excel_viewer TO secureviewer;"
```

#### Database Schema
```sql
-- Create tables for production
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW()
);

CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    upload_date TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP
);

CREATE TABLE activity_logs (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    file_id INTEGER REFERENCES files(id),
    activity_type VARCHAR(100) NOT NULL,
    additional_info JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_activity_logs_session_id ON activity_logs(session_id);
CREATE INDEX idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX idx_activity_logs_activity_type ON activity_logs(activity_type);
```

### Step 4: Application Configuration

#### Production Configuration File
```python
# config.py
import os
from datetime import timedelta

class ProductionConfig:
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-production-secret-key'
    DEBUG = False
    TESTING = False
    
    # Database Settings
    DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://secureviewer:password@localhost/secure_excel_viewer'
    
    # Security Settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # File Settings
    EXCEL_FILES_DIR = '/var/www/secure-excel-viewer/secure_files'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/secure-excel-viewer/app.log'
    
    # Redis (for session storage)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
```

#### Environment Variables
```bash
# Create .env file
cat > /var/www/secure-excel-viewer/.env << EOF
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=postgresql://secureviewer:password@localhost/secure_excel_viewer
REDIS_URL=redis://localhost:6379/0
EOF

# Secure the environment file
chmod 600 /var/www/secure-excel-viewer/.env
```

### Step 5: Web Server Configuration

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/secure-excel-viewer
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data:;" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    location /static {
        alias /var/www/secure-excel-viewer/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Enable Nginx Site
```bash
sudo ln -s /etc/nginx/sites-available/secure-excel-viewer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: SSL Certificate Setup

#### Let's Encrypt Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### Step 7: Application Server Configuration

#### Gunicorn Configuration
```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 300
keepalive = 2
user = "secureviewer"
group = "secureviewer"
tmp_upload_dir = "/tmp"
errorlog = "/var/log/secure-excel-viewer/gunicorn_error.log"
accesslog = "/var/log/secure-excel-viewer/gunicorn_access.log"
loglevel = "info"
```

#### Systemd Service Configuration
```ini
# /etc/systemd/system/secure-excel-viewer.service
[Unit]
Description=Secure Excel Viewer Gunicorn Application
After=network.target

[Service]
Type=exec
User=secureviewer
Group=secureviewer
WorkingDirectory=/var/www/secure-excel-viewer
Environment="PATH=/var/www/secure-excel-viewer/venv/bin"
ExecStart=/var/www/secure-excel-viewer/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### Start Services
```bash
# Create log directory
sudo mkdir -p /var/log/secure-excel-viewer
sudo chown secureviewer:secureviewer /var/log/secure-excel-viewer

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable secure-excel-viewer
sudo systemctl start secure-excel-viewer
sudo systemctl status secure-excel-viewer
```

## 🔒 Security Hardening

### System Security

#### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

#### Fail2Ban Configuration
```bash
# Install and configure Fail2Ban
sudo apt install fail2ban

# Create custom jail
sudo cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl restart fail2ban
```

### Application Security

#### Enhanced Flask Security
```python
# security.py
from flask import Flask, request, abort
from functools import wraps
import time
import hashlib

class SecurityManager:
    def __init__(self, app):
        self.app = app
        self.request_counts = {}
        self.blocked_ips = set()
    
    def rate_limit(self, max_requests=100, window=3600):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                current_time = int(time.time())
                window_start = current_time - window
                
                # Clean old entries
                self.request_counts = {
                    ip: [(timestamp, count) for timestamp, count in requests 
                         if timestamp > window_start]
                    for ip, requests in self.request_counts.items()
                }
                
                # Count requests for this IP
                if client_ip not in self.request_counts:
                    self.request_counts[client_ip] = []
                
                request_count = sum(count for _, count in self.request_counts[client_ip])
                
                if request_count >= max_requests:
                    self.blocked_ips.add(client_ip)
                    abort(429)  # Too Many Requests
                
                # Add this request
                self.request_counts[client_ip].append((current_time, 1))
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def check_blocked_ip(self):
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        if client_ip in self.blocked_ips:
            abort(403)
```

#### Content Security Policy
```python
# Enhanced CSP in app.py
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## 📊 Monitoring & Logging

### Application Monitoring

#### Health Check Endpoint
```python
# Add to app.py
@app.route('/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check file system
        if not os.path.exists(EXCEL_FILES_DIR):
            raise Exception("File directory not accessible")
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503
```

#### Structured Logging
```python
# logging_config.py
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_ip'):
            log_entry['user_ip'] = record.user_ip
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
            
        return json.dumps(log_entry)

def setup_logging(app):
    handler = logging.FileHandler('/var/log/secure-excel-viewer/app.log')
    handler.setFormatter(StructuredFormatter())
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
```

### System Monitoring

#### Prometheus Metrics
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Response

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_SESSIONS = Gauge('active_sessions_total', 'Number of active sessions')
FILE_ACCESS_COUNT = Counter('file_access_total', 'Total file accesses', ['filename'])

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

@app.before_request
def before_request():
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_duration = time.time() - request.start_time
    REQUEST_DURATION.observe(request_duration)
    return response
```

#### Log Management with ELK Stack
```yaml
# docker-compose.elk.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.2
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    
  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.2
    ports:
      - "5044:5044"
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    
  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.2
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

## 🔄 Backup & Recovery

### Database Backup Strategy
```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/var/backups/secure-excel-viewer"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump -h localhost -U secureviewer secure_excel_viewer > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_FILE.gz s3://your-backup-bucket/
```

### File Backup Strategy
```bash
#!/bin/bash
# backup_files.sh

SOURCE_DIR="/var/www/secure-excel-viewer/secure_files"
BACKUP_DIR="/var/backups/secure-excel-viewer/files"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup with rsync
rsync -avz --delete $SOURCE_DIR/ $BACKUP_DIR/current/

# Create dated snapshot
cp -al $BACKUP_DIR/current/ $BACKUP_DIR/$DATE/

# Remove snapshots older than 7 days
find $BACKUP_DIR -maxdepth 1 -name "20*" -mtime +7 -exec rm -rf {} \;
```

### Automated Backup Cron Jobs
```bash
# Add to crontab (sudo crontab -e)
# Database backup every 6 hours
0 */6 * * * /usr/local/bin/backup_database.sh

# File backup every hour
0 * * * * /usr/local/bin/backup_files.sh

# Log rotation daily
0 2 * * * /usr/sbin/logrotate /etc/logrotate.d/secure-excel-viewer
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Performance tuning queries
-- Analyze table statistics
ANALYZE activity_logs;
ANALYZE sessions;
ANALYZE files;

-- Create additional indexes based on usage patterns
CREATE INDEX idx_activity_logs_composite ON activity_logs(file_id, activity_type, timestamp);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX idx_files_last_accessed ON files(last_accessed);

-- Partition large tables by date
CREATE TABLE activity_logs_2025_q1 PARTITION OF activity_logs
FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
```

### Application Optimization
```python
# Caching configuration
from flask_caching import Cache

cache_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/1',
    'CACHE_DEFAULT_TIMEOUT': 300
}

cache = Cache()
cache.init_app(app, config=cache_config)

# Cache file processing results
@cache.memoize(timeout=3600)
def process_excel_file(filename, file_mtime):
    # Process and return HTML
    pass

# Async task processing with Celery
from celery import Celery

celery = Celery(app.name, broker='redis://localhost:6379/2')

@celery.task
def process_large_file_async(filename):
    # Process large files in background
    pass
```

### Static File Optimization
```nginx
# Nginx configuration for static files
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary Accept-Encoding;
    gzip_static on;
}

# Enable gzip compression
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

## 🚨 Incident Response

### Monitoring Alerts
```bash
# Basic alert script
#!/bin/bash
# check_service.sh

SERVICE="secure-excel-viewer"
EMAIL="admin@yourcompany.com"

if ! systemctl is-active --quiet $SERVICE; then
    echo "Service $SERVICE is down!" | mail -s "ALERT: Service Down" $EMAIL
    systemctl restart $SERVICE
fi

# Check disk usage
DISK_USAGE=$(df /var/www/secure-excel-viewer | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is $DISK_USAGE%" | mail -s "ALERT: High Disk Usage" $EMAIL
fi
```

### Security Incident Response
```python
# Security incident handler
def handle_security_incident(event_type, session_id, details):
    incident = {
        'timestamp': datetime.now().isoformat(),
        'type': event_type,
        'session_id': session_id,
        'details': details,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    }
    
    # Log to security log
    security_logger.warning(f"Security incident: {incident}")
    
    # Send alert if high severity
    if event_type in ['MULTIPLE_VIOLATIONS', 'POSSIBLE_AUTOMATION']:
        send_security_alert(incident)
    
    # Auto-block if necessary
    if should_auto_block(event_type, session_id):
        block_session(session_id)
```

This comprehensive deployment guide ensures a secure, scalable, and maintainable production environment for the Secure Excel Viewer system.
