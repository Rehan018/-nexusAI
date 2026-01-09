"""
Activity Logger - Track all outreach activities and prevent duplicates
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import config


class ActivityLogger:
    """Log and track all LinkedIn outreach activities"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize activity logger
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or config.DATABASE_PATH
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables if not exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                profile_url TEXT UNIQUE NOT NULL,
                name TEXT,
                role TEXT,
                connection_status TEXT,
                action_type TEXT,
                message_sent TEXT,
                timestamp TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_duplicate(self, profile_url: str, action_type: str = None) -> bool:
        """
        Check if we've already performed this specific action on this profile
        
        Args:
            profile_url: LinkedIn profile URL
            action_type: Specific action to check (e.g., 'message', 'connection_request')
                         If None, checks if ANY action was taken.
        
        Returns:
            True if action already taken
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if action_type:
            cursor.execute(
                'SELECT COUNT(*) FROM outreach_log WHERE profile_url = ? AND action_type = ?',
                (profile_url, action_type)
            )
        else:
            cursor.execute(
                'SELECT COUNT(*) FROM outreach_log WHERE profile_url = ?',
                (profile_url,)
            )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def log_action(
        self,
        company: str,
        profile_url: str,
        name: str,
        role: str,
        connection_status: str,
        action_type: str,
        message_sent: str,
        status: str = "success"
    ):
        """
        Log an outreach action
        
        Args:
            company: Company name
            profile_url: LinkedIn profile URL
            name: Person's name
            role: Person's role/title
            connection_status: 'connected' or 'not_connected'
            action_type: 'connection_request' or 'message'
            message_sent: The actual message/note sent
            status: 'success', 'failed', or 'skipped'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO outreach_log 
                (company, profile_url, name, role, connection_status, 
                 action_type, message_sent, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company, profile_url, name, role, connection_status,
                  action_type, message_sent, timestamp, status))
            
            conn.commit()
            if status == 'failed':
                 print(f"❌ Logged FAILURE: {action_type} for {name} at {company}")
            else:
                 print(f"✅ Logged action: {action_type} for {name} at {company}")
        
        except sqlite3.IntegrityError:
            print(f"⚠️  Duplicate entry detected for {profile_url}")
        
        finally:
            conn.close()
    
    def get_company_stats(self, company: str) -> Dict:
        """
        Get statistics for a specific company
        
        Args:
            company: Company name
        
        Returns:
            Dictionary with stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN action_type = 'connection_request' THEN 1 ELSE 0 END) as connections,
                SUM(CASE WHEN action_type = 'message' THEN 1 ELSE 0 END) as messages
            FROM outreach_log
            WHERE company = ?
        ''', (company,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_contacted': result[0],
            'connections_sent': result[1],
            'messages_sent': result[2]
        }
    
    def get_all_logs(self) -> List[Dict]:
        """
        Get all logged activities
        
        Returns:
            List of all log entries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM outreach_log ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def export_to_csv(self, csv_path: str = None):
        """
        Export logs to CSV file
        
        Args:
            csv_path: Path to CSV file
        """
        csv_path = csv_path or config.LOG_CSV_PATH
        
        logs = self.get_all_logs()
        if logs:
            df = pd.DataFrame(logs)
            df.to_csv(csv_path, index=False)
            print(f"📄 Exported {len(logs)} log entries to {csv_path}")
        else:
            print("ℹ️  No logs to export")
    
    def get_summary(self) -> Dict:
        """
        Get overall summary statistics
        
        Returns:
            Summary statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT company) as companies,
                SUM(CASE WHEN action_type = 'connection_request' THEN 1 ELSE 0 END) as connections,
                SUM(CASE WHEN action_type = 'message' THEN 1 ELSE 0 END) as messages,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM outreach_log
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_actions': result[0],
            'companies_contacted': result[1],
            'connections_sent': result[2],
            'messages_sent': result[3],
            'successful_actions': result[4],
            'failed_actions': result[5]
        }
