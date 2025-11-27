# Bugnosis CLI

Command-line tool to find high-impact bugs in open source projects.

## Quick Start

```bash
# Install
pip install -e .

# Scan a repository
bugnosis scan pytorch/pytorch

# With GitHub token (recommended)
export GITHUB_TOKEN=your_token_here
bugnosis scan rust-lang/rust --min-impact 80
```

## Installation

```bash
cd cli
pip install -e .
```

## Usage

```bash
# Basic scan
bugnosis scan owner/repo

# Filter by impact score
bugnosis scan microsoft/vscode --min-impact 85

# Show more details
bugnosis scan python/cpython --details

# With custom token
bugnosis scan facebook/react --token ghp_your_token
```

## GitHub Token

Get better rate limits with a GitHub token:

1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `public_repo`
4. Export: `export GITHUB_TOKEN=your_token`

## How It Works

Bugnosis scans GitHub repositories and scores bugs 0-100 based on:

- **User base** (40 pts): How many people use the project
- **Severity** (30 pts): Community engagement (comments, reactions)  
- **Ease** (20 pts): How easy it is to fix
- **Time** (10 pts): How recent the issue is

High scores (70+) = bugs worth fixing that help many people.

## Example Output

```
Scanning pytorch/pytorch for high-impact bugs...

Found 3 high-impact bugs:

1. [92/100] 🔥 pytorch/pytorch
   CUDA out of memory error on RTX 4090
   Users affected: ~8,000
   Severity: Critical
   https://github.com/pytorch/pytorch/issues/12345

2. [85/100] ⭐ pytorch/pytorch
   Performance regression in transformer models
   Users affected: ~5,000
   Severity: High
   https://github.com/pytorch/pytorch/issues/67890

Total potential impact: ~13,000 users
Average impact score: 88/100
```

## Development

```bash
# Run without installing
python -m bugnosis scan owner/repo

# Run tests
pytest

# Format code
black .
```

## Future Features

- Scan multiple repos at once
- Save results to database
- AI-powered bug analysis
- PR generation assistance
- Impact tracking over time

## License

MIT




