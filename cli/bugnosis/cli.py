"""CLI interface for Bugnosis."""

import sys
import os
from typing import Optional
from .scanner import GitHubScanner
from .ai import AIEngine
from .github import GitHubClient
from .storage import BugDatabase
from .multi_scan import scan_multiple_repos


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


def cmd_diagnose(args):
    """AI diagnosis of a bug."""
    if len(args) < 2:
        print("Error: Repository and issue number required")
        print("Usage: bugnosis diagnose owner/repo issue-number")
        sys.exit(1)
        
    repo = args[0]
    issue_num = int(args[1])
    token = os.environ.get('GITHUB_TOKEN')
    
    print(f"Fetching issue #{issue_num} from {repo}...")
    
    client = GitHubClient(token=token)
    issue = client.get_issue(repo, issue_num)
    
    if not issue:
        print("Error: Could not fetch issue")
        sys.exit(1)
        
    print(f"\nIssue: {issue['title']}")
    print(f"URL: {issue['html_url']}")
    print(f"Comments: {issue.get('comments', 0)}")
    print("\nRunning AI diagnosis...\n")
    
    ai = AIEngine()
    diagnosis = ai.diagnose_bug(issue)
    
    if diagnosis:
        print("AI Diagnosis:")
        print("-" * 60)
        print(diagnosis)
        print("-" * 60)
    else:
        print("AI diagnosis failed. Set GROQ_API_KEY environment variable.")
        

def cmd_generate_pr(args):
    """Generate PR description with AI."""
    if len(args) < 3:
        print("Error: Repository, issue number, and fix description required")
        print('Usage: bugnosis generate-pr owner/repo issue-number "what you fixed"')
        sys.exit(1)
        
    repo = args[0]
    issue_num = int(args[1])
    fix_desc = args[2]
    token = os.environ.get('GITHUB_TOKEN')
    
    print(f"Generating PR description for issue #{issue_num}...")
    
    client = GitHubClient(token=token)
    issue = client.get_issue(repo, issue_num)
    
    if not issue:
        print("Error: Could not fetch issue")
        sys.exit(1)
        
    ai = AIEngine()
    pr_description = ai.generate_pr_description(issue, fix_desc)
    
    if pr_description:
        print("\nGenerated PR Description:")
        print("=" * 60)
        print(pr_description)
        print("=" * 60)
        print("\nCopy this for your PR or save to a file:")
        print(f"  bugnosis generate-pr {repo} {issue_num} \"{fix_desc}\" > PR_DESCRIPTION.md")
    else:
        print("PR generation failed. Set GROQ_API_KEY environment variable.")


def cmd_scan_multi(args):
    """Scan multiple repositories."""
    if len(args) < 2:
        print("Error: At least 2 repositories required")
        print("Usage: bugnosis scan-multi repo1 repo2 [repo3...] [options]")
        sys.exit(1)
        
    # Parse repos and options
    repos = []
    min_impact = 70
    save_results = False
    token = os.environ.get('GITHUB_TOKEN')
    
    i = 0
    while i < len(args):
        if args[i].startswith('--'):
            if args[i] == '--min-impact' and i + 1 < len(args):
                min_impact = int(args[i + 1])
                i += 2
            elif args[i] == '--save':
                save_results = True
                i += 1
            elif args[i] == '--token' and i + 1 < len(args):
                token = args[i + 1]
                i += 2
            else:
                i += 1
        else:
            repos.append(args[i])
            i += 1
            
    if not repos:
        print("Error: No repositories specified")
        sys.exit(1)
        
    print(f"Scanning {len(repos)} repositories...")
    print(f"Minimum impact: {min_impact}\n")
    
    bugs = scan_multiple_repos(repos, min_impact=min_impact, token=token)
    
    if save_results:
        db = BugDatabase()
        db.save_bugs(bugs)
        db.close()
        print(f"\nSaved {len(bugs)} bugs to local database")
        
    print_bugs(bugs[:10])  # Show top 10
    
    if len(bugs) > 10:
        print(f"... and {len(bugs) - 10} more bugs")
        print(f"Run 'bugnosis list --min-impact {min_impact}' to see all")
        
    print(f"\nTotal bugs found: {len(bugs)}")
    print(f"Total potential impact: ~{sum(b.affected_users for b in bugs):,} users")


