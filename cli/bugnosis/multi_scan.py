"""Multi-repository scanning."""

from typing import List
from .scanner import GitHubScanner, Bug


def scan_multiple_repos(repos: List[str], min_impact: int = 70, 
                       token: str = None) -> List[Bug]:
    """
    Scan multiple repositories and aggregate results.
    
    Args:
        repos: List of repo names (owner/repo format)
        min_impact: Minimum impact score
        token: GitHub token
        
    Returns:
        Combined list of bugs sorted by impact
    """
    scanner = GitHubScanner(token=token)
    all_bugs = []
    
    for repo in repos:
        print(f"Scanning {repo}...")
        bugs = scanner.scan_repo(repo, min_impact=min_impact)
        all_bugs.extend(bugs)
        print(f"  Found {len(bugs)} bugs\n")
        
    # Sort by impact
    all_bugs.sort(key=lambda b: b.impact_score, reverse=True)
    
    return all_bugs


