# Bugnosis Python API

Complete API reference for integrating Bugnosis into your projects.

## Installation

```bash
pip install -e /path/to/bugnosis/cli
```

## Quick Start

```python
from bugnosis import BugnosisAPI

# Initialize API
api = BugnosisAPI(
    github_token="your_github_token",  # Optional but recommended
    groq_key="your_groq_key"  # Optional, for AI features
)

# Scan a repository
bugs = api.scan_repo("pytorch/pytorch", min_impact=85)

# Print results
for bug in bugs:
    print(f"{bug.title}")
    print(f"Impact: {bug.impact_score}/100")
    print(f"Users affected: ~{bug.affected_users:,}")
    print(f"URL: {bug.url}\n")
```

## API Reference

### BugnosisAPI

Main class for programmatic access to Bugnosis.

#### Constructor

```python
BugnosisAPI(
    github_token: Optional[str] = None,
    groq_key: Optional[str] = None,
    use_cache: bool = True,
    db_path: Optional[str] = None
)
```

**Parameters:**
- `github_token`: GitHub personal access token (increases API rate limits)
- `groq_key`: Groq API key for AI features
- `use_cache`: Enable API response caching (default: True)
- `db_path`: Custom database path (default: `~/.config/bugnosis/bugnosis.db`)

**Example:**
```python
api = BugnosisAPI(github_token="ghp_...", use_cache=True)
```

#### scan_repo()

Scan a single repository for high-impact bugs.

```python
api.scan_repo(
    repo: str,
    min_impact: int = 70,
    save: bool = False
) -> List[Bug]
```

**Parameters:**
- `repo`: Repository in `owner/repo` format
- `min_impact`: Minimum impact score (0-100)
- `save`: Save results to local database

**Returns:** List of `Bug` objects sorted by impact score

**Example:**
```python
bugs = api.scan_repo("pytorch/pytorch", min_impact=85, save=True)
```

#### scan_multiple_repos()

Scan multiple repositories and aggregate results.

```python
api.scan_multiple_repos(
    repos: List[str],
    min_impact: int = 70,
    save: bool = False
) -> List[Bug]
```

**Parameters:**
- `repos`: List of repositories in `owner/repo` format
- `min_impact`: Minimum impact score (0-100)
- `save`: Save results to local database

**Returns:** Combined list of bugs sorted by impact

**Example:**
```python
bugs = api.scan_multiple_repos([
    "rust-lang/rust",
    "python/cpython",
    "pytorch/pytorch"
], min_impact=80)
```

#### diagnose_bug()

Get AI-powered diagnosis of a bug.

```python
api.diagnose_bug(
    repo: str,
    issue_number: int
) -> Optional[str]
```

**Parameters:**
- `repo`: Repository in `owner/repo` format
- `issue_number`: GitHub issue number

**Returns:** AI diagnosis text or `None` if unavailable

**Example:**
```python
diagnosis = api.diagnose_bug("pytorch/pytorch", 12345)
if diagnosis:
    print(diagnosis)
```

#### generate_pr()

Generate professional PR description with AI.

```python
api.generate_pr(
    repo: str,
    issue_number: int,
    fix_description: str
) -> Optional[str]
```

**Parameters:**
- `repo`: Repository in `owner/repo` format
- `issue_number`: GitHub issue number
- `fix_description`: Brief description of your fix

**Returns:** Professional PR description or `None` if unavailable

**Example:**
```python
pr_desc = api.generate_pr(
    "pytorch/pytorch",
    12345,
    "Fixed memory leak in tensor allocation"
)
```

#### get_saved_bugs()

Retrieve bugs from local database.

```python
api.get_saved_bugs(
    min_impact: int = 0,
    status: str = None
) -> List[Dict]
```

**Parameters:**
- `min_impact`: Minimum impact score filter
- `status`: Filter by status (e.g., `'discovered'`, `'fixed'`)

**Returns:** List of bug dictionaries

**Example:**
```python
high_impact_bugs = api.get_saved_bugs(min_impact=90)
```

#### record_contribution()

Record a contribution to track your impact.

```python
api.record_contribution(
    repo: str,
    issue_number: int,
    pr_number: int,
    pr_url: str,
    impact_score: int,
    affected_users: int
)
```

**Example:**
```python
api.record_contribution(
    repo="pytorch/pytorch",
    issue_number=12345,
    pr_number=67890,
    pr_url="https://github.com/pytorch/pytorch/pull/67890",
    impact_score=95,
    affected_users=100000
)
```

#### get_stats()

Get your contribution statistics.

```python
api.get_stats() -> Dict
```

**Returns:** Dictionary with:
- `total_contributions`: Number of PRs submitted
- `total_users_helped`: Total users impacted
- `avg_impact_score`: Average impact score
- `merged_count`: Number of merged PRs

