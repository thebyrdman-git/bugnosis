"""CLI interface for Bugnosis."""

import sys
import os
from typing import Optional
from .scanner import GitHubScanner
from .ai import AIEngine
from .github import GitHubClient
from .storage import BugDatabase
from .multi_scan import scan_multiple_repos
from .cache import APICache
from .export import (export_bugs_json, export_bugs_csv, export_bugs_markdown,
                     export_stats_json, export_leaderboard)
from .config import BugnosisConfig
from .analytics import generate_insights
from .copilot import BugFixCopilot
from .platforms import get_platform, list_platforms
from .plugins import PluginManager
from .auth import set_token, get_token, delete_token
import json
import getpass


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
    token = os.environ.get('GITHUB_TOKEN') or get_token('github')
    
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
    token = os.environ.get('GITHUB_TOKEN') or get_token('github')
    groq_key = os.environ.get('GROQ_API_KEY')
    
    if not groq_key:
        print("Debug: GROQ_API_KEY not found in environment variables.")
        # print(f"Debug: Env keys: {list(os.environ.keys())}")
    
    print(f"Generating PR description for issue #{issue_num}...")
    
    client = GitHubClient(token=token)
    issue = client.get_issue(repo, issue_num)
    
    if not issue:
        print("Error: Could not fetch issue")
        sys.exit(1)
        
    ai = AIEngine(api_key=groq_key)
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
    token = os.environ.get('GITHUB_TOKEN') or get_token('github')
    
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
    output_json = False
    
    i = 0
    while i < len(args):
        if args[i] == '--min-impact' and i + 1 < len(args):
            min_impact = int(args[i + 1])
            i += 2
        elif args[i] == '--json':
            output_json = True
            i += 1
        else:
            i += 1
            
    db = BugDatabase()
    bugs_data = db.get_bugs(min_impact=min_impact)
    db.close()
    
    if output_json:
        # Convert rows to dicts if they aren't already
        json_bugs = [dict(b) for b in bugs_data]
        print(json.dumps(json_bugs))
        return

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


def cmd_clear_cache(args):
    """Clear API cache."""
    cache = APICache()
    cache.clear()
    print("API cache cleared!")


def cmd_export(args):
    """Export bugs to file."""
    if len(args) < 2:
        print("Error: Format and output file required")
        print("Usage: bugnosis export <json|csv|markdown> <output-file> [--min-impact N]")
        sys.exit(1)
        
    format_type = args[0].lower()
    output_file = args[1]
    min_impact = 0
    
    # Parse options
    i = 2
    while i < len(args):
        if args[i] == '--min-impact' and i + 1 < len(args):
            min_impact = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    # Get bugs from database
    db = BugDatabase()
    bugs = db.get_bugs(min_impact=min_impact)
    db.close()
    
    if not bugs:
        print(f"No bugs found with impact >= {min_impact}")
        print("Run 'bugnosis scan <repo> --save' first")
        return
    
    # Export
    print(f"Exporting {len(bugs)} bugs to {output_file}...")
    
    if format_type == 'json':
        export_bugs_json(bugs, output_file)
    elif format_type == 'csv':
        export_bugs_csv(bugs, output_file)
    elif format_type == 'markdown' or format_type == 'md':
        export_bugs_markdown(bugs, output_file)
    else:
        print(f"Error: Unknown format '{format_type}'")
        print("Supported formats: json, csv, markdown")
        sys.exit(1)
    
    print(f"Exported successfully!")
    print(f"Total bugs: {len(bugs)}")
    print(f"Total potential impact: ~{sum(b['affected_users'] for b in bugs):,} users")


def cmd_leaderboard(args):
    """Generate leaderboard HTML."""
    if len(args) < 1:
        print("Error: Output file required")
        print("Usage: bugnosis leaderboard <output-file.html>")
        sys.exit(1)
        
    output_file = args[0]
    
    db = BugDatabase()
    contributions = db.conn.execute(
        'SELECT * FROM contributions ORDER BY submitted_at DESC'
    ).fetchall()
    contributions = [dict(row) for row in contributions]
    db.close()
    
    if not contributions:
        print("No contributions recorded yet")
        print("Use 'bugnosis record-contribution' or the API to track contributions")
        return
    
    print(f"Generating leaderboard with {len(contributions)} contributions...")
    export_leaderboard(contributions, output_file)
    print(f"Leaderboard generated: {output_file}")
    print(f"Open in browser: file://{os.path.abspath(output_file)}")


