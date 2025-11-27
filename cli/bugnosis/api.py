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
from .scanner import GitHubScanner, Bug
from .ai import AIEngine
from .github import GitHubClient
from .storage import BugDatabase
from .multi_scan import scan_multiple_repos


class BugnosisAPI:
    """
    Main API class for Bugnosis.
    
    Provides programmatic access to all Bugnosis features.
    
    Attributes:
        scanner: GitHub repository scanner
        ai: AI engine for diagnosis and PR generation
        github: GitHub API client
        db: Local bug database
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
        self.scanner = GitHubScanner(token=github_token)
        self.ai = AIEngine(api_key=groq_key)
        self.github = GitHubClient(token=github_token, use_cache=use_cache)
        self.db = BugDatabase(db_path=db_path)
        
    def scan_repo(self, 
                  repo: str, 
                  min_impact: int = 70,
                  save: bool = False) -> List[Bug]:
        """
        Scan a repository for high-impact bugs.
        
        Args:
            repo: Repository in owner/repo format
            min_impact: Minimum impact score (0-100)
            save: Save results to local database
            
        Returns:
            List of Bug objects sorted by impact score
            
        Example:
            >>> bugs = api.scan_repo("pytorch/pytorch", min_impact=85)
            >>> for bug in bugs:
            ...     print(f"{bug.title} (Impact: {bug.impact_score})")
        """
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
            
        Example:
            >>> bugs = api.scan_multiple_repos([
            ...     "rust-lang/rust",
            ...     "python/cpython"
            ... ], min_impact=80)
        """
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
            
        Example:
            >>> bugs = api.get_saved_bugs(min_impact=85, status='discovered')
        """
        return self.db.get_bugs(min_impact=min_impact, status=status)
        
    def diagnose_bug(self, repo: str, issue_number: int) -> Optional[str]:
        """
        Get AI-powered diagnosis of a bug.
        
        Args:
            repo: Repository in owner/repo format
            issue_number: GitHub issue number
            
        Returns:
            AI diagnosis text or None if unavailable
            
        Example:
            >>> diagnosis = api.diagnose_bug("pytorch/pytorch", 12345)
            >>> print(diagnosis)
        """
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
        
        Args:
            repo: Repository in owner/repo format
            issue_number: GitHub issue number
            fix_description: Brief description of your fix
            
        Returns:
            Professional PR description or None if unavailable
            
        Example:
            >>> pr_desc = api.generate_pr(
            ...     "pytorch/pytorch", 
            ...     12345,
            ...     "Fixed memory leak in tensor allocation"
            ... )
            >>> print(pr_desc)
        """
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
        """
        Record a contribution to track your impact.
        
        Args:
            repo: Repository in owner/repo format
            issue_number: GitHub issue number
            pr_number: GitHub PR number
            pr_url: URL to the PR
            impact_score: Impact score of the fix (0-100)
            affected_users: Estimated users affected
            
        Example:
            >>> api.record_contribution(
            ...     "pytorch/pytorch",
            ...     12345,
            ...     67890,
            ...     "https://github.com/pytorch/pytorch/pull/67890",
            ...     95,
            ...     100000
            ... )
        """
        self.db.record_contribution(
            repo, issue_number, pr_number, pr_url,
            impact_score, affected_users
        )
        
    def get_stats(self) -> Dict:
        """
        Get your contribution statistics.
        
        Returns:
            Dictionary with stats:
            - total_contributions: Number of PRs submitted
            - total_users_helped: Total users impacted
            - avg_impact_score: Average impact score
            - merged_count: Number of merged PRs
            
        Example:
            >>> stats = api.get_stats()
            >>> print(f"You've helped {stats['total_users_helped']:,} users!")
        """
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


# Convenience functions for quick operations

def scan(repo: str, min_impact: int = 70, **kwargs) -> List[Bug]:
    """
    Quick scan function.
    
    Example:
        >>> from bugnosis.api import scan
        >>> bugs = scan("pytorch/pytorch", min_impact=85)
    """
    with BugnosisAPI(**kwargs) as api:
        return api.scan_repo(repo, min_impact=min_impact)


def diagnose(repo: str, issue_number: int, **kwargs) -> Optional[str]:
    """
    Quick diagnose function.
    
    Example:
        >>> from bugnosis.api import diagnose
        >>> diagnosis = diagnose("pytorch/pytorch", 12345, groq_key="...")
    """
    with BugnosisAPI(**kwargs) as api:
        return api.diagnose_bug(repo, issue_number)


def generate_pr_description(repo: str, issue_number: int, 
                           fix_description: str, **kwargs) -> Optional[str]:
    """
    Quick PR generation function.
    
    Example:
        >>> from bugnosis.api import generate_pr_description
        >>> pr = generate_pr_description(
        ...     "pytorch/pytorch", 
        ...     12345, 
        ...     "Fixed leak",
        ...     groq_key="..."
        ... )
    """
    with BugnosisAPI(**kwargs) as api:
        return api.generate_pr(repo, issue_number, fix_description)


