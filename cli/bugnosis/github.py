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

    def get_user(self) -> Optional[Dict]:
        """Get current authenticated user."""
        if not self.token:
            return None
        resp = self.session.get('https://api.github.com/user')
        return resp.json() if resp.status_code == 200 else None

    def create_gist(self, files: Dict[str, Dict[str, str]], description: str, public: bool = False) -> Optional[Dict]:
        """Create a GitHub Gist."""
        if not self.token:
            raise ValueError("Token required to create gist")
            
        url = 'https://api.github.com/gists'
        payload = {
            'description': description,
            'public': public,
            'files': files
        }
        resp = self.session.post(url, json=payload)
        return resp.json() if resp.status_code == 201 else None

    def update_gist(self, gist_id: str, files: Dict[str, Dict[str, str]]) -> Optional[Dict]:
        """Update an existing Gist."""
        if not self.token:
            raise ValueError("Token required to update gist")
            
        url = f'https://api.github.com/gists/{gist_id}'
        resp = self.session.patch(url, json={'files': files})
        return resp.json() if resp.status_code == 200 else None

    def get_gist(self, gist_id: str) -> Optional[Dict]:
        """Fetch a Gist."""
        if not self.token:
            raise ValueError("Token required to fetch gist")
            
        url = f'https://api.github.com/gists/{gist_id}'
        resp = self.session.get(url)
        return resp.json() if resp.status_code == 200 else None

