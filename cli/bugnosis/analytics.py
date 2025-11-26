"""Analytics and insights for bug data."""

from typing import List, Dict, Optional
from collections import defaultdict, Counter


class BugAnalytics:
    """Analytics engine for bug data."""
    
    def __init__(self, bugs: List[Dict]):
        """
        Initialize analytics with bug data.
        
        Args:
            bugs: List of bug dictionaries
        """
        self.bugs = bugs
        
    def by_repo(self) -> Dict[str, List[Dict]]:
        """Group bugs by repository."""
        grouped = defaultdict(list)
        for bug in self.bugs:
            grouped[bug['repo']].append(bug)
        return dict(grouped)
        
    def by_severity(self) -> Dict[str, List[Dict]]:
        """Group bugs by severity."""
        grouped = defaultdict(list)
        for bug in self.bugs:
            grouped[bug.get('severity', 'unknown')].append(bug)
        return dict(grouped)
        
    def top_impact_repos(self, n: int = 10) -> List[tuple]:
        """
        Get top N repositories by total impact.
        
        Returns:
            List of (repo, total_users, bug_count) tuples
        """
        by_repo = self.by_repo()
        
        repo_stats = []
        for repo, repo_bugs in by_repo.items():
            total_users = sum(b['affected_users'] for b in repo_bugs)
            repo_stats.append((repo, total_users, len(repo_bugs)))
            
        return sorted(repo_stats, key=lambda x: x[1], reverse=True)[:n]
        
    def impact_distribution(self) -> Dict[str, int]:
        """
        Get distribution of bugs by impact level.
        
        Returns:
            Dictionary with counts for each impact level
        """
        distribution = {
            'critical (90-100)': 0,
            'high (80-89)': 0,
            'significant (70-79)': 0,
            'moderate (60-69)': 0,
            'low (<60)': 0
        }
        
        for bug in self.bugs:
            score = bug['impact_score']
            if score >= 90:
                distribution['critical (90-100)'] += 1
            elif score >= 80:
                distribution['high (80-89)'] += 1
            elif score >= 70:
                distribution['significant (70-79)'] += 1
            elif score >= 60:
                distribution['moderate (60-69)'] += 1
            else:
                distribution['low (<60)'] += 1
                
        return distribution
        
    def total_potential_impact(self) -> Dict[str, int]:
        """Calculate total potential impact metrics."""
        if not self.bugs:
            return {
                'total_bugs': 0,
                'total_users': 0,
                'total_hours_saved': 0,
                'avg_impact': 0
            }
            
        total_users = sum(b['affected_users'] for b in self.bugs)
        total_hours = total_users * 0.5  # 30 min per user
        avg_impact = sum(b['impact_score'] for b in self.bugs) // len(self.bugs)
        
        return {
            'total_bugs': len(self.bugs),
            'total_users': total_users,
            'total_hours_saved': int(total_hours),
            'avg_impact': avg_impact
        }
        
    def recommend_next_fix(self) -> Optional[Dict]:
        """
        Recommend the next bug to fix based on impact and difficulty.
        
        Returns:
            Bug dictionary or None
        """
        if not self.bugs:
            return None
            
        # Sort by impact score
        sorted_bugs = sorted(self.bugs, key=lambda b: b['impact_score'], reverse=True)
        
        # Return highest impact bug
        return sorted_bugs[0]
        
    def summary(self) -> str:
        """Generate text summary of analytics."""
        if not self.bugs:
            return "No bugs to analyze"
            
        impact = self.total_potential_impact()
        distribution = self.impact_distribution()
        top_repos = self.top_impact_repos(5)
        
        summary = []
        summary.append("Bug Analysis Summary")
        summary.append("=" * 50)
        summary.append(f"\nTotal bugs: {impact['total_bugs']}")
        summary.append(f"Potential users helped: ~{impact['total_users']:,}")
        summary.append(f"Potential time saved: ~{impact['total_hours_saved']:,} hours")
        summary.append(f"Average impact score: {impact['avg_impact']}/100")
        
        summary.append("\n\nImpact Distribution:")
        summary.append("-" * 50)
        for level, count in distribution.items():
            if count > 0:
                summary.append(f"{level}: {count} bugs")
                
        summary.append("\n\nTop Repositories by Impact:")
        summary.append("-" * 50)
        for i, (repo, users, count) in enumerate(top_repos, 1):
            summary.append(f"{i}. {repo}")
            summary.append(f"   Bugs: {count} | Users: ~{users:,}")
            
        recommended = self.recommend_next_fix()
        if recommended:
            summary.append("\n\nRecommended Next Fix:")
            summary.append("-" * 50)
            summary.append(f"Repository: {recommended['repo']}")
            summary.append(f"Title: {recommended['title']}")
            summary.append(f"Impact: {recommended['impact_score']}/100")
            summary.append(f"Users: ~{recommended['affected_users']:,}")
            summary.append(f"URL: {recommended['url']}")
            
        return '\n'.join(summary)


def generate_insights(bugs: List[Dict]) -> str:
    """
    Generate insights from bug data.
    
    Args:
        bugs: List of bug dictionaries
        
    Returns:
        Formatted insights string
    """
    analytics = BugAnalytics(bugs)
    return analytics.summary()

