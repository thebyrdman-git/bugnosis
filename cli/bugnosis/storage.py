"""Local storage for bugs and contributions."""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from .scanner import Bug


class BugDatabase:
    """Local database for tracked bugs and contributions."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            config_dir = Path.home() / '.config' / 'bugnosis'
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(config_dir / 'bugnosis.db')
            
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
    def _init_db(self):
        """Initialize database schema."""
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS bugs (
                id INTEGER PRIMARY KEY,
                repo TEXT NOT NULL,
                issue_number INTEGER NOT NULL,
                title TEXT,
                url TEXT,
                impact_score INTEGER,
                affected_users INTEGER,
                severity TEXT,
                labels TEXT,
                comments INTEGER,
                created_at TEXT,
                updated_at TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'discovered',
                UNIQUE(repo, issue_number)
            );
            
            CREATE TABLE IF NOT EXISTS contributions (
                id INTEGER PRIMARY KEY,
                repo TEXT NOT NULL,
                issue_number INTEGER,
                pr_number INTEGER,
                pr_url TEXT,
                impact_score INTEGER,
                affected_users INTEGER,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                merged_at TIMESTAMP,
                status TEXT DEFAULT 'submitted'
            );
            
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY,
                repo TEXT NOT NULL,
                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bugs_found INTEGER
            );
            
            CREATE INDEX IF NOT EXISTS idx_bugs_impact ON bugs(impact_score DESC);
            CREATE INDEX IF NOT EXISTS idx_bugs_status ON bugs(status);
            CREATE INDEX IF NOT EXISTS idx_contributions_status ON contributions(status);
            
            -- Migration to add columns if missing (safe if exists)
            -- SQLite doesn't support ADD COLUMN IF NOT EXISTS easily, so we rely on CREATE TABLE IF NOT EXISTS being sufficient
            -- for new dbs, and for old dbs we'd need a schema migration system.
            -- For now, we just ensure core columns.
        ''')
        
        # Quick hack to ensure new columns exist for existing DBs
        try:
            self.conn.execute("ALTER TABLE bugs ADD COLUMN labels TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            self.conn.execute("ALTER TABLE bugs ADD COLUMN comments INTEGER")
        except sqlite3.OperationalError:
            pass
        try:
            self.conn.execute("ALTER TABLE bugs ADD COLUMN created_at TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            self.conn.execute("ALTER TABLE bugs ADD COLUMN updated_at TEXT")
        except sqlite3.OperationalError:
            pass
            
        self.conn.commit()
        
    def save_bug(self, 
                repo: str, 
                issue_number: int, 
                title: str, 
                url: str, 
                impact_score: int, 
                affected_users: int, 
                severity: str,
                labels: Any = None,
                comments: int = 0,
                created_at: str = None,
                updated_at: str = None):
        """Save or update a bug with detailed fields."""
        
        # Convert list to JSON string if needed
        if isinstance(labels, list):
            labels_json = json.dumps(labels)
        else:
            labels_json = labels if labels else "[]"
            
        self.conn.execute('''
            INSERT OR REPLACE INTO bugs 
            (repo, issue_number, title, url, impact_score, affected_users, severity, labels, comments, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (repo, issue_number, title, url, impact_score, affected_users, severity, labels_json, comments, created_at, updated_at))
        self.conn.commit()
        
    def save_bugs(self, bugs: List[Bug]):
        """Save multiple bugs from Bug objects."""
        for bug in bugs:
            # Construct repo string (handle platform prefix if present)
            repo_str = f"{bug.platform}:{bug.repo}" if hasattr(bug, 'platform') and bug.platform != 'github' else bug.repo
            
            self.save_bug(
                repo=repo_str,
                issue_number=bug.issue_number,
                title=bug.title,
                url=bug.url,
                impact_score=bug.impact_score,
                affected_users=bug.affected_users,
                severity=bug.severity,
                labels=bug.labels,
                comments=bug.comments_count,
                created_at=bug.created_at.isoformat() if bug.created_at else None,
                updated_at=bug.updated_at.isoformat() if bug.updated_at else None
            )
            
    def get_bugs(self, min_impact: int = 0, status: str = None) -> List[Dict]:
        """Retrieve bugs from database."""
        query = 'SELECT * FROM bugs WHERE impact_score >= ?'
        params = [min_impact]
        
        if status:
            query += ' AND status = ?'
            params.append(status)
            
        query += ' ORDER BY impact_score DESC'
        
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    def search_bugs(self, repo_query: str, min_impact: int = 0) -> List[Dict]:
        """
        Search bugs in local database by repository name (partial match).
        Used for Offline Mode.
        """
        query = '''
            SELECT * FROM bugs 
            WHERE repo LIKE ? 
            AND impact_score >= ?
            ORDER BY impact_score DESC
        '''
        params = [f"%{repo_query}%", min_impact]
        
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    def record_contribution(self, repo: str, issue_number: int, 
                          pr_number: int, pr_url: str, 
                          impact_score: int, affected_users: int):
        """Record a contribution."""
        self.conn.execute('''
            INSERT INTO contributions
            (repo, issue_number, pr_number, pr_url, impact_score, affected_users)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (repo, issue_number, pr_number, pr_url, impact_score, affected_users))
        self.conn.commit()
        
    def get_stats(self) -> Dict:
        """Get contribution statistics."""
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total_contributions,
                SUM(affected_users) as total_users_helped,
                AVG(impact_score) as avg_impact_score,
                COUNT(CASE WHEN status = 'merged' THEN 1 END) as merged_count
            FROM contributions
        ''')
        row = cursor.fetchone()
        
        return {
            'total_contributions': row['total_contributions'] or 0,
            'total_users_helped': row['total_users_helped'] or 0,
            'avg_impact_score': int(row['avg_impact_score'] or 0),
            'merged_count': row['merged_count'] or 0,
        }
        
    def export_profile_json(self) -> str:
        """Export all user data (bugs and contributions) to JSON."""
        bugs = self.get_bugs(min_impact=0)
        
        cursor = self.conn.execute('SELECT * FROM contributions')
        contributions = [dict(row) for row in cursor.fetchall()]
        
        data = {
            'version': 1,
            'exported_at': datetime.now().isoformat(),
            'bugs': bugs,
            'contributions': contributions
        }
        return json.dumps(data, indent=2)

    def import_profile_json(self, json_str: str):
        """Import user data from JSON string (merge strategy)."""
        try:
            data = json.loads(json_str)
            
            # Import bugs
            for bug in data.get('bugs', []):
                self.conn.execute('''
                    INSERT OR IGNORE INTO bugs 
                    (repo, issue_number, title, url, impact_score, affected_users, severity, labels, comments, created_at, updated_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (bug['repo'], bug['issue_number'], bug['title'], bug['url'], 
                      bug['impact_score'], bug['affected_users'], bug['severity'], 
                      bug.get('labels'), bug.get('comments'), bug.get('created_at'), 
                      bug.get('updated_at'), bug.get('status')))
            
            # Import contributions
            for contrib in data.get('contributions', []):
                self.conn.execute('''
                    INSERT OR IGNORE INTO contributions
                    (repo, issue_number, pr_number, pr_url, impact_score, affected_users, submitted_at, merged_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (contrib['repo'], contrib['issue_number'], contrib['pr_number'], contrib['pr_url'],
                      contrib['impact_score'], contrib['affected_users'], contrib['submitted_at'],
                      contrib.get('merged_at'), contrib.get('status')))
                      
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Import error: {e}")
            return False

    def close(self):
        """Close database connection."""
        self.conn.close()
