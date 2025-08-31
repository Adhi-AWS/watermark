import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

class ActivityDatabase:
    def __init__(self, db_path: str = "activity_audit.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                activity TEXT NOT NULL,
                file_name TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                additional_info TEXT,
                created_date DATE NOT NULL,
                created_time TIME NOT NULL
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_name ON activities(file_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity ON activities(activity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_date ON activities(created_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON activities(session_id)')

        # Table for download tokens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_tokens (
                token TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                allowed_email TEXT,
                expires_at TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()
    
    def add_activity(self, timestamp: str, session_id: str, activity: str, 
                    file_name: str, ip_address: str = None, user_agent: str = None, 
                    additional_info: Dict = None):
        """Add a new activity to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Parse timestamp to get date and time
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        created_date = dt.date().isoformat()
        created_time = dt.time().isoformat()
        
        cursor.execute('''
            INSERT INTO activities 
            (timestamp, session_id, activity, file_name, ip_address, user_agent, additional_info, created_date, created_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, session_id, activity, file_name, ip_address, user_agent,
            json.dumps(additional_info) if additional_info else None,
            created_date, created_time
        ))
        
        conn.commit()
        conn.close()
    
    def get_activities(self, file_name: str = None, start_date: str = None, 
                      end_date: str = None, activity_type: str = None, 
                      session_id: str = None, limit: int = 1000) -> List[Dict]:
        """Get activities with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM activities WHERE 1=1"
        params = []
        
        if file_name:
            query += " AND file_name LIKE ?"
            params.append(f"%{file_name}%")
        
        if start_date:
            query += " AND created_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND created_date <= ?"
            params.append(end_date)
        
        if activity_type:
            query += " AND activity LIKE ?"
            params.append(f"%{activity_type}%")
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        
        activities = []
        for row in cursor.fetchall():
            activity = dict(zip(columns, row))
            if activity['additional_info']:
                activity['additional_info'] = json.loads(activity['additional_info'])
            activities.append(activity)
        
        conn.close()
        return activities
    
    def get_file_names(self) -> List[str]:
        """Get unique file names from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT file_name FROM activities ORDER BY file_name")
        file_names = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return file_names
    
    def get_activity_types(self) -> List[str]:
        """Get unique activity types from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT activity FROM activities ORDER BY activity")
        activities = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return activities
    
    def get_statistics(self, start_date: str = None, end_date: str = None) -> Dict:
        """Get activity statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_filter = ""
        params = []
        
        if start_date:
            date_filter += " AND created_date >= ?"
            params.append(start_date)
        
        if end_date:
            date_filter += " AND created_date <= ?"
            params.append(end_date)
        
        # Total activities
        cursor.execute(f"SELECT COUNT(*) FROM activities WHERE 1=1{date_filter}", params)
        total_activities = cursor.fetchone()[0]
        
        # Unique sessions
        cursor.execute(f"SELECT COUNT(DISTINCT session_id) FROM activities WHERE 1=1{date_filter}", params)
        unique_sessions = cursor.fetchone()[0]
        
        # File opens
        cursor.execute(f"SELECT COUNT(*) FROM activities WHERE activity LIKE '%OPENED%'{date_filter}", params)
        file_opens = cursor.fetchone()[0]
        
        # Downloads
        cursor.execute(f"SELECT COUNT(*) FROM activities WHERE activity LIKE '%DOWNLOAD%'{date_filter}", params)
        downloads = cursor.fetchone()[0]
        
        # Prints
        cursor.execute(f"SELECT COUNT(*) FROM activities WHERE activity LIKE '%PRINT%'{date_filter}", params)
        prints = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_activities': total_activities,
            'unique_sessions': unique_sessions,
            'file_opens': file_opens,
            'downloads': downloads,
            'prints': prints
        }

    def create_download_token(self, file_name: str, allowed_email: str = None,
                               expire_minutes: int = 10) -> str:
        """Create a download token with expiration"""
        token = uuid.uuid4().hex
        expires_at = (datetime.now() + timedelta(minutes=expire_minutes)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO download_tokens (token, file_name, allowed_email, expires_at) VALUES (?, ?, ?, ?)",
            (token, file_name, allowed_email, expires_at)
        )
        conn.commit()
        conn.close()
        return token

    def validate_download_token(self, token: str, file_name: str,
                                user_email: str = None) -> bool:
        """Validate token against database and expiration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT allowed_email, expires_at FROM download_tokens WHERE token = ? AND file_name = ?",
            (token, file_name)
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return False
        allowed_email, expires_at = row
        if datetime.fromisoformat(expires_at) < datetime.now():
            return False
        if allowed_email:
            if not user_email or allowed_email.lower() != user_email.lower():
                return False
        return True

    def revoke_download_token(self, token: str):
        """Revoke a token after use"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM download_tokens WHERE token = ?", (token,))
        conn.commit()
        conn.close()

    def migrate_json_logs(self, json_file_path: str):
        """Migrate existing JSON logs to database"""
        if not os.path.exists(json_file_path):
            return
        
        try:
            with open(json_file_path, 'r') as f:
                logs = json.load(f)
            
            for log in logs:
                self.add_activity(
                    timestamp=log.get('timestamp'),
                    session_id=log.get('session_id'),
                    activity=log.get('activity'),
                    file_name=log.get('file_name'),
                    ip_address=log.get('ip_address'),
                    user_agent=log.get('user_agent'),
                    additional_info=log.get('additional_info')
                )
        except Exception as e:
            print(f"Error migrating logs: {e}")
