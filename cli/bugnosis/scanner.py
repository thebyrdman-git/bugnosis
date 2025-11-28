"""Bug scanner - finds high-impact bugs on GitHub."""

import requests
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Bug:
    """Represents a bug with impact score."""
    repo: str
    issue_number: int
    title: str
    url: str
    impact_score: int
    affected_users: int
    severity: str
    comments: int
    reactions: int
    created_days_ago: int


class ImpactScorer:
    """Calculates impact scores for bugs."""
    
    @staticmethod
    def calculate(bug_data: Dict, repo_stats: Dict, mode: str = "normal") -> int:
        """
        Calculate impact score (0-100).
        
        Components:
        - User base: 0-40 (based on repo stars/downloads)
        - Severity: 0-30 (based on labels, comments, reactions)
        - Ease: 0-20 (based on labels like "good first issue")
        - Time: 0-10 (recent = higher score)
        
        In 'novice' mode, Ease is weighted significantly higher.
        """
        score = 0
        
        # User base (0-40) - estimate based on repo popularity
        stars = repo_stats.get('stargazers_count', 0)
        if stars > 10000:
            score += 40
        elif stars > 5000:
            score += 35
        elif stars > 1000:
            score += 30
        elif stars > 500:
            score += 20
        else:
            score += 10
            
        # Severity (0-30) - based on community engagement
        comments = bug_data.get('comments', 0)
        reactions = bug_data.get('reactions', {}).get('total_count', 0)
        
        engagement = comments + (reactions * 2)
        if engagement > 50:
            score += 30
        elif engagement > 20:
            score += 25
        elif engagement > 10:
            score += 20
        elif engagement > 5:
            score += 15
        else:
            score += 10
            
        # Check for severity labels
        labels = [label['name'].lower() for label in bug_data.get('labels', [])]
        if any(word in ' '.join(labels) for word in ['critical', 'blocker', 'urgent']):
            score += 5
            
        # Ease (0-20) - easier bugs get more points (better ROI)
        is_easy = False
        if any(x in labels for x in ['good first issue', 'good-first-issue', 'documentation', 'easy', 'beginner']):
            is_easy = True
            score += 20
        elif 'help wanted' in labels:
            score += 15
        else:
            score += 10
            
        # Time (0-10) - recent issues are more relevant
        # This would need actual date calculation, simplified here
        score += 7
        
        # Mode adjustment
        if mode == "novice":
            # Boost easy issues, penalize hard ones
            if is_easy:
                score += 50  # Huge boost for explicitly easy issues
            else:
                score -= 30  # Penalize unknown difficulty
                
            # Cap at 100
            score = min(score, 100)
            # Floor at 0
            score = max(score, 0)
        
        return min(score, 100)


class GitHubScanner:
    """Scans GitHub for high-impact bugs."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers['Authorization'] = f'token {token}'
        self.session.headers['Accept'] = 'application/vnd.github.v3+json'
        
    def scan_repo(self, repo: str, min_impact: int = 70) -> List[Bug]:
        """
        Scan a repository for high-impact bugs.
        
        Args:
            repo: Repository in format "owner/name"
            min_impact: Minimum impact score to include
            
        Returns:
            List of Bug objects sorted by impact score
        """
        bugs = []
        
        # Get repo stats
        repo_url = f'https://api.github.com/repos/{repo}'
        repo_response = self.session.get(repo_url)
        if repo_response.status_code != 200:
            print(f"Error: Could not fetch repo {repo}")
            return []
            
        repo_stats = repo_response.json()
        
        # Search for bugs
        issues_url = f'https://api.github.com/repos/{repo}/issues'
        params = {
            'state': 'open',
            # 'labels': 'bug',
            'sort': 'comments',
            'direction': 'desc',
            'per_page': 30
        }
        
        response = self.session.get(issues_url, params=params)
        if response.status_code != 200:
            print(f"Error fetching issues: {response.status_code}")
            return []
            
        issues = response.json()
        
        for issue in issues:
            # Skip pull requests
            if 'pull_request' in issue:
                continue
                
            # Calculate impact
            impact_score = ImpactScorer.calculate(issue, repo_stats)
            
            if impact_score >= min_impact:
                bug = Bug(
                    repo=repo,
                    issue_number=issue['number'],
                    title=issue['title'],
                    url=issue['html_url'],
                    impact_score=impact_score,
                    affected_users=self._estimate_users(repo_stats, impact_score),
                    severity=self._determine_severity(impact_score),
                    comments=issue.get('comments', 0),
                    reactions=issue.get('reactions', {}).get('total_count', 0),
                    created_days_ago=0  # Simplified
                )
                bugs.append(bug)
                
        # Sort by impact score
        bugs.sort(key=lambda b: b.impact_score, reverse=True)
        return bugs
    
    def _estimate_users(self, repo_stats: Dict, impact_score: int) -> int:
        """Estimate affected users based on repo stats and impact."""
        stars = repo_stats.get('stargazers_count', 0)
        # Rough estimate: 10-20% of stars are active users
        base_users = int(stars * 0.15)
        
        # Adjust by impact score
        if impact_score >= 90:
            return int(base_users * 0.8)  # High impact = many affected
        elif impact_score >= 80:
            return int(base_users * 0.5)
        elif impact_score >= 70:
            return int(base_users * 0.3)
        else:
            return int(base_users * 0.1)
            
    def _determine_severity(self, impact_score: int) -> str:
        """Determine severity level from impact score."""
        if impact_score >= 90:
            return "Critical"
        elif impact_score >= 80:
            return "High"
        elif impact_score >= 70:
            return "Medium"
        else:
            return "Low"