def cmd_insights(args):
    """Generate insights from saved bugs."""
    min_impact = 0
    
    # Parse options
    i = 0
    while i < len(args):
        if args[i] == '--min-impact' and i + 1 < len(args):
            min_impact = int(args[i + 1])
            i += 2
        else:
            i += 1
            
    db = BugDatabase()
    bugs = db.get_bugs(min_impact=min_impact)
    db.close()
    
    if not bugs:
        print(f"No bugs found with impact >= {min_impact}")
        print("Run 'bugnosis scan <repo> --save' first")
        return
        
    print(generate_insights(bugs))


def cmd_watch(args):
    """Manage watched repositories."""
    if len(args) < 1:
        print("Error: Subcommand required")
        print("Usage: bugnosis watch <add|list|scan> [args]")
        sys.exit(1)
        
    subcommand = args[0]
    config = BugnosisConfig()
    
    if subcommand == 'add':
        if len(args) < 2:
            print("Error: Repository required")
            print("Usage: bugnosis watch add <repo>")
            sys.exit(1)
        repo = args[1]
        config.add_watched_repo(repo)
        config.save()
        print(f"Added {repo} to watch list")
        
    elif subcommand == 'remove':
        if len(args) < 2:
            print("Error: Repository required")
            print("Usage: bugnosis watch remove <repo>")
            sys.exit(1)
        repo = args[1]
        config.remove_watched_repo(repo)
        config.save()
        print(f"Removed {repo} from watch list")
        
    elif subcommand == 'list':
        repos = config.get_watched_repos()
        if not repos:
            print("No repositories being watched")
            print("Add with: bugnosis watch add <repo>")
        else:
            print(f"Watching {len(repos)} repositories:\n")
            for repo in repos:
                print(f"  - {repo}")
                
    elif subcommand == 'scan':
        repos = config.get_watched_repos()
        if not repos:
            print("No repositories to scan")
            print("Add with: bugnosis watch add <repo>")
            return
            
        min_impact = config.get('min_impact', 70)
        print(f"Scanning {len(repos)} watched repositories...\n")
        
        bugs = scan_multiple_repos(repos, min_impact=min_impact, 
                                  token=config.get_github_token())
        
        db = BugDatabase()
        db.save_bugs(bugs)
        db.close()
        
        print(f"\nFound {len(bugs)} high-impact bugs")
        print(f"Total potential impact: ~{sum(b.affected_users for b in bugs):,} users")
        print(f"\nRun 'bugnosis list --min-impact {min_impact}' to see all")
        
    else:
        print(f"Unknown subcommand: {subcommand}")
        print("Available: add, remove, list, scan")


def cmd_config(args):
    """Manage configuration."""
    if len(args) < 1:
        print("Error: Subcommand required")
        print("Usage: bugnosis config <get|set> <key> [value]")
        sys.exit(1)
        
    subcommand = args[0]
    config = BugnosisConfig()
    
    if subcommand == 'get':
        if len(args) < 2:
            # Show all config
            print("Current configuration:")
            print(json.dumps(config.config, indent=2))
        else:
            key = args[1]
            value = config.get(key)
            print(f"{key}: {value}")
            
    elif subcommand == 'set':
        if len(args) < 3:
            print("Error: Key and value required")
            print("Usage: bugnosis config set <key> <value>")
            sys.exit(1)
        key = args[1]
        value = args[2]
        
        # Try to parse value as JSON for complex types
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass  # Keep as string
            
        config.set(key, value)
        config.save()
        print(f"Set {key} = {value}")
        
    else:
        print(f"Unknown subcommand: {subcommand}")
        print("Available: get, set")


