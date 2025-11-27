"""Bugnosis Python API for programmatic access.

This module provides a clean API for integrating Bugnosis
into your own tools and workflows.

Example:
    >>> from bugnosis.api import BugnosisAPI
    >>> 
    >>> # Initialize API
    >>> api = BugnosisAPI(github_token="your_token", groq_key="your_key")
    >>> 
    >>> # Scan a repository
    >>> bugs = api.scan_repo("pytorch/pytorch", min_impact=80)
    >>> 
    >>> # Get AI diagnosis
    >>> diagnosis = api.diagnose_bug("pytorch/pytorch", 12345)
    >>> 
    >>> # Generate PR description
    >>> pr_desc = api.generate_pr("pytorch/pytorch", 12345, "Fixed memory leak")
"""

from typing import List, Dict, Optional
import socket
import logging
from .scanner import GitHubScanner, Bug
from .ai import AIEngine
from .github import GitHubClient
from .storage import BugDatabase
from .multi_scan import scan_multiple_repos

logger = logging.getLogger(__name__)

def is_online() -> bool:
    """Check if internet connection is available."""
    try:
        # Try to connect to a reliable DNS
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

class BugnosisAPI:
    """
    Main API class for Bugnosis.
    
    Provides programmatic access to all Bugnosis features.
    
    Attributes:
        scanner: GitHub repository scanner
        ai: AI engine for diagnosis and PR generation
        github: GitHub API client
        db: Local bug database
        online: Boolean indicating connectivity status
    """
    
    def __init__(self, 
                 github_token: Optional[str] = None,
                 groq_key: Optional[str] = None,
                 use_cache: bool = True,
                 db_path: Optional[str] = None):
        """
        Initialize Bugnosis API.
        
        Args:
            github_token: GitHub personal access token (optional, but recommended)
            groq_key: Groq API key for AI features (optional)
            use_cache: Enable API response caching (default: True)
            db_path: Custom database path (default: ~/.config/bugnosis/bugnosis.db)
        """
        self.online = is_online()
        self.db = BugDatabase(db_path=db_path)
        
        if self.online:
            self.scanner = GitHubScanner(token=github_token)
            self.ai = AIEngine(api_key=groq_key)
            self.github = GitHubClient(token=github_token, use_cache=use_cache)
        else:
            logger.warning("Offline mode detected. API functionality will be limited to local data.")
            self.scanner = None
            self.ai = None
            self.github = None
        
    def scan_repo(self, 
                  repo: str, 
                  min_impact: int = 70,
                  save: bool = False) -> List[Bug]:
        """
        Scan a repository for high-impact bugs.
        
        If offline, searches local database for previously saved bugs.
        
        Args:
            repo: Repository in owner/repo format
            min_impact: Minimum impact score (0-100)
            save: Save results to local database
            
        Returns:
            List of Bug objects sorted by impact score
        """
        if not self.online:
            # Offline mode: Search local DB
            logger.info(f"Offline mode: Searching local database for {repo}")
            
            # Query local database for bugs matching this repo
            # BugDatabase.get_bugs returns dicts, convert to objects? 
            # For now, scan_repo expects Bug objects.
            
            # We'll implement a search method in DB that mimics scan
            results = self.db.search_bugs(repo_query=repo, min_impact=min_impact)
            
            # Convert dicts to Bug objects
            bugs = []
            for r in results:
                # Need to construct Bug object from dict
                # This assumes Bug class can handle it or we manually map
                bug = Bug(
                    repo=r['repo'].split(':')[-1] if ':' in r['repo'] else r['repo'],
                    issue_number=r['issue_number'],
                    title=r['title'],
                    url=r['url'],
                    impact_score=r['impact_score'],
                    affected_users=r['affected_users'],
                    severity=r['severity'],
                    labels=json.loads(r['labels']) if isinstance(r['labels'], str) else [],
                    comments_count=r['comments'],
                    created_at=r['created_at'],
                    updated_at=r['updated_at'],
                    platform=r['repo'].split(':')[0] if ':' in r['repo'] else 'github'
                )
                bugs.append(bug)
            return bugs

        bugs = self.scanner.scan_repo(repo, min_impact=min_impact)
        
        if save and bugs:
            self.db.save_bugs(bugs)
            
        return bugs
        
    def scan_multiple_repos(self,
                           repos: List[str],
                           min_impact: int = 70,
                           save: bool = False) -> List[Bug]:
        """
        Scan multiple repositories and aggregate results.
        
        Args:
            repos: List of repositories (owner/repo format)
            min_impact: Minimum impact score (0-100)
            save: Save results to local database
            
        Returns:
            Combined list of bugs sorted by impact
        """
        if not self.online:
             # Simple offline aggregation
             all_bugs = []
             for repo in repos:
                 all_bugs.extend(self.scan_repo(repo, min_impact=min_impact, save=False))
             all_bugs.sort(key=lambda x: x.impact_score, reverse=True)
             return all_bugs

        bugs = scan_multiple_repos(repos, min_impact=min_impact, 
                                  token=self.scanner.token)
        
        if save and bugs:
            self.db.save_bugs(bugs)
            
        return bugs
        
    def get_saved_bugs(self, 
                      min_impact: int = 0,
                      status: str = None) -> List[Dict]:
        """
        Retrieve bugs from local database.
        
        Args:
            min_impact: Minimum impact score filter
            status: Filter by status (e.g., 'discovered', 'fixed')
            
        Returns:
            List of bug dictionaries
        """
        return self.db.get_bugs(min_impact=min_impact, status=status)
        
    def diagnose_bug(self, repo: str, issue_number: int) -> Optional[str]:
        """
        Get AI-powered diagnosis of a bug.
        """
        if not self.online:
            return "Error: AI features require an internet connection."

        issue = self.github.get_issue(repo, issue_number)
        if not issue:
            return None
            
        return self.ai.diagnose(issue)
        
    def generate_pr(self, 
                   repo: str, 
                   issue_number: int,
                   fix_description: str) -> Optional[str]:
        """
        Generate PR description with AI.
        """
        if not self.online:
            return "Error: AI features require an internet connection."

        issue = self.github.get_issue(repo, issue_number)
        if not issue:
            return None
            
        return self.ai.generate_pr_description(issue, fix_description)
        
    def record_contribution(self,
                          repo: str,
                          issue_number: int,
                          pr_number: int,
                          pr_url: str,
                          impact_score: int,
                          affected_users: int):
        """Record a contribution to track your impact."""
        self.db.record_contribution(
            repo, issue_number, pr_number, pr_url,
            impact_score, affected_users
        )
        
    def get_stats(self) -> Dict:
        """Get your contribution statistics."""
        return self.db.get_stats()
        
    def close(self):
        """Close database connection."""
        self.db.close()
        
    def __enter__(self):
        """Context manager support."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close on context exit."""
        self.close()
    
    @property
    def status(self) -> str:
        """Return 'online' or 'offline'."""
        return 'online' if self.online else 'offline'


# Convenience functions for quick operations

def scan(repo: str, min_impact: int = 70, **kwargs) -> List[Bug]:
    """Quick scan function."""
    with BugnosisAPI(**kwargs) as api:
        return api.scan_repo(repo, min_impact=min_impact)


def diagnose(repo: str, issue_number: int, **kwargs) -> Optional[str]:
    """Quick diagnose function."""
    with BugnosisAPI(**kwargs) as api:
        return api.diagnose_bug(repo, issue_number)


def generate_pr_description(repo: str, issue_number: int, 
                           fix_description: str, **kwargs) -> Optional[str]:
    """Quick PR generation function."""
    with BugnosisAPI(**kwargs) as api:
        return api.generate_pr(repo, issue_number, fix_description)
