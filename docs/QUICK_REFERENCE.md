# Bugnosis Quick Reference

Fast reference for common Bugnosis commands and workflows.

## Installation

```bash
git clone https://github.com/thebyrdman-git/bugnosis.git
cd bugnosis/cli
pip install -e .
```

## Environment Setup

```bash
export GITHUB_TOKEN="ghp_..."  # For higher API rate limits
export GROQ_API_KEY="gsk_..."  # For AI features
```

## Common Commands

### Scanning

```bash
# Scan single repository
bugnosis scan pytorch/pytorch

# Scan with higher impact threshold
bugnosis scan pytorch/pytorch --min-impact 85

# Scan and save to database
bugnosis scan pytorch/pytorch --save

# Scan multiple repositories
bugnosis scan-multi rust-lang/rust python/cpython pytorch/pytorch --save
```

### Viewing Results

```bash
# List saved bugs
bugnosis list

# List high-impact bugs only
bugnosis list --min-impact 85

# View your statistics
bugnosis stats
```

### Exporting

```bash
# Export to JSON
bugnosis export json bugs.json --min-impact 85

# Export to CSV
bugnosis export csv bugs.csv

# Export to Markdown
bugnosis export markdown BUGS_TO_FIX.md --min-impact 90

# Generate HTML leaderboard
bugnosis leaderboard leaderboard.html
```

### AI Features

```bash
# AI Co-Pilot (interactive bug fixing)
bugnosis copilot pytorch/pytorch 12345

# Estimate bug difficulty
bugnosis difficulty rust-lang/rust 54321

# Get AI diagnosis of a bug
bugnosis diagnose pytorch/pytorch 12345

# Generate PR description
bugnosis generate-pr pytorch/pytorch 12345 "Fixed memory leak in tensor allocation"
```

### Maintenance

```bash
# Clear API cache
bugnosis clear-cache

# Show help
bugnosis help
```

## Python API

### Quick Start

```python
from bugnosis import BugnosisAPI

# Initialize
api = BugnosisAPI(github_token="ghp_...")

# Scan
bugs = api.scan_repo("pytorch/pytorch", min_impact=85)

# Close
api.close()
```

### Context Manager

```python
from bugnosis import BugnosisAPI

with BugnosisAPI(github_token="ghp_...") as api:
    bugs = api.scan_repo("pytorch/pytorch", min_impact=85)
    for bug in bugs:
        print(f"{bug.title} - Impact: {bug.impact_score}/100")
```

### Convenience Functions

```python
from bugnosis.api import scan, diagnose, generate_pr_description

# Quick scan
bugs = scan("pytorch/pytorch", min_impact=85, github_token="ghp_...")

# Quick diagnosis
diagnosis = diagnose("pytorch/pytorch", 12345, groq_key="gsk_...")

# Quick PR generation
pr = generate_pr_description(
    "pytorch/pytorch", 
    12345, 
    "Fixed memory leak",
    groq_key="gsk_..."
)
```

## Workflows

### Workflow 1: Find Your First Bug to Fix

```bash
# 1. Scan a popular repository
bugnosis scan pytorch/pytorch --min-impact 85 --save

# 2. List the bugs
bugnosis list --min-impact 85

# 3. Pick one and get AI diagnosis
bugnosis diagnose pytorch/pytorch 12345

# 4. Fix the bug (in your IDE)

# 5. Generate PR description
bugnosis generate-pr pytorch/pytorch 12345 "Your fix description"

# 6. Submit PR and track contribution (via API or database)
```

### Workflow 2: Weekly Bug Scanning

```bash
# Scan your favorite projects weekly
bugnosis scan-multi \
  rust-lang/rust \
  python/cpython \
  pytorch/pytorch \
  tensorflow/tensorflow \
  --min-impact 80 \
  --save

# Export to markdown for review
bugnosis export markdown BUGS_THIS_WEEK.md --min-impact 80

# Check your impact
bugnosis stats
```

### Workflow 3: Build a Dashboard

```python
from bugnosis import BugnosisAPI

api = BugnosisAPI(github_token="ghp_...")

# Scan multiple repos
repos = ["rust-lang/rust", "python/cpython", "pytorch/pytorch"]
all_bugs = api.scan_multiple_repos(repos, min_impact=80, save=True)

# Get stats
stats = api.get_stats()

# Generate leaderboard
# (use CLI: bugnosis leaderboard dashboard.html)

api.close()
```

## Impact Scoring

Bugnosis scores bugs 0-100 based on:

- **90-100**: Critical bugs affecting 100K+ users
- **80-89**: High impact bugs affecting 50K-100K users
- **70-79**: Significant bugs affecting 10K-50K users
- **60-69**: Moderate bugs affecting 5K-10K users
- **0-59**: Lower impact or niche bugs

Focus on bugs scoring 80+ for maximum impact.

## Tips

1. **Set GitHub token** to avoid rate limits (60 → 5000 requests/hour)
2. **Use caching** (enabled by default) for faster repeat scans
3. **Save results** with `--save` to track over time
4. **Export regularly** to share with your team
5. **Track contributions** to see your cumulative impact

## File Locations

- Database: `~/.config/bugnosis/bugnosis.db`
- Cache: `~/.cache/bugnosis/`
- Exports: Current directory (or specify path)

## Common Issues

### "No GitHub token set"
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

### "AI features unavailable"
```bash
export GROQ_API_KEY="gsk_your_key_here"
```

### Rate limit exceeded
- Set GITHUB_TOKEN
- Use caching (default)
- Reduce scan frequency

## More Help

- Full documentation: https://github.com/thebyrdman-git/bugnosis
- API reference: `docs/API.md`
- Examples: `examples/api_usage.py`
- Issues: https://github.com/thebyrdman-git/bugnosis/issues