def cmd_copilot(args):
    """AI Co-Pilot for guided bug fixing."""
    if len(args) < 2:
        print("Error: Repository and issue number required")
        print("Usage: bugnosis copilot owner/repo issue-number")
        sys.exit(1)
        
    repo = args[0]
    issue_num = int(args[1])
    token = os.environ.get('GITHUB_TOKEN')
    groq_key = os.environ.get('GROQ_API_KEY')
    
    if not groq_key:
        print("Error: GROQ_API_KEY required for AI Co-Pilot")
        print("\nGet your free API key:")
        print("1. Visit: https://console.groq.com/keys")
        print("2. Create account (free)")
        print("3. Generate API key")
        print("4. Export: export GROQ_API_KEY=your_key")
        sys.exit(1)
    
    print(f"\n🤖 Starting AI Co-Pilot for {repo}#{issue_num}...\n")
    
    # Fetch issue
    client = GitHubClient(token=token)
    issue = client.get_issue(repo, issue_num)
    
    if not issue:
        print(f"Error: Could not fetch issue #{issue_num}")
        sys.exit(1)
    
    # Initialize Co-Pilot
    copilot = BugFixCopilot(api_key=groq_key)
    
    print("="*70)
    print(f"Issue: {issue['title']}")
    print(f"URL: {issue.get('html_url', 'N/A')}")
    print("="*70)
    print()
    
    # Step 1: Analyze
    print("📊 Step 1: Deep Analysis")
    print("-" * 70)
    analysis = copilot.analyze_bug(issue)
    
    if analysis.get('success'):
        print(analysis['analysis'])
        print()
    else:
        print(f"Error: {analysis.get('error')}")
        sys.exit(1)
    
    # Ask user to continue
    response = input("\n👉 Continue to difficulty estimation? (y/n): ")
    if response.lower() != 'y':
        print("Co-Pilot session ended.")
        return
    
    # Step 2: Difficulty
    print("\n⚡ Step 2: Difficulty Estimation")
    print("-" * 70)
    difficulty = copilot.estimate_difficulty(issue)
    
    if difficulty.get('success'):
        print(difficulty['estimate'])
        print()
    else:
        print(f"Error: {difficulty.get('error')}")
    
    print("\n" + "="*70)
    print("🎯 Co-Pilot Analysis Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Clone the repository")
    print("2. Create a new branch")
    print("3. Use the analysis above to implement the fix")
    print("4. Test your changes")
    print(f"5. Run: bugnosis generate-pr {repo} {issue_num} 'Your fix description'")
    print()
    print("💡 Tip: The Co-Pilot analyzed the bug for you. You implement the fix!")
    print("     This keeps YOU in control while AI does the research.")


def cmd_difficulty(args):
    """Estimate bug difficulty."""
    if len(args) < 2:
        print("Error: Repository and issue number required")
        print("Usage: bugnosis difficulty owner/repo issue-number")
        sys.exit(1)
        
    repo = args[0]
    issue_num = int(args[1])
    token = os.environ.get('GITHUB_TOKEN')
    groq_key = os.environ.get('GROQ_API_KEY')
    
    if not groq_key:
        print("Error: GROQ_API_KEY required for difficulty estimation")
        sys.exit(1)
    
    # Fetch issue
    client = GitHubClient(token=token)
    issue = client.get_issue(repo, issue_num)
    
    if not issue:
        print(f"Error: Could not fetch issue #{issue_num}")
        sys.exit(1)
    
    print(f"\nEstimating difficulty for: {issue['title']}\n")
    
    copilot = BugFixCopilot(api_key=groq_key)
    result = copilot.estimate_difficulty(issue)
    
    if result.get('success'):
        print(result['estimate'])
        print(f"\n📊 Difficulty Level: {result['difficulty']}")
    else:
        print(f"Error: {result.get('error')}")


