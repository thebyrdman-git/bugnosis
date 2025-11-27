# Bugnosis Python API

Complete API reference for integrating Bugnosis into your projects.

## Installation

```bash
pip install -e /path/to/bugnosis/cli
```

## Quick Start

```python
from bugnosis import BugnosisAPI

# Initialize API (loads tokens from secure auth store)
api = BugnosisAPI()

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
- `github_token`: Optional override. Defaults to `keyring` storage or `GITHUB_TOKEN` env var.
- `groq_key`: Optional override. Defaults to `GROQ_API_KEY` env var.
- `use_cache`: Enable API response caching (default: True)
- `db_path`: Custom database path (default: `~/.config/bugnosis/bugnosis.db`)

**Example:**
```python
api = BugnosisAPI(use_cache=True)
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

**Returns:** AI diagnosis text or `None` if unavailable

#### generate_pr()

Generate professional PR description with AI.

```python
api.generate_pr(
    repo: str,
    issue_number: int,
    fix_description: str
) -> Optional[str]
```

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

**Returns:** List of bug dictionaries

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

#### close()

Close database connection. Recommended to use context manager instead.

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

bugs = scan("pytorch/pytorch", min_impact=85)
```

### diagnose()

```python
from bugnosis.api import diagnose

diagnosis = diagnose("pytorch/pytorch", 12345)
```

### generate_pr_description()

```python
from bugnosis.api import generate_pr_description

pr_desc = generate_pr_description(
    "pytorch/pytorch",
    12345,
    "Fixed memory leak"
)
```

## Context Manager Support

BugnosisAPI supports context managers for automatic cleanup:

```python
with BugnosisAPI() as api:
    bugs = api.scan_repo("pytorch/pytorch")
    stats = api.get_stats()
# Database connection automatically closed
```

## Cloud Sync & Auth (New)

You can also manage authentication programmatically via the internal auth module, though the CLI `bugnosis auth` is preferred.

To check connectivity:
```python
api = BugnosisAPI()
if api.online:
    print("Connected to Bugnosis Network")
else:
    print("Offline Mode: Using local database")
```

## Support

For issues, feature requests, or contributions:
https://github.com/thebyrdman-git/bugnosis
