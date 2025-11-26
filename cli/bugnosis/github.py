"""GitHub API helpers."""

import requests
from typing import Optional, Dict


class GitHubClient:
    """Simplified GitHub API client."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers['Authorization'] = f'token {token}'
        self.session.headers['Accept'] = 'application/vnd.github.v3+json'
        
    def get_issue(self, repo: str, issue_number: int) -> Optional[Dict]:
        """Fetch full issue data including body."""
        url = f'https://api.github.com/repos/{repo}/issues/{issue_number}'
        response = self.session.get(url)
        
        if response.status_code == 200:
            return response.json()
        return None

