"""CLI interface for Bugnosis."""

import sys
import os
from typing import Optional
from .scanner import GitHubScanner


def print_bugs(bugs, show_details=False):
    """Print bugs in a clean format."""
    if not bugs:
        print("No high-impact bugs found.")
        return
        
    print(f"\nFound {len(bugs)} high-impact bugs:\n")
    
    for i, bug in enumerate(bugs, 1):
        # Impact indicator
        if bug.impact_score >= 90:
            indicator = "🔥"
        elif bug.impact_score >= 80:
            indicator = "⭐"
        else:
            indicator = "✨"
            
        print(f"{i}. [{bug.impact_score}/100] {indicator} {bug.repo}")
        print(f"   {bug.title}")
        print(f"   Users affected: ~{bug.affected_users:,}")
        print(f"   Severity: {bug.severity}")
        
        if show_details:
            print(f"   Comments: {bug.comments} | Reactions: {bug.reactions}")
            
        print(f"   {bug.url}")
        print()


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help']:
        print("""
Bugnosis - Find high-impact bugs to fix

Usage:
    bugnosis scan <repo> [options]
    bugnosis help

Examples:
    bugnosis scan pytorch/pytorch
    bugnosis scan rust-lang/rust --min-impact 80
    bugnosis scan microsoft/vscode --details

Options:
    --min-impact N    Minimum impact score (0-100, default: 70)
    --details         Show additional details
    --token TOKEN     GitHub API token (or set GITHUB_TOKEN env var)

Environment:
    GITHUB_TOKEN      GitHub personal access token for API
    
Note: Without a token, API rate limits are very low (60 requests/hour).
Get a token at: https://github.com/settings/tokens
""")
        return
        
    if args[0] != 'scan':
        print(f"Unknown command: {args[0]}")
        print("Run 'bugnosis help' for usage")
        sys.exit(1)
        
    if len(args) < 2:
        print("Error: Repository required")
        print("Usage: bugnosis scan <owner/repo>")
        sys.exit(1)
        
    repo = args[1]
    
    # Parse options
    min_impact = 70
    show_details = False
    token = os.environ.get('GITHUB_TOKEN')
    
    i = 2
    while i < len(args):
        if args[i] == '--min-impact' and i + 1 < len(args):
            min_impact = int(args[i + 1])
            i += 2
        elif args[i] == '--details':
            show_details = True
            i += 1
        elif args[i] == '--token' and i + 1 < len(args):
            token = args[i + 1]
            i += 2
        else:
            print(f"Unknown option: {args[i]}")
            i += 1
            
    # Scan
    print(f"Scanning {repo} for high-impact bugs...")
    print(f"Minimum impact score: {min_impact}")
    
    if not token:
        print("\nWarning: No GitHub token set. Rate limits are very low.")
        print("Set GITHUB_TOKEN environment variable or use --token")
        print()
        
    scanner = GitHubScanner(token=token)
    bugs = scanner.scan_repo(repo, min_impact=min_impact)
    
    print_bugs(bugs, show_details=show_details)
    
    if bugs:
        print(f"Total potential impact: ~{sum(b.affected_users for b in bugs):,} users")
        print(f"Average impact score: {sum(b.impact_score for b in bugs) // len(bugs)}/100")


if __name__ == '__main__':
    main()

