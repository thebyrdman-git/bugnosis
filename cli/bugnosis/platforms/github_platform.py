"""GitHub platform integration."""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from .base import BugPlatform, Bug
from ..github import GitHubClient


class GitHubPlatform(BugPlatform):
    """GitHub bug tracking platform."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize GitHub platform."""
        super().__init__(api_token or os.getenv('GITHUB_TOKEN'))
        self.client = GitHubClient(token=self.api_token)
    
    @property
    def name(self) -> str:
        return "github"
    
    def search_bugs(self,
                   project: str,
                   min_impact: int = 70,
                   labels: Optional[List[str]] = None,
                   severity: Optional[str] = None,
                   mode: str = "normal") -> List[Bug]:
        """Search GitHub issues."""
        from ..scanner import ImpactScorer
        
        # Get repo stats
        repo_url = f'https://api.github.com/repos/{project}'
        repo_resp = self.client.session.get(repo_url)
        if repo_resp.status_code != 200:
            print(f"Error fetching repo {project}: {repo_resp.status_code}")
            return []
        repo_stats = repo_resp.json()
        
        # Search params
        issues_url = f'https://api.github.com/repos/{project}/issues'
        params = {
            'state': 'open',
            # 'labels': 'bug',
            'sort': 'comments',
            'direction': 'desc',
            'per_page': 30
        }
        
        # Apply novice mode filters
        if mode == "novice":
            # In novice mode, prioritize finding labeled easy issues
            # We try multiple common labels
            params['labels'] = 'good first issue'
            params['sort'] = 'updated' # Fresh easy issues are better
            
            # Note: GitHub API only allows one label param at a time effectively in this format
            # A better approach would be to try a few calls or use search API
            # But for now, 'good first issue' is the gold standard.
        
        resp = self.client.session.get(issues_url, params=params)
        if resp.status_code != 200:
            print(f"Error fetching issues: {resp.status_code}")
            return []
            
        issues = resp.json()
        bugs = []
        
        for issue in issues:
            if 'pull_request' in issue:
                continue
                
            impact = ImpactScorer.calculate(issue, repo_stats, mode=mode)
            
            if impact >= min_impact:
                bug = Bug(
                    platform="github",
                    repo=project,
                    issue_number=issue['number'],
                    title=issue['title'],
                    url=issue['html_url'],
                    description=issue.get('body', '') or '',
                    impact_score=impact,
                    affected_users=self._estimate_users_logic(repo_stats, impact),
                    severity=self._determine_severity(issue),
                    status=issue['state'],
                    labels=[l['name'] for l in issue.get('labels', [])],
                    created_at=datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00')) if issue.get('created_at') else None,
                    updated_at=datetime.fromisoformat(issue['updated_at'].replace('Z', '+00:00')) if issue.get('updated_at') else None,
                    comments_count=issue.get('comments', 0),
                    raw_data=issue
                )
                bugs.append(bug)
        
        bugs.sort(key=lambda x: x.impact_score, reverse=True)
        return bugs
    
    def get_bug(self, project: str, bug_id: int) -> Optional[Bug]:
        """Get a specific GitHub issue."""
        from ..scanner import ImpactScorer
        
        issue = self.client.get_issue(project, bug_id)
        if not issue:
            return None
            
        # Need repo stats for accurate impact
        repo_url = f'https://api.github.com/repos/{project}'
        repo_resp = self.client.session.get(repo_url)
        repo_stats = repo_resp.json() if repo_resp.status_code == 200 else {}
        
        impact = ImpactScorer.calculate(issue, repo_stats)
        affected = self._estimate_users_logic(repo_stats, impact)
        
        return Bug(
            platform="github",
            repo=project,
            issue_number=bug_id,
            title=issue['title'],
            url=issue['html_url'],
            description=issue.get('body', '') or '',
            impact_score=impact,
            affected_users=affected,
            severity=self._determine_severity(issue),
            status=issue['state'],
            labels=[label['name'] for label in issue.get('labels', [])],
            created_at=datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(issue['updated_at'].replace('Z', '+00:00')),
            comments_count=issue.get('comments', 0),
            raw_data=issue
        )
    
    def calculate_impact(self, bug_data: Dict[str, Any]) -> int:
        """Calculate GitHub issue impact."""
        # Placeholder - requires repo_stats which this signature doesn't have
        return 50
    
    def estimate_affected_users(self, bug_data: Dict[str, Any]) -> int:
        """Estimate affected users for GitHub issue."""
        return 1000

    def _estimate_users_logic(self, repo_stats: Dict, impact_score: int) -> int:
        """Internal logic to estimate users."""
        stars = repo_stats.get('stargazers_count', 0)
        base_users = int(stars * 0.15)
        
        if impact_score >= 90:
            return int(base_users * 0.8)
        elif impact_score >= 80:
            return int(base_users * 0.5)
        elif impact_score >= 70:
            return int(base_users * 0.3)
        else:
            return int(base_users * 0.1)
    
    def _determine_severity(self, issue: Dict[str, Any]) -> str:
        """Determine severity from labels."""
        labels = [label['name'].lower() for label in issue.get('labels', [])]
        
        if any(x in labels for x in ['critical', 'blocker', 'p0']):
            return 'critical'
        elif any(x in labels for x in ['high', 'important', 'p1']):
            return 'high'
        elif any(x in labels for x in ['medium', 'normal', 'p2']):
            return 'medium'
        else:
            return 'low'



