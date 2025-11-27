"""Base classes for bug tracking platforms."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Bug:
    """Normalized bug representation across platforms."""
    
    platform: str           # github, gitlab, bugzilla, etc.
    repo: str              # Repository/project identifier
    issue_number: int      # Issue/bug number
    title: str             # Bug title
    url: str               # Link to bug
    description: str       # Bug description
    impact_score: int      # 0-100 impact score
    affected_users: int    # Estimated affected users
    severity: str          # critical, high, medium, low
    status: str            # open, closed, etc.
    labels: List[str]      # Tags/labels
    created_at: datetime   # When created
    updated_at: datetime   # Last updated
    comments_count: int    # Number of comments
    
    # Platform-specific data
    raw_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'platform': self.platform,
            'repo': self.repo,
            'issue_number': self.issue_number,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'impact_score': self.impact_score,
            'affected_users': self.affected_users,
            'severity': self.severity,
            'status': self.status,
            'labels': self.labels,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'comments_count': self.comments_count,
        }


class BugPlatform(ABC):
    """Abstract base class for bug tracking platforms."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize platform with optional API token."""
        self.api_token = api_token
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Platform name."""
        pass
    
    @abstractmethod
    def search_bugs(self, 
                   project: str,
                   min_impact: int = 70,
                   labels: Optional[List[str]] = None,
                   severity: Optional[str] = None) -> List[Bug]:
        """
        Search for bugs in a project.
        
        Args:
            project: Project identifier (varies by platform)
            min_impact: Minimum impact score (0-100)
            labels: Filter by labels/tags
            severity: Filter by severity
            
        Returns:
            List of Bug objects sorted by impact
        """
        pass
    
    @abstractmethod
    def get_bug(self, project: str, bug_id: int) -> Optional[Bug]:
        """Get a specific bug by ID."""
        pass
    
    @abstractmethod
    def calculate_impact(self, bug_data: Dict[str, Any]) -> int:
        """
        Calculate impact score (0-100) for a bug.
        
        Platform-specific implementation based on:
        - Number of affected users
        - Severity/priority
        - Comments/reactions
        - Time since reported
        """
        pass
    
    @abstractmethod
    def estimate_affected_users(self, bug_data: Dict[str, Any]) -> int:
        """Estimate number of affected users."""
        pass



