"""GitLab platform integration."""

import os
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import BugPlatform, Bug


class GitLabPlatform(BugPlatform):
    """GitLab bug tracking platform."""
    
    def __init__(self, api_token: Optional[str] = None, instance_url: str = "https://gitlab.com"):
        """
        Initialize GitLab platform.
        
        Args:
            api_token: GitLab personal access token
            instance_url: GitLab instance URL (default: gitlab.com)
        """
        super().__init__(api_token or os.getenv('GITLAB_TOKEN'))
        self.instance_url = instance_url.rstrip('/')
        self.api_base = f"{self.instance_url}/api/v4"
    
    @property
    def name(self) -> str:
        return "gitlab"
    
    def search_bugs(self,
                   project: str,
                   min_impact: int = 70,
                   labels: Optional[List[str]] = None,
                   severity: Optional[str] = None) -> List[Bug]:
        """Search GitLab issues."""
        # Encode project path for URL
        project_encoded = project.replace('/', '%2F')
        
        # Build API request
        url = f"{self.api_base}/projects/{project_encoded}/issues"
        headers = {}
        if self.api_token:
            headers['PRIVATE-TOKEN'] = self.api_token
        
        params = {
            'state': 'opened',
            'per_page': 100,
            'order_by': 'updated_at',
            'sort': 'desc'
        }
        
        if labels:
            params['labels'] = ','.join(labels)
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            issues = response.json()
        except Exception as e:
            print(f"Error fetching GitLab issues: {e}")
            return []
        
        # Convert to Bug objects and filter by impact
        bugs = []
        for issue in issues:
            impact = self.calculate_impact(issue)
            if impact < min_impact:
                continue
            
            bug = Bug(
                platform="gitlab",
                repo=project,
                issue_number=issue['iid'],
                title=issue['title'],
                url=issue['web_url'],
                description=issue.get('description', ''),
                impact_score=impact,
                affected_users=self.estimate_affected_users(issue),
                severity=self._determine_severity(issue),
                status=issue['state'],
                labels=issue.get('labels', []),
                created_at=datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(issue['updated_at'].replace('Z', '+00:00')),
                comments_count=issue.get('user_notes_count', 0),
                raw_data=issue
            )
            bugs.append(bug)
        
        # Sort by impact
        bugs.sort(key=lambda x: x.impact_score, reverse=True)
        return bugs
    
    def get_bug(self, project: str, bug_id: int) -> Optional[Bug]:
        """Get a specific GitLab issue."""
        project_encoded = project.replace('/', '%2F')
        url = f"{self.api_base}/projects/{project_encoded}/issues/{bug_id}"
        
        headers = {}
        if self.api_token:
            headers['PRIVATE-TOKEN'] = self.api_token
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            issue = response.json()
        except Exception as e:
            print(f"Error fetching GitLab issue: {e}")
            return None
        
        return Bug(
            platform="gitlab",
            repo=project,
            issue_number=issue['iid'],
            title=issue['title'],
            url=issue['web_url'],
            description=issue.get('description', ''),
            impact_score=self.calculate_impact(issue),
            affected_users=self.estimate_affected_users(issue),
            severity=self._determine_severity(issue),
            status=issue['state'],
            labels=issue.get('labels', []),
            created_at=datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(issue['updated_at'].replace('Z', '+00:00')),
            comments_count=issue.get('user_notes_count', 0),
            raw_data=issue
        )
    
    def calculate_impact(self, bug_data: Dict[str, Any]) -> int:
        """
        Calculate impact score for GitLab issue.
        
        Based on:
        - Upvotes (similar to GitHub reactions)
        - Comments
        - Labels (severity indicators)
        - Time open
        """
        score = 0
        
        # Upvotes (0-30 points)
        upvotes = bug_data.get('upvotes', 0)
        score += min(upvotes * 3, 30)
        
        # Comments (0-20 points)
        comments = bug_data.get('user_notes_count', 0)
        score += min(comments * 2, 20)
        
        # Labels (0-30 points)
        labels = [l.lower() for l in bug_data.get('labels', [])]
        if any(x in labels for x in ['critical', 'blocker', 'security']):
            score += 30
        elif any(x in labels for x in ['bug', 'high', 'important']):
            score += 20
        elif 'medium' in labels:
            score += 10
        
        # Time open (0-20 points)
        created = datetime.fromisoformat(bug_data['created_at'].replace('Z', '+00:00'))
        days_old = (datetime.now(created.tzinfo) - created).days
        if days_old > 90:
            score += 20
        elif days_old > 30:
            score += 10
        
        return min(score, 100)
    
    def estimate_affected_users(self, bug_data: Dict[str, Any]) -> int:
        """
        Estimate affected users for GitLab issue.
        
        Based on project popularity and issue engagement.
        """
        # Fetch project stats if possible
        upvotes = bug_data.get('upvotes', 0)
        comments = bug_data.get('user_notes_count', 0)
        
        # Rough estimation
        base = upvotes * 100 + comments * 50
        
        # Boost for certain labels
        labels = [l.lower() for l in bug_data.get('labels', [])]
        if any(x in labels for x in ['critical', 'blocker']):
            base *= 5
        elif 'security' in labels:
            base *= 3
        
        return max(base, 10)  # Minimum 10 users
    
    def _determine_severity(self, issue: Dict[str, Any]) -> str:
        """Determine severity from labels."""
        labels = [l.lower() for l in issue.get('labels', [])]
        
        if any(x in labels for x in ['critical', 'blocker', 'security']):
            return 'critical'
        elif any(x in labels for x in ['high', 'important']):
            return 'high'
        elif 'medium' in labels:
            return 'medium'
        else:
            return 'low'



