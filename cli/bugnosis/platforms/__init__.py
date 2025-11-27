"""Multi-platform bug tracking integrations."""

from .github_platform import GitHubPlatform
from .gitlab_platform import GitLabPlatform
from .bugzilla_platform import BugzillaPlatform
from .base import BugPlatform, Bug

__all__ = [
    'BugPlatform',
    'Bug',
    'GitHubPlatform',
    'GitLabPlatform',
    'BugzillaPlatform',
    'get_platform',
    'list_platforms',
]


PLATFORMS = {
    'github': GitHubPlatform,
    'gitlab': GitLabPlatform,
    'bugzilla': BugzillaPlatform,
}


def get_platform(name: str, **kwargs):
    """Get a platform instance by name."""
    platform_class = PLATFORMS.get(name.lower())
    if not platform_class:
        raise ValueError(f"Unknown platform: {name}. Available: {', '.join(PLATFORMS.keys())}")
    return platform_class(**kwargs)


def list_platforms():
    """List all available platforms."""
    return list(PLATFORMS.keys())