def cmd_list(args):
    """List saved bugs from database."""
    min_impact = 70
    
    i = 0
    while i < len(args):
        if args[i] == '--min-impact' and i + 1 < len(args):
            min_impact = int(args[i + 1])
            i += 2
        else:
            i += 1
            
    db = BugDatabase()
    bugs_data = db.get_bugs(min_impact=min_impact)
    db.close()
    
    if not bugs_data:
        print(f"No saved bugs with impact >= {min_impact}")
        print("Run 'bugnosis scan <repo> --save' to save bugs")
        return
        
    print(f"\nSaved bugs (impact >= {min_impact}):\n")
    
    for i, bug in enumerate(bugs_data[:20], 1):
        indicator = "🔥" if bug['impact_score'] >= 90 else "⭐" if bug['impact_score'] >= 80 else "✨"
        print(f"{i}. [{bug['impact_score']}/100] {indicator} {bug['repo']}")
        print(f"   {bug['title']}")
        print(f"   Users: ~{bug['affected_users']:,} | Severity: {bug['severity']}")
        print(f"   {bug['url']}")
        print()
        
    if len(bugs_data) > 20:
        print(f"... and {len(bugs_data) - 20} more")
        
    print(f"Total: {len(bugs_data)} bugs")


def cmd_stats(args):
    """Show contribution statistics."""
    db = BugDatabase()
    stats = db.get_stats()
    bugs_count = len(db.get_bugs())
    db.close()
    
    print("\nYour Bugnosis Stats:\n")
    print(f"Bugs tracked: {bugs_count}")
    print(f"Contributions: {stats['total_contributions']}")
    print(f"Users helped: {stats['total_users_helped']:,}")
    print(f"Average impact: {stats['avg_impact_score']}/100")
    print(f"Merged PRs: {stats['merged_count']}")
    
    if stats['total_users_helped'] > 0:
        print(f"\nCollective time saved: ~{stats['total_users_helped'] * 0.5:,.0f} hours")
    
    print("\nKeep making an impact!")


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help']:
        print("""
Bugnosis - Find high-impact bugs to fix

Usage:
    bugnosis scan <repo> [options]
    bugnosis scan-multi <repo1> <repo2> ... [options]
    bugnosis list [--min-impact N]
    bugnosis stats
    bugnosis diagnose <repo> <issue-number>
    bugnosis generate-pr <repo> <issue-number> "<what-you-fixed>"
    bugnosis help

Examples:
    bugnosis scan pytorch/pytorch
    bugnosis scan-multi rust-lang/rust python/cpython --min-impact 80
    bugnosis list --min-impact 85
    bugnosis stats
    bugnosis diagnose microsoft/vscode 23991
    bugnosis generate-pr wireguard-gui 123 "Fixed snap package build"

Options:
    --min-impact N    Minimum impact score (0-100, default: 70)
    --details         Show additional details
    --token TOKEN     GitHub API token (or set GITHUB_TOKEN env var)
    --save            Save results to local database

Environment:
    GITHUB_TOKEN      GitHub personal access token for API
    GROQ_API_KEY      Groq API key for AI features
    
Note: Without a token, API rate limits are very low (60 requests/hour).
Get a token at: https://github.com/settings/tokens
""")
        return
        
    command = args[0]
    
    if command == 'diagnose':
        cmd_diagnose(args[1:])
        return
    elif command == 'generate-pr':
        cmd_generate_pr(args[1:])
        return
    elif command == 'scan-multi':
        cmd_scan_multi(args[1:])
        return
    elif command == 'list':
        cmd_list(args[1:])
        return
    elif command == 'stats':
        cmd_stats(args[1:])
        return
    elif command != 'scan':
        print(f"Unknown command: {command}")
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
    save_results = False
    token = os.environ.get('GITHUB_TOKEN')
    
    i = 2
    while i < len(args):
        if args[i] == '--min-impact' and i + 1 < len(args):
            min_impact = int(args[i + 1])
            i += 2
        elif args[i] == '--details':
            show_details = True
            i += 1
        elif args[i] == '--save':
            save_results = True
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
    
    if save_results and bugs:
        db = BugDatabase()
        db.save_bugs(bugs)
        db.close()
        print(f"Saved {len(bugs)} bugs to local database\n")
    
    print_bugs(bugs, show_details=show_details)
    
    if bugs:
        print(f"Total potential impact: ~{sum(b.affected_users for b in bugs):,} users")
        print(f"Average impact score: {sum(b.impact_score for b in bugs) // len(bugs)}/100")


if __name__ == '__main__':
    main()