def cmd_scan_platform(args):
    """Scan a bug tracking platform."""
    if len(args) < 2:
        print("Error: Platform and project required")
        print("Usage: bugnosis scan-platform <platform> <project> [options]")
        print("\nAvailable platforms:")
        for platform in list_platforms():
            print(f"  - {platform}")
        sys.exit(1)
    
    platform_name = args[0]
    project = args[1]
    
    # Parse options
    min_impact = 70
    save_results = False
    instance = None
    mode = "normal"
    
    i = 2
    while i < len(args):
        if args[i] == '--min-impact' and i + 1 < len(args):
            min_impact = int(args[i + 1])
            i += 2
        elif args[i] == '--save':
            save_results = True
            i += 1
        elif args[i] == '--instance' and i + 1 < len(args):
            instance = args[i + 1]
            i += 2
        elif args[i] == '--novice':
            mode = "novice"
            # Adjust default min_impact for novice mode if user didn't set it
            if min_impact == 70:
                min_impact = 50 
            i += 1
        else:
            i += 1
    
    print(f"\n🔍 Scanning {platform_name.upper()}: {project}")
    print(f"   Minimum impact: {min_impact}")
    print()
    
    try:
        # Initialize platform
        kwargs = {}
        if instance:
            kwargs['instance'] = instance
            
        # Get token for platform
        token_key = f"{platform_name}_token".upper()
        token = os.environ.get(token_key) or get_token(platform_name)
        if token:
            kwargs['token'] = token
        
        platform = get_platform(platform_name, **kwargs)
        
        # Search bugs
        bugs = platform.search_bugs(project, min_impact=min_impact, mode=mode)
        
        if not bugs:
            print(f"No bugs found with impact >= {min_impact}")
            return
        
        print(f"Found {len(bugs)} high-impact bugs:\n")
        
        # Print bugs
        for i, bug in enumerate(bugs, 1):
            # Impact indicator
            if bug.impact_score >= 90:
                indicator = "🔴"
            elif bug.impact_score >= 80:
                indicator = "🟠"
            else:
                indicator = "🟡"
            
            print(f"{indicator} [{i}] {bug.title}")
            print(f"    Platform: {bug.platform}")
            print(f"    Impact: {bug.impact_score}/100 | Users: ~{bug.affected_users:,}")
            print(f"    Severity: {bug.severity} | Status: {bug.status}")
            print(f"    URL: {bug.url}")
            print()
        
        # Save if requested
        if save_results:
            db = BugDatabase()
            for bug in bugs:
                db.save_bug(
                    repo=f"{bug.platform}:{bug.repo}",
                    issue_number=bug.issue_number,
                    title=bug.title,
                    url=bug.url,
                    impact_score=bug.impact_score,
                    affected_users=bug.affected_users,
                    severity=bug.severity,
                    labels=bug.labels,
                    comments=bug.comments_count,
                    created_at=bug.created_at.isoformat() if bug.created_at else None,
                    updated_at=bug.updated_at.isoformat() if bug.updated_at else None
                )
            db.close()
            print(f"✅ Saved {len(bugs)} bugs to database")
        
        # Print summary
        print("\n" + "="*60)
        print(f"Total bugs found: {len(bugs)}")
        total_users = sum(bug.affected_users for bug in bugs)
        print(f"Potential users helped: ~{total_users:,}")
        avg_impact = sum(bug.impact_score for bug in bugs) / len(bugs)
        print(f"Average impact: {avg_impact:.1f}/100")
        print("="*60)
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error scanning platform: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_platforms():
    """List available bug tracking platforms."""
    print("\n🌐 Available Bug Tracking Platforms:\n")
    
    print("1. GitHub (github)")
    print("   - Default platform")
    print("   - Usage: bugnosis scan owner/repo")
    print()
    
    print("2. GitLab (gitlab)")
    print("   - GitLab.com and self-hosted instances")
    print("   - Usage: bugnosis scan-platform gitlab owner/repo")
    print("   - Token: GITLAB_TOKEN environment variable")
    print()
    
    print("3. Bugzilla (bugzilla)")
    print("   - Mozilla, Red Hat, KDE, GNOME, Kernel.org")
    print("   - Usage: bugnosis scan-platform bugzilla ProductName --instance mozilla")
    print("   - Instances: mozilla, redhat, kde, gnome, kernel")
    print("   - Token: BUGZILLA_TOKEN environment variable")
    print()
    
    print("Examples:")
    print("  bugnosis scan pytorch/pytorch")
    print("  bugnosis scan-platform gitlab gitlab-org/gitlab")
    print("  bugnosis scan-platform bugzilla Firefox --instance mozilla")
    print()
    
    print("Coming soon: Jira, Launchpad, SourceForge, Bitbucket")
    print()


def cmd_smart_scan(args):
    """AI-powered smart scan that resolves platform from query."""
    if len(args) < 1:
        print("Error: Query required")
        print("Usage: bugnosis smart-scan \"query\" [options]")
        sys.exit(1)
        
    query = args[0]
    min_impact = 70
    
    i = 1
    while i < len(args):
        if args[i] == '--min-impact' and i + 1 < len(args):
            min_impact = int(args[i + 1])
            i += 2
        else:
            i += 1
            
    print(f"Analyzing query: '{query}'...")
    
    # Resolve target
    ai = AIEngine()
    target = ai.resolve_target(query)
    
    platform_name = target.get('platform', 'github')
    project = target.get('target')
    instance = target.get('instance')
    
    if not project:
        print("Could not resolve repository from query.")
        sys.exit(1)
        
    print(f"🎯 Target Resolved: {platform_name.upper()} -> {project}")
    if instance:
        print(f"   Instance: {instance}")
        
    # Delegate to platform scan
    scan_args = [platform_name, project, '--min-impact', str(min_impact)]
    if instance:
        scan_args.extend(['--instance', instance])
        
    # Add --save by default for smart scans in GUI context? 
    # No, let user decide or GUI pass flag. GUI doesn't pass --save currently.
    
    cmd_scan_platform(scan_args)


