"""
Bugnosis - Find high-impact bugs to fix in open source projects.

This package provides both a CLI tool and a Python API for
discovering, analyzing, and fixing bugs that will help the most users.

CLI Usage:
    $ bugnosis scan pytorch/pytorch
    $ bugnosis diagnose microsoft/vscode 12345
    $ bugnosis generate-pr owner/repo 123 "Fixed bug"

API Usage:
    >>> from bugnosis import BugnosisAPI
    >>> 
    >>> with BugnosisAPI(github_token="...") as api:
    ...     bugs = api.scan_repo("pytorch/pytorch", min_impact=85)
    ...     for bug in bugs:
    ...         print(f"{bug.title} - Impact: {bug.impact_score}")

Quick Functions:
    >>> from bugnosis.api import scan, diagnose, generate_pr_description
    >>> 
    >>> bugs = scan("pytorch/pytorch", min_impact=80)
    >>> diagnosis = diagnose("pytorch/pytorch", 12345)
"""

__version__ = "0.1.0"
__author__ = "Bugnosis Contributors"
__license__ = "MIT"

from .api import (
    BugnosisAPI,
    scan,
    diagnose,
    generate_pr_description,
)
from .scanner import Bug, GitHubScanner

__all__ = [
    'BugnosisAPI',
    'Bug',
    'GitHubScanner',
    'scan',
    'diagnose',
    'generate_pr_description',
]

