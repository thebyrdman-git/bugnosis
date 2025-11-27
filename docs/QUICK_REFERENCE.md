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
export GITHUB_TOKEN="ghp_..."  # Or use 'bugnosis auth login'
export GROQ_API_KEY="gsk_..."  # For AI features
```

## Common Commands

### Scanning

```bash
# Scan single repository
bugnosis scan pytorch/pytorch --save

# AI Smart Scan (Finds platform automatically)
bugnosis smart-scan "python requests" --min-impact 80

# Federated Search (GitHub + GitLab + Bugzilla)
bugnosis search "linux kernel"
```

### Developer Tools

```bash
# Authentication (Secure Keyring)
bugnosis auth login github
bugnosis auth status

# System Health Check
bugnosis doctor

# AI Co-Pilot (Guided Fix)
bugnosis copilot pytorch/pytorch 12345

# Rejection Coaching (AI Post-Mortem)
bugnosis coach pytorch/pytorch 54321

# Cloud Sync (Backup Profile)
bugnosis sync push
bugnosis sync pull <gist-id>
```

### Viewing Results

```bash
# List saved bugs
bugnosis list --min-impact 85

# View your statistics
bugnosis stats
```

### Exporting

```bash
# Export to JSON/CSV/Markdown
bugnosis export json bugs.json --min-impact 85
bugnosis export markdown BUGS_TO_FIX.md

# Generate HTML leaderboard
bugnosis leaderboard leaderboard.html
```

### Maintenance

```bash
# Clear API cache
bugnosis clear-cache

# List installed plugins
bugnosis plugins
```

## Python API

### Quick Start

```python
from bugnosis.api import BugnosisAPI

# Initialize (auto-loads token from auth command)
api = BugnosisAPI()

# Scan
bugs = api.scan_repo("pytorch/pytorch", min_impact=85)

# Close
api.close()
```

### Convenience Functions

```python
from bugnosis.api import scan, diagnose, generate_pr_description

# Quick scan
bugs = scan("pytorch/pytorch", min_impact=85)

# Quick diagnosis
diagnosis = diagnose("pytorch/pytorch", 12345)
```

## Impact Scoring

Bugnosis scores bugs 0-100 based on:

- **90-100**: Critical bugs affecting 100K+ users (Boss Level)
- **80-89**: High impact bugs affecting 50K-100K users
- **70-79**: Significant bugs affecting 10K-50K users
- **0-69**: Lower impact or niche bugs

## File Locations

- Database: `~/.config/bugnosis/bugnosis.db`
- Plugins: `~/.bugnosis/plugins/`
- Cache: `~/.cache/bugnosis/`

## More Help

- Full documentation: https://github.com/thebyrdman-git/bugnosis
- API reference: `API.md`
- Developer Guide: `../DEVELOPERS.md`