**Example:**
```python
stats = api.get_stats()
print(f"Total contributions: {stats['total_contributions']}")
print(f"Users helped: {stats['total_users_helped']:,}")
```

### Bug Object

Represents a discovered bug.

**Attributes:**
- `repo`: Repository name
- `issue_number`: GitHub issue number
- `title`: Issue title
- `url`: GitHub issue URL
- `impact_score`: Impact score (0-100)
- `affected_users`: Estimated affected users
- `severity`: Severity level
- `labels`: Issue labels

## Convenience Functions

Quick single-operation functions that auto-manage resources.

### scan()

```python
from bugnosis.api import scan

bugs = scan("pytorch/pytorch", min_impact=85, github_token="...")
```

### diagnose()

```python
from bugnosis.api import diagnose

diagnosis = diagnose("pytorch/pytorch", 12345, groq_key="...")
```

### generate_pr_description()

```python
from bugnosis.api import generate_pr_description

pr_desc = generate_pr_description(
    "pytorch/pytorch",
    12345,
    "Fixed memory leak",
    groq_key="..."
)
```

## Context Manager Support

BugnosisAPI supports context managers for automatic cleanup:

```python
with BugnosisAPI(github_token="...") as api:
    bugs = api.scan_repo("pytorch/pytorch")
    stats = api.get_stats()
# Database connection automatically closed
```

## Complete Examples

### Find and fix your first bug

```python
from bugnosis import BugnosisAPI

# Initialize
api = BugnosisAPI(github_token="ghp_...")

# Scan popular repo
bugs = api.scan_repo("pytorch/pytorch", min_impact=85, save=True)

# Pick the top bug
top_bug = bugs[0]
print(f"Fix this: {top_bug.title}")
print(f"Impact: {top_bug.impact_score}/100")
print(f"Users affected: ~{top_bug.affected_users:,}")
print(f"URL: {top_bug.url}")

# Get AI diagnosis
diagnosis = api.diagnose_bug(top_bug.repo, top_bug.issue_number)
print(f"\nDiagnosis:\n{diagnosis}")

# After you fix it, generate PR description
pr_desc = api.generate_pr(
    top_bug.repo,
    top_bug.issue_number,
    "Your fix description here"
)
print(f"\nPR Description:\n{pr_desc}")

# Record your contribution
api.record_contribution(
    repo=top_bug.repo,
    issue_number=top_bug.issue_number,
    pr_number=12345,  # Your PR number
    pr_url="https://github.com/.../pull/12345",
    impact_score=top_bug.impact_score,
    affected_users=top_bug.affected_users
)

api.close()
```

### Batch scan multiple projects

```python
from bugnosis.api import scan

# Scan multiple repos at once
repos = [
    "rust-lang/rust",
    "python/cpython",
    "pytorch/pytorch",
    "tensorflow/tensorflow"
]

bugs = scan_multiple_repos(repos, min_impact=80, github_token="...")

# Group by repo
by_repo = {}
for bug in bugs:
    if bug.repo not in by_repo:
        by_repo[bug.repo] = []
    by_repo[bug.repo].append(bug)

# Print summary
for repo, repo_bugs in by_repo.items():
    print(f"\n{repo}: {len(repo_bugs)} high-impact bugs")
    total_impact = sum(b.affected_users for b in repo_bugs)
    print(f"Total potential users helped: ~{total_impact:,}")
```

### Track your impact over time

```python
from bugnosis import BugnosisAPI

with BugnosisAPI() as api:
    # Get all saved bugs
    all_bugs = api.get_saved_bugs()
    
    # Get your stats
    stats = api.get_stats()
    
    print(f"Bugs tracked: {len(all_bugs)}")
    print(f"Contributions made: {stats['total_contributions']}")
    print(f"Total users helped: {stats['total_users_helped']:,}")
    print(f"Average impact: {stats['avg_impact_score']}/100")
    
    # Calculate time saved (assume 30min saved per user)
    hours_saved = stats['total_users_helped'] * 0.5
    print(f"Collective time saved: ~{hours_saved:,.0f} hours")
```

## Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token
- `GROQ_API_KEY`: Groq API key for AI features

## Error Handling

All API methods return `None` or empty lists on errors instead of raising exceptions:

```python
bugs = api.scan_repo("invalid/repo")
# Returns [] if repo doesn't exist

diagnosis = api.diagnose_bug("repo", 99999)
# Returns None if issue doesn't exist or AI unavailable
```

## Rate Limits

- **Without GitHub token**: 60 requests/hour
- **With GitHub token**: 5,000 requests/hour
- **Caching enabled**: Dramatically reduces API calls

Enable caching (default) to maximize your rate limits:

```python
api = BugnosisAPI(github_token="...", use_cache=True)
```

## Support

For issues, feature requests, or contributions:
https://github.com/thebyrdman-git/bugnosis

