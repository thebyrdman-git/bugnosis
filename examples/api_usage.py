#!/usr/bin/env python3
"""
Bugnosis API Usage Examples

This file demonstrates how to use the Bugnosis Python API
for programmatic bug discovery and analysis.
"""

import os
from bugnosis import BugnosisAPI
from bugnosis.api import scan, diagnose, generate_pr_description


def example_1_basic_scan():
    """Example 1: Basic repository scan."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Repository Scan")
    print("=" * 60)
    
    # Initialize API
    api = BugnosisAPI(github_token=os.getenv('GITHUB_TOKEN'))
    
    # Scan a repository
    print("Scanning pytorch/pytorch for high-impact bugs...")
    bugs = api.scan_repo("pytorch/pytorch", min_impact=85)
    
    # Display results
    print(f"\nFound {len(bugs)} high-impact bugs:\n")
    for i, bug in enumerate(bugs[:5], 1):  # Show top 5
        print(f"{i}. {bug.title}")
        print(f"   Impact: {bug.impact_score}/100")
        print(f"   Users affected: ~{bug.affected_users:,}")
        print(f"   URL: {bug.url}\n")
    
    api.close()


def example_2_multi_repo_scan():
    """Example 2: Scan multiple repositories."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Multi-Repository Scan")
    print("=" * 60)
    
    repos = [
        "rust-lang/rust",
        "python/cpython",
        "pytorch/pytorch"
    ]
    
    with BugnosisAPI(github_token=os.getenv('GITHUB_TOKEN')) as api:
        print(f"Scanning {len(repos)} repositories...\n")
        bugs = api.scan_multiple_repos(repos, min_impact=80, save=True)
        
        # Group by repo
        by_repo = {}
        for bug in bugs:
            if bug.repo not in by_repo:
                by_repo[bug.repo] = []
            by_repo[bug.repo].append(bug)
        
        # Summary
        for repo, repo_bugs in by_repo.items():
            print(f"\n{repo}:")
            print(f"  High-impact bugs: {len(repo_bugs)}")
            total_users = sum(b.affected_users for b in repo_bugs)
            print(f"  Potential users helped: ~{total_users:,}")


def example_3_ai_diagnosis():
    """Example 3: AI-powered bug diagnosis."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: AI Bug Diagnosis")
    print("=" * 60)
    
    with BugnosisAPI(groq_key=os.getenv('GROQ_API_KEY')) as api:
        # Diagnose a specific bug
        repo = "pytorch/pytorch"
        issue_num = 12345
        
        print(f"\nAnalyzing issue #{issue_num} in {repo}...")
        diagnosis = api.diagnose_bug(repo, issue_num)
        
        if diagnosis:
            print("\nAI Diagnosis:")
            print("-" * 60)
            print(diagnosis)
        else:
            print("AI diagnosis unavailable (check GROQ_API_KEY)")


def example_4_generate_pr():
    """Example 4: Generate PR description."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Generate PR Description")
    print("=" * 60)
    
    with BugnosisAPI(groq_key=os.getenv('GROQ_API_KEY')) as api:
        repo = "pytorch/pytorch"
        issue_num = 12345
        fix = "Fixed memory leak in tensor allocation"
        
        print(f"\nGenerating PR description for issue #{issue_num}...")
        pr_desc = api.generate_pr(repo, issue_num, fix)
        
        if pr_desc:
            print("\nGenerated PR Description:")
            print("-" * 60)
            print(pr_desc)
        else:
            print("PR generation unavailable (check GROQ_API_KEY)")


def example_5_track_contributions():
    """Example 5: Track your contributions."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Track Your Contributions")
    print("=" * 60)
    
    with BugnosisAPI() as api:
        # Record a contribution
        api.record_contribution(
            repo="pytorch/pytorch",
            issue_number=12345,
            pr_number=67890,
            pr_url="https://github.com/pytorch/pytorch/pull/67890",
            impact_score=95,
            affected_users=100000
        )
        
        # Get stats
        stats = api.get_stats()
        
        print("\nYour Impact:")
        print(f"  Total contributions: {stats['total_contributions']}")
        print(f"  Users helped: {stats['total_users_helped']:,}")
        print(f"  Average impact: {stats['avg_impact_score']}/100")
        print(f"  Merged PRs: {stats['merged_count']}")
        
        # Calculate time saved
        hours_saved = stats['total_users_helped'] * 0.5
        print(f"  Time saved: ~{hours_saved:,.0f} hours")


def example_6_convenience_functions():
    """Example 6: Quick convenience functions."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Convenience Functions")
    print("=" * 60)
    
    # Quick scan without managing API object
    print("\nQuick scan using convenience function...")
    bugs = scan("pytorch/pytorch", min_impact=90, 
                github_token=os.getenv('GITHUB_TOKEN'))
    
    print(f"Found {len(bugs)} very high-impact bugs (90+)")
    
    if bugs:
        top = bugs[0]
        print(f"\nTop bug: {top.title}")
        print(f"Impact: {top.impact_score}/100")


def example_7_saved_bugs():
    """Example 7: Work with saved bugs."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Saved Bugs Database")
    print("=" * 60)
    
    with BugnosisAPI() as api:
        # Get all high-impact saved bugs
        saved = api.get_saved_bugs(min_impact=85)
        
        print(f"\nYou have {len(saved)} saved high-impact bugs")
        
        if saved:
            print("\nTop 3 saved bugs to fix:")
            for i, bug in enumerate(saved[:3], 1):
                print(f"{i}. [{bug['impact_score']}/100] {bug['title']}")
                print(f"   {bug['url']}")


if __name__ == "__main__":
    print("\nBugnosis API Examples")
    print("=" * 60)
    print("\nNote: Set GITHUB_TOKEN and GROQ_API_KEY environment")
    print("variables for full functionality.\n")
    
    # Run all examples
    try:
        example_1_basic_scan()
        example_2_multi_repo_scan()
        example_3_ai_diagnosis()
        example_4_generate_pr()
        example_5_track_contributions()
        example_6_convenience_functions()
        example_7_saved_bugs()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have set environment variables correctly.")


