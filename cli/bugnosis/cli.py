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
import json


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
        
        platform = get_platform(platform_name, **kwargs)
        
        # Search bugs
        bugs = platform.search_bugs(project, min_impact=min_impact)
        
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


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help']:
        print("""
Bugnosis - Find high-impact bugs to fix

Usage:
    bugnosis scan <repo> [options]
    bugnosis scan-multi <repo1> <repo2> ... [options]
    bugnosis scan-platform <platform> <project> [options]
    bugnosis platforms
    bugnosis list [--min-impact N]
    bugnosis stats
    bugnosis insights [--min-impact N]
    bugnosis watch add <repo>
    bugnosis watch list
    bugnosis watch scan
    bugnosis config get <key>
    bugnosis config set <key> <value>
    bugnosis export <format> <output-file> [--min-impact N]
    bugnosis leaderboard <output-file>
    bugnosis diagnose <repo> <issue-number>
    bugnosis generate-pr <repo> <issue-number> "<what-you-fixed>"
    bugnosis copilot <repo> <issue-number>
    bugnosis difficulty <repo> <issue-number>
    bugnosis clear-cache
    bugnosis help

Examples:
    # GitHub (default)
    bugnosis scan pytorch/pytorch
    
    # Other platforms
    bugnosis scan-platform gitlab gitlab-org/gitlab --min-impact 80
    bugnosis scan-platform bugzilla Firefox --instance mozilla
    bugnosis platforms
    
    # Multi-repo
    bugnosis scan-multi rust-lang/rust python/cpython --min-impact 80
    
    # Analysis
    bugnosis list --min-impact 85
    bugnosis stats
    bugnosis insights
    
    # Export
    bugnosis export json bugs.json --min-impact 85
    bugnosis leaderboard leaderboard.html
    
    # AI Features
    bugnosis copilot pytorch/pytorch 12345
    bugnosis difficulty rust-lang/rust 54321
    bugnosis diagnose microsoft/vscode 23991
    bugnosis generate-pr wireguard-gui 123 "Fixed snap package build"
    
    # Maintenance
    bugnosis clear-cache

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

