"""AI integration for bug diagnosis and PR generation."""

import os
import json
import requests
from typing import Optional, Dict


class AIEngine:
    """AI engine for analyzing bugs and generating PRs."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        self.base_url = 'https://api.groq.com/openai/v1/chat/completions'
        self.model = 'llama-3.1-70b-versatile'
        
    def resolve_target(self, query: str) -> Dict[str, str]:
        """
        Resolve a natural language query into a platform and repository target.
        DEPRECATED: Use resolve_targets for multi-platform support.
        """
        targets = self.resolve_targets(query)
        if targets:
            return targets[0]
        return {'platform': 'github', 'target': query}

    def resolve_targets(self, query: str) -> list[Dict[str, str]]:
        """
        Resolve a query into multiple potential targets across platforms.
        
        Args:
            query: User input (e.g. "python", "browsers", "linux")
            
        Returns:
            List of dicts with 'platform', 'target', 'instance'
        """
        if not self.api_key:
            # Basic heuristic fallback
            return [
                {'platform': 'github', 'target': query},
                {'platform': 'gitlab', 'target': query},
            ]
            
        prompt = f"""You are a Bug Hunter assistant.
User Query: "{query}"

Identify up to 3 most relevant repository/project targets across different platforms (GitHub, GitLab, Bugzilla).
Focus on the official or most popular repositories for this topic.

Return a JSON object with a "targets" array.
Each target must have: "platform", "target" (repo name or product name), "instance" (optional).

Example for "firefox":
{{
  "targets": [
    {{"platform": "bugzilla", "target": "Firefox", "instance": "mozilla"}},
    {{"platform": "github", "target": "mozilla/gecko-dev"}}
  ]
}}

Example for "linux":
{{
  "targets": [
    {{"platform": "github", "target": "torvalds/linux"}},
    {{"platform": "bugzilla", "target": "Kernel", "instance": "kernel"}}
  ]
}}
"""
        try:
            response = requests.post(
                self.base_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': self.model,
                    'messages': [
                        {'role': 'system', 'content': 'You are a JSON-only API.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.1,
                    'response_format': {"type": "json_object"},
                    'max_tokens': 300,
                },
                timeout=15
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                data = json.loads(content)
                return data.get('targets', [])
            return []
        except Exception as e:
            print(f"AI Target Resolution Error: {e}")
            return [{'platform': 'github', 'target': query}]

    def diagnose_bug(self, issue_data: Dict) -> Optional[str]:
        """
        Use AI to diagnose what's wrong with a bug.
        
        Args:
            issue_data: GitHub issue data
            
        Returns:
            AI diagnosis text or None if error
        """
        if not self.api_key:
            return None
            
        prompt = f"""Analyze this GitHub issue and provide a concise diagnosis.

Issue Title: {issue_data.get('title', 'Unknown')}
Issue Body: {issue_data.get('body', 'No description')[:1000]}
Comments: {issue_data.get('comments', 0)}
Labels: {', '.join(label['name'] for label in issue_data.get('labels', []))}

Provide:
1. What's broken (1-2 sentences)
2. Likely root cause (1 sentence)
3. Suggested fix approach (2-3 sentences)

Keep it technical and concise. No fluff."""

        try:
            response = requests.post(
                self.base_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': self.model,
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.3,
                    'max_tokens': 500,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"AI request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"AI error: {e}")
            return None
    
    def generate_pr_description(self, bug_data: Dict, fix_description: str) -> Optional[str]:
        """
        Generate a PR description for a bug fix.
        
        Args:
            bug_data: GitHub issue data
            fix_description: What you fixed (user provides this)
            
        Returns:
            PR description text
        """
        if not self.api_key:
            return None
            
        prompt = f"""Generate a professional GitHub pull request description for this bug fix.

Bug Title: {bug_data.get('title', 'Unknown')}
Bug Description: {bug_data.get('body', 'No description')[:500]}
What I Fixed: {fix_description}

Generate a PR description with these sections:
- Problem: What was broken (2-3 sentences)
- Solution: What you changed (2-3 sentences)
- Testing: How it was tested (1-2 sentences)
- Impact: Estimated users helped

Use markdown formatting. Be professional and concise. No hype."""

        try:
            response = requests.post(
                self.base_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': self.model,
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.5,
                    'max_tokens': 800,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return None
                
        except Exception as e:
            print(f"AI error: {e}")
            return None

    def analyze_rejection(self, pr_data: Dict, comments: list) -> Dict:
        """
        Analyze a closed/rejected PR to provide coaching.
        
        Args:
            pr_data: PR details (title, body, state)
            comments: List of review comments
            
        Returns:
            Dict with 'reason', 'advice', 'encouragement'
        """
        if not self.api_key:
            return {'error': 'No API key'}

        # Format comments for prompt
        comments_text = "\n".join([f"- {c['user']['login']}: {c['body'][:200]}" for c in comments])

        prompt = f"""Analyze this rejected Pull Request and provide coaching for the contributor.

PR Title: {pr_data.get('title')}
State: {pr_data.get('state')}
Review Comments:
{comments_text}

You are a senior engineering mentor. Analyze why this was rejected.
Return JSON with these fields:
1. "reason": The primary technical or process reason (e.g. "Code Style", "Duplicate", "Wrong Approach", "Tests Missing").
2. "analysis": A 2-sentence explanation of what went wrong.
3. "advice": Actionable advice for next time (bullet points).
4. "encouragement": A short, motivating message to keep them trying (Hero/Gaming theme).
"""

        try:
            response = requests.post(
                self.base_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': self.model,
                    'messages': [
                        {'role': 'system', 'content': 'You are a supportive engineering mentor. Return JSON only.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.4,
                    'response_format': {"type": "json_object"},
                    'max_tokens': 500,
                },
                timeout=30
            )

            if response.status_code == 200:
                return json.loads(response.json()['choices'][0]['message']['content'])
            return {'error': f'API Error {response.status_code}'}
            
        except Exception as e:
            return {'error': str(e)}