def cmd_search(args):
    """Federated search across multiple platforms."""
    if len(args) < 1:
        print("Error: Query required")
        print("Usage: bugnosis search \"query\" [options]")
        sys.exit(1)
        
    query = args[0]
    min_impact = 70
    save_results = False
    
    i = 1
    while i < len(args):
        if args[i] == '--min-impact' and i + 1 < len(args):
            min_impact = int(args[i + 1])
            i += 2
        elif args[i] == '--save':
            save_results = True
            i += 1
        else:
            i += 1
            
    print(f"🔎 Searching bug ecosystem for: '{query}'")
    print(f"   Minimum impact: {min_impact}")
    print()
    
    from .federated import FederatedSearch
    
    engine = FederatedSearch(min_impact=min_impact)
    results = engine.search(query)
    
    bugs = results.get('results', [])
    stats = results.get('stats', {})
    targets = results.get('targets_scanned', [])
    
    # Show targets scanned
    print("Targets identified:")
    for t in targets:
        print(f" - {t['platform'].upper()}: {t['target']}")
    print()
    
    if not bugs:
        print(f"No high-impact bugs found for '{query}'.")
        return
        
    # Show results
    print(f"Found {len(bugs)} opportunities across platforms:\n")
    
    for i, bug in enumerate(bugs, 1):
        # Impact indicator
        if bug.impact_score >= 90:
            indicator = "🔥"
        elif bug.impact_score >= 80:
            indicator = "⭐"
        else:
            indicator = "✨"
        
        # Platform icon
        plat_icon = "🐙" if bug.platform == 'github' else "🦊" if bug.platform == 'gitlab' else "🐛"
        
        print(f"{indicator} [{i}] {bug.title}")
        print(f"    {plat_icon} {bug.platform.upper()} | {bug.repo}")
        print(f"    Impact: {bug.impact_score}/100 | Users: ~{bug.affected_users:,}")
        print(f"    Severity: {bug.severity} | Status: {bug.status}")
        print(f"    URL: {bug.url}")
        print()
        
    # Show stats
    print("="*60)
    print("Source Breakdown:")
    for platform, count in stats.items():
        if count > 0:
            print(f"  {platform.capitalize()}: {count}")
    print(f"\nTotal: {len(bugs)} bugs")
    print("="*60)
    
    if save_results:
        db = BugDatabase()
        for bug in bugs:
            db.save_bug(
                repo=f"{bug.platform}:{bug.repo}",
                issue_number=bug.issue_number,
                title=bug.title,
                url=bug.url,
                impact_score=bug.impact_score,
                affected_users=bug.affected_users,
                severity=bug.severity,
                labels=bug.labels,
                comments=bug.comments_count,
                created_at=bug.created_at.isoformat() if bug.created_at else None,
                updated_at=bug.updated_at.isoformat() if bug.updated_at else None
            )
        db.close()
        print(f"\n✅ Saved {len(bugs)} bugs to database")


def cmd_plugins(args):
    """Manage plugins."""
    if len(args) < 1:
        # List plugins
        manager = PluginManager()
        manager.load_plugins()
        plugins = manager.list_plugins()
        
        print("\n🧩 Installed Plugins:\n")
        if not plugins:
            print("No plugins installed.")
            print("Drop .py files into ~/.bugnosis/plugins/ to extend functionality.")
            return
            
        for p in plugins:
            print(f"- {p['name']} (v{p['version']})")
            print(f"  {p['description']}")
        print()
        return

    print("Plugin management commands coming soon.")


