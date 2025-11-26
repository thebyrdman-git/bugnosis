"""Local storage for bugs and contributions."""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
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
        ''')
        self.conn.commit()
        
    def save_bug(self, bug: Bug):
        """Save or update a bug."""
        self.conn.execute('''
            INSERT OR REPLACE INTO bugs 
            (repo, issue_number, title, url, impact_score, affected_users, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (bug.repo, bug.issue_number, bug.title, bug.url, 
              bug.impact_score, bug.affected_users, bug.severity))
        self.conn.commit()
        
    def save_bugs(self, bugs: List[Bug]):
        """Save multiple bugs."""
        for bug in bugs:
            self.save_bug(bug)
            
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
        
    def close(self):
        """Close database connection."""
        self.conn.close()

