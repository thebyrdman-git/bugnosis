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