def cmd_coach(args):
    """AI Rejection Coaching (Post-Mortem)."""
    if len(args) < 2:
        print("Error: Repository and PR number required")
        print("Usage: bugnosis coach owner/repo pr-number")
        sys.exit(1)
        
    repo = args[0]
    pr_num = int(args[1])
    token = os.environ.get('GITHUB_TOKEN') or get_token('github')
    groq_key = os.environ.get('GROQ_API_KEY')
    
    if not groq_key:
        print("Error: GROQ_API_KEY required for AI Coaching")
        sys.exit(1)

    print(f"\n🎓 Analyzing Rejected PR #{pr_num} for coaching...\n")

    client = GitHubClient(token=token)
    
    # We need PR details and review comments
    # GitHubClient needs to be extended or we use raw requests here for speed
    # For now, let's assume we can get basic PR data
    # Implementing a quick fetch here to avoid huge refactor of GitHubClient right now
    
    import requests
    headers = {'Authorization': f'token {token}'} if token else {}
    
    try:
        # Get PR
        pr_resp = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pr_num}", headers=headers)
        if pr_resp.status_code != 200:
            print(f"Error fetching PR: {pr_resp.status_code}")
            return
        pr_data = pr_resp.json()
        
        # Check if actually closed/merged
        if pr_data['state'] == 'open':
            print("⚠️ This PR is still Open! Coaching is for rejected/closed PRs.")
            print("Good luck! You got this!")
            return
        if pr_data.get('merged_at'):
            print("🎉 This PR was merged! No coaching needed. You are a Hero!")
            return

        # Get Reviews/Comments
        comments_resp = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pr_num}/reviews", headers=headers)
        reviews = comments_resp.json() if comments_resp.status_code == 200 else []
        
        # Also get issue comments
        issue_comments_resp = requests.get(f"https://api.github.com/repos/{repo}/issues/{pr_num}/comments", headers=headers)
        issue_comments = issue_comments_resp.json() if issue_comments_resp.status_code == 200 else []

        all_comments = reviews + issue_comments

        # Analyze
        ai = AIEngine(api_key=groq_key)
        coaching = ai.analyze_rejection(pr_data, all_comments)

        if 'error' in coaching:
            print(f"Error: {coaching['error']}")
            return

        print("=" * 60)
        print(f"🛡️  REJECTION POST-MORTEM: {repo}#{pr_num}")
        print("=" * 60)
        print(f"\n🔴 Root Cause: {coaching.get('reason', 'Unknown')}")
        print(f"\n🧐 Analysis:\n{coaching.get('analysis')}")
        
        print("\n💡 Actionable Advice:")
        if isinstance(coaching.get('advice'), list):
            for tip in coaching['advice']:
                print(f"  - {tip}")
        else:
            print(coaching.get('advice'))
            
        print(f"\n🦁 Coach says: \"{coaching.get('encouragement')}\"")
        print("\n" + "=" * 60)
        print("Every rejection is just XP for the next level. Keep hunting.")

    except Exception as e:
        print(f"Error: {e}")


def cmd_auth(args):
    """Manage authentication."""
    if len(args) < 1:
        print("Error: Action required")
        print("Usage: bugnosis auth <login|logout|status> [platform]")
        sys.exit(1)
        
    action = args[0]
    platform = args[1] if len(args) > 1 else 'github'
    
    if action == 'login':
        print(f"Authenticating with {platform}...")
        print("Tip: Create a Personal Access Token (PAT) with 'repo' scope.")
        
        if platform == 'github':
            print("URL: https://github.com/settings/tokens/new")
        elif platform == 'gitlab':
            print("URL: https://gitlab.com/-/profile/personal_access_tokens")
            
        token = getpass.getpass(f"Enter {platform} token: ").strip()
        
        if not token:
            print("Error: Token cannot be empty")
            return
            
        # TODO: Validate token by making a test API call
        set_token(platform, token)
        print(f"✅ Successfully authenticated with {platform}!")
        
    elif action == 'logout':
        delete_token(platform)
        print(f"Logged out of {platform}")
        
    elif action == 'status':
        token = get_token(platform)
        if token:
            print(f"✅ {platform}: Authenticated")
        else:
            print(f"❌ {platform}: Not authenticated")
            
    else:
        print(f"Unknown action: {action}")


