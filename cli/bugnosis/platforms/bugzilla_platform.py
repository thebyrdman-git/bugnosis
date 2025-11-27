"""Bugzilla platform integration."""

import os
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import BugPlatform, Bug


class BugzillaPlatform(BugPlatform):
    """Bugzilla bug tracking platform."""
    
    # Popular Bugzilla instances
    INSTANCES = {
        'mozilla': 'https://bugzilla.mozilla.org',
        'redhat': 'https://bugzilla.redhat.com',
        'kde': 'https://bugs.kde.org',
        'gnome': 'https://bugzilla.gnome.org',
        'kernel': 'https://bugzilla.kernel.org',
    }
    
    def __init__(self, api_token: Optional[str] = None, instance: str = "mozilla"):
        """
        Initialize Bugzilla platform.
        
        Args:
            api_token: Bugzilla API key
            instance: Instance name (mozilla, redhat, kde, gnome) or URL
        """
        super().__init__(api_token or os.getenv('BUGZILLA_TOKEN'))
        
        # Determine instance URL
        if instance in self.INSTANCES:
            self.instance_url = self.INSTANCES[instance]
            self.instance_name = instance
        elif instance.startswith('http'):
            self.instance_url = instance.rstrip('/')
            self.instance_name = 'custom'
        else:
            raise ValueError(f"Unknown Bugzilla instance: {instance}")
        
        self.api_base = f"{self.instance_url}/rest"
    
    @property
    def name(self) -> str:
        return f"bugzilla-{self.instance_name}"
    
    def search_bugs(self,
                   project: str,
                   min_impact: int = 70,
                   labels: Optional[List[str]] = None,
                   severity: Optional[str] = None) -> List[Bug]:
        """
        Search Bugzilla bugs.
        
        Args:
            project: Product name in Bugzilla
        """
        url = f"{self.api_base}/bug"
        
        params = {
            'product': project,
            'status': ['NEW', 'ASSIGNED', 'REOPENED'],
            'limit': 100,
        }
        
        if severity:
            params['severity'] = severity
        
        headers = {}
        if self.api_token:
            headers['X-BUGZILLA-API-KEY'] = self.api_token
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            bugs_data = data.get('bugs', [])
        except Exception as e:
            print(f"Error fetching Bugzilla bugs: {e}")
            return []
        
        # Convert to Bug objects and filter by impact
        bugs = []
        for bug_data in bugs_data:
            impact = self.calculate_impact(bug_data)
            if impact < min_impact:
                continue
            
            bug = Bug(
                platform=self.name,
                repo=project,
                issue_number=bug_data['id'],
                title=bug_data['summary'],
                url=f"{self.instance_url}/show_bug.cgi?id={bug_data['id']}",
                description=bug_data.get('description', ''),
                impact_score=impact,
                affected_users=self.estimate_affected_users(bug_data),
                severity=bug_data.get('severity', 'normal'),
                status=bug_data['status'],
                labels=bug_data.get('keywords', []),
                created_at=datetime.fromisoformat(bug_data['creation_time'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(bug_data['last_change_time'].replace('Z', '+00:00')),
                comments_count=bug_data.get('comment_count', 0),
                raw_data=bug_data
            )
            bugs.append(bug)
        
        # Sort by impact
        bugs.sort(key=lambda x: x.impact_score, reverse=True)
        return bugs
    
    def get_bug(self, project: str, bug_id: int) -> Optional[Bug]:
        """Get a specific Bugzilla bug."""
        url = f"{self.api_base}/bug/{bug_id}"
        
        headers = {}
        if self.api_token:
            headers['X-BUGZILLA-API-KEY'] = self.api_token
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            bug_data = data['bugs'][0]
        except Exception as e:
            print(f"Error fetching Bugzilla bug: {e}")
            return None
        
        return Bug(
            platform=self.name,
            repo=bug_data['product'],
            issue_number=bug_data['id'],
            title=bug_data['summary'],
            url=f"{self.instance_url}/show_bug.cgi?id={bug_data['id']}",
            description=bug_data.get('description', ''),
            impact_score=self.calculate_impact(bug_data),
            affected_users=self.estimate_affected_users(bug_data),
            severity=bug_data.get('severity', 'normal'),
            status=bug_data['status'],
            labels=bug_data.get('keywords', []),
            created_at=datetime.fromisoformat(bug_data['creation_time'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(bug_data['last_change_time'].replace('Z', '+00:00')),
            comments_count=bug_data.get('comment_count', 0),
            raw_data=bug_data
        )
    
    def calculate_impact(self, bug_data: Dict[str, Any]) -> int:
        """
        Calculate impact score for Bugzilla bug.
        
        Bugzilla has explicit severity and priority fields.
        """
        score = 0
        
        # Severity (0-40 points)
        severity = bug_data.get('severity', 'normal').lower()
        severity_scores = {
            'blocker': 40,
            'critical': 35,
            's1': 40,  # Mozilla
            'major': 25,
            's2': 25,  # Mozilla
            'normal': 15,
            's3': 15,  # Mozilla
            'minor': 5,
            's4': 5,   # Mozilla
            'trivial': 0,
        }
        score += severity_scores.get(severity, 15)
        
        # Priority (0-30 points)
        priority = bug_data.get('priority', '').lower()
        if 'p1' in priority or 'high' in priority:
            score += 30
        elif 'p2' in priority or 'medium' in priority:
            score += 15
        elif 'p3' in priority or 'low' in priority:
            score += 5
        
        # Comments (0-20 points)
        comments = bug_data.get('comment_count', 0)
        score += min(comments * 2, 20)
        
        # Time open (0-10 points)
        created = datetime.fromisoformat(bug_data['creation_time'].replace('Z', '+00:00'))
        days_old = (datetime.now(created.tzinfo) - created).days
        if days_old > 90:
            score += 10
        elif days_old > 30:
            score += 5
        
        return min(score, 100)
    
    def estimate_affected_users(self, bug_data: Dict[str, Any]) -> int:
        """Estimate affected users for Bugzilla bug."""
        # Bugzilla often has vote counts
        votes = bug_data.get('votes', 0)
        cc_count = len(bug_data.get('cc', []))
        comments = bug_data.get('comment_count', 0)
        
        # Estimation
        base = votes * 500 + cc_count * 100 + comments * 50
        
        # Boost for severity
        severity = bug_data.get('severity', 'normal').lower()
        if severity in ['blocker', 'critical']:
            base *= 10
        elif severity == 'major':
            base *= 3
        
        return max(base, 10)



