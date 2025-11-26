"""GitHub API helpers."""

import requests
from typing import Optional, Dict
from .cache import APICache


class GitHubClient:
    """Simplified GitHub API client with caching."""
    
    def __init__(self, token: Optional[str] = None, use_cache: bool = True):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers['Authorization'] = f'token {token}'
        self.session.headers['Accept'] = 'application/vnd.github.v3+json'
        self.cache = APICache(ttl=3600) if use_cache else None  # 1 hour cache
        
    def get_issue(self, repo: str, issue_number: int) -> Optional[Dict]:
        """Fetch full issue data including body with caching."""
        cache_key = f"issue:{repo}:{issue_number}"
        
        # Try cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        url = f'https://api.github.com/repos/{repo}/issues/{issue_number}'
        response = self.session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Cache the result
            if self.cache:
                self.cache.set(cache_key, data)
            return data
        return None