def cmd_sandbox(args):
    """Run a repository in a Podman sandbox."""
    if len(args) < 1:
        print("Error: Repository required")
        print("Usage: bugnosis sandbox <owner/repo>")
        sys.exit(1)
        
    repo = args[0]
    print(f"📦 Preparing sandbox for {repo}...")
    
    # Check for podman
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path
    
    podman_cmd = shutil.which("podman")
    if not podman_cmd:
        print("Error: 'podman' not found. Please install Podman first.")
        return

    # Create temp dir
    # We use a try/finally block with mkdtemp manually or just TemporaryDirectory
    # TemporaryDirectory is safer for cleanup
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            repo_name = repo.split('/')[-1]
            repo_path = work_dir / repo_name
            
            print(f"1. Cloning {repo}...")
            # Using https clone for simplicity
            subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", str(repo_path)], check=True)
            
            print("2. Detecting language...")
            # Simple heuristic
            language = "Unknown (Generic Linux)"
            base_image = "registry.fedoraproject.org/fedora:latest"
            build_cmds = []
            
            if (repo_path / "Cargo.toml").exists():
                language = "Rust"
                base_image = "docker.io/library/rust:latest"
                build_cmds = ["cargo build"]
            elif (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists():
                language = "Python"
                base_image = "docker.io/library/python:3.11"
                if (repo_path / "requirements.txt").exists():
                    build_cmds = ["pip install -r requirements.txt"]
                else:
                    build_cmds = ["pip install ."]
            elif (repo_path / "package.json").exists():
                language = "Node.js"
                base_image = "docker.io/library/node:20"
                build_cmds = ["npm install"]
            elif (repo_path / "go.mod").exists():
                language = "Go"
                base_image = "docker.io/library/golang:1.21"
                build_cmds = ["go build ./..."]
            elif (repo_path / "Makefile").exists():
                language = "C/C++ (Makefile)"
                base_image = "registry.fedoraproject.org/fedora:latest"
                build_cmds = ["dnf install -y make gcc", "make"]

            print(f"   Detected: {language}")
            
            print("3. Generating Containerfile...")
            containerfile_content = f"""
FROM {base_image}
WORKDIR /app
COPY . .
"""
            # Add build commands
            for cmd in build_cmds:
                 containerfile_content += f"RUN {cmd}\n"
                 
            containerfile_content += 'CMD ["/bin/bash"]\n'
            
            containerfile_path = repo_path / "Containerfile"
            with open(containerfile_path, "w") as f:
                f.write(containerfile_content)
                
            print("4. Building sandbox image...")
            image_tag = f"bugnosis-sandbox-{repo_name.lower()}"
            # capture_output=True to keep it clean, or let it stream so user sees progress?
            # Stream is better for "demo" feeling of work happening
            subprocess.run(["podman", "build", "-t", image_tag, "-f", "Containerfile", "."], cwd=repo_path, check=True)
            
            print(f"5. Launching sandbox ({image_tag})...")
            print("   (Type 'exit' to return to Bugnosis)")
            print("-" * 50)
            
            subprocess.run(["podman", "run", "-it", "--rm", image_tag], check=False)
            
    except subprocess.CalledProcessError as e:
        print(f"Error during sandbox creation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        
    print("-" * 50)
    print("Sandbox session ended. Cleaned up temporary files.")


def cmd_doctor(args):
    """System health check for developers."""
    print("\n🩺  Bugnosis Doctor: System Health Check\n")
    
    # 1. Python Environment
    import platform
    print(f"✅ Python: {platform.python_version()}")
    
    # 2. Authentication
    print("\n🔐 Authentication:")
    for svc in ['github', 'gitlab', 'bugzilla']:
        if get_token(svc):
            print(f"   ✅ {svc.capitalize()}: Token found")
        elif os.environ.get(f"{svc.upper()}_TOKEN"):
            print(f"   ✅ {svc.capitalize()}: Env var set")
        else:
            print(f"   ❌ {svc.capitalize()}: No token (Rate limits will be tight)")
            
    # 3. External Tools
    import shutil
    print("\n🛠  External Tools:")
    
    podman = shutil.which("podman")
    if podman:
        print(f"   ✅ Podman: Found at {podman}")
    else:
        print("   ❌ Podman: Not found (Sandbox features disabled)")
        
    git = shutil.which("git")
    if git:
        print(f"   ✅ Git: Found at {git}")
    else:
        print("   ❌ Git: Not found (Required for Co-Pilot)")
        
    # 4. AI Connectivity
    print("\n🧠 AI Services:")
    if os.environ.get("GROQ_API_KEY"):
        print("   ✅ Groq API: Key configured")
    else:
        print("   ❌ Groq API: Key missing (AI features disabled)")
        
    # 5. Database
    try:
        db = BugDatabase()
        stats = db.get_stats()
        db.close()
        print(f"\n💾 Database: Connected ({stats['total_contributions']} contributions tracked)")
    except Exception as e:
        print(f"\n❌ Database: Error connecting ({e})")
        
    print("\n" + "="*60)
    if not podman or not os.environ.get("GROQ_API_KEY"):
        print("⚠️  Setup incomplete for Power User features.")
    else:
        print("✨ System ready for high-impact engineering.")


def cmd_sync(args):
    """Cloud Sync: Backup/Restore your Hero Profile."""
    if len(args) < 1:
        print("Error: Action required")
        print("Usage: bugnosis sync <push|pull> [gist-id]")
        sys.exit(1)
        
    action = args[0]
    gist_id = args[1] if len(args) > 1 else None
    
    # Get config to see if we have a saved gist_id
    config = BugnosisConfig()
    if not gist_id:
        gist_id = config.get('sync_gist_id')
        
    token = get_token('github')
    if not token:
        print("Error: Authentication required. Run 'bugnosis auth login github'")
        return
        
    client = GitHubClient(token=token)
    db = BugDatabase()
    
    if action == 'push':
        print("☁️  Pushing Hero Profile to Cloud...")
        json_data = db.export_profile_json()
        
        files = {
            'bugnosis_profile.json': {'content': json_data}
        }
        
        if gist_id:
            print(f"Updating existing Gist: {gist_id}")
            resp = client.update_gist(gist_id, files)
        else:
            print("Creating new private Gist...")
            user = client.get_user()
            desc = f"Bugnosis Hero Profile for {user.get('login', 'User')}"
            resp = client.create_gist(files, desc, public=False)
            
        if resp:
            new_id = resp['id']
            config.set('sync_gist_id', new_id)
            config.save()
            print(f"✅ Sync Complete! Gist ID: {new_id}")
            print("Use this ID to pull on another machine.")
        else:
            print("❌ Sync failed.")
            
    elif action == 'pull':
        if not gist_id:
            print("Error: Gist ID required for first pull")
            print("Usage: bugnosis sync pull <gist-id>")
            return
            
        print(f"☁️  Pulling Hero Profile from Gist: {gist_id}...")
        gist = client.get_gist(gist_id)
        
        if gist and 'bugnosis_profile.json' in gist['files']:
            content = gist['files']['bugnosis_profile.json']['content']
            if db.import_profile_json(content):
                config.set('sync_gist_id', gist_id)
                config.save()
                print("✅ Profile Restored! Your XP and badges are back.")
            else:
                print("❌ Restore failed (Import Error)")
        else:
            print("❌ Restore failed (Gist not found or invalid format)")
            
    db.close()


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help']:
        print("""
Bugnosis - The Hero Engine for Open Source

Core Workflow:
    bugnosis scan <repo>            Scan a GitHub repository
    bugnosis smart-scan "query"     Find bugs across all platforms (AI)
    bugnosis search "query"         Federated search (GitHub + GitLab + Bugzilla)
    bugnosis list                   View saved opportunities
    bugnosis stats                  View your impact dashboard

Developer Tools:
    bugnosis copilot <repo> <id>    AI-assisted bug fixing
    bugnosis coach <repo> <id>      AI post-mortem for rejected PRs
    bugnosis sandbox <repo>         Launch Podman test environment
    bugnosis generate-pr            Draft a PR description
    bugnosis diagnose               AI root cause analysis

Configuration:
    bugnosis auth <login|status>    Manage API tokens securely
    bugnosis sync <push|pull>       Backup profile to GitHub Gist
    bugnosis watch <add|scan>       Monitor repositories
    bugnosis plugins                Manage external modules
    bugnosis config <get|set>       Tweaks (min_impact, theme)
    bugnosis doctor                 Check system health & dependencies

API Power Users:
    Python:  from bugnosis.api import BugnosisAPI
    Export:  bugnosis export json bugs.json
    
Run 'bugnosis help' for detailed options.
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
    elif command == 'clear-cache':
        cmd_clear_cache(args[1:])
        return
    elif command == 'export':
        cmd_export(args[1:])
        return
    elif command == 'leaderboard':
        cmd_leaderboard(args[1:])
        return
    elif command == 'insights':
        cmd_insights(args[1:])
        return
    elif command == 'watch':
        cmd_watch(args[1:])
        return
    elif command == 'config':
        cmd_config(args[1:])
        return
    elif command == 'copilot':
        cmd_copilot(args[1:])
        return
    elif command == 'difficulty':
        cmd_difficulty(args[1:])
        return
    elif command == 'scan-platform':
        cmd_scan_platform(args[1:])
        return
    elif command == 'platforms':
        cmd_platforms()
        return
    elif command == 'plugins':
        cmd_plugins(args[1:])
        return
    elif command == 'auth':
        cmd_auth(args[1:])
        return
    elif command == 'sync':
        cmd_sync(args[1:])
        return
    elif command == 'coach':
        cmd_coach(args[1:])
        return
    elif command == 'doctor':
        cmd_doctor(args[1:])
        return
    elif command == 'sandbox':
        cmd_sandbox(args[1:])
        return
    elif command == 'smart-scan':
        cmd_smart_scan(args[1:])
        return
    elif command == 'search':
        cmd_search(args[1:])
        return
    elif command == 'scan':
        # Legacy alias for scan-platform github
        if len(args) < 2:
            print("Error: Repository required")
            print("Usage: bugnosis scan <owner/repo> [options]")
            sys.exit(1)
            
        # Redirect to unified platform scanner
        new_args = ['github'] + args[1:]
        cmd_scan_platform(new_args)
        return

    else:
        print(f"Unknown command: {command}")
        print("Run 'bugnosis help' for usage")
        sys.exit(1)

if __name__ == '__main__':
    main()

