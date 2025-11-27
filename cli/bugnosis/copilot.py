"""AI Co-Pilot for bug fixing with human oversight.

The Co-Pilot helps you fix bugs faster while YOU stay in control:
1. Fetches and analyzes code
2. Generates fix suggestions
3. Creates tests
4. Helps write PR description
5. YOU approve each step
"""

import os
from typing import Optional, Dict, List
from groq import Groq


class BugFixCopilot:
    """AI Co-Pilot for guided bug fixing."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Co-Pilot.
        
        Args:
            api_key: Groq API key (optional, will check env)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        
        # Conversation history for context
        self.conversation = []
        
    def analyze_bug(self, issue: Dict, code_context: Optional[str] = None) -> Dict[str, str]:
        """
        Deeply analyze a bug with code context.
        
        Args:
            issue: GitHub issue dict with title, body, etc.
            code_context: Optional code snippets from the repo
            
        Returns:
            Dictionary with analysis, root_cause, fix_strategy
        """
        if not self.client:
            return {"error": "AI Co-Pilot requires GROQ_API_KEY"}
        
        prompt = f"""You are an expert software engineer helping fix a bug.

Issue: {issue.get('title', 'N/A')}

Description:
{issue.get('body', 'N/A')}

{"Code Context:\n" + code_context if code_context else ""}

Provide a detailed analysis:
1. What is the bug?
2. What is the root cause?
3. What strategy should we use to fix it?
4. What files likely need changes?
5. Are there any edge cases to consider?

Be specific and technical."""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.3,
                max_tokens=2048,
            )
            
            analysis = response.choices[0].message.content
            self.conversation.append({
                "role": "assistant",
                "content": analysis,
                "type": "analysis"
            })
            
            return {
                "analysis": analysis,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def generate_fix(self, 
                    issue: Dict,
                    file_path: str,
                    file_content: str,
                    analysis: Optional[str] = None) -> Dict[str, str]:
        """
        Generate code fix for a specific file.
        
        Args:
            issue: GitHub issue dict
            file_path: Path to file that needs fixing
            file_content: Current content of the file
            analysis: Previous analysis (optional)
            
        Returns:
            Dictionary with original_code, fixed_code, explanation
        """
        if not self.client:
            return {"error": "AI Co-Pilot requires GROQ_API_KEY"}
        
        context = ""
        if analysis:
            context = f"\n\nPrevious Analysis:\n{analysis}\n"
        
        prompt = f"""You are helping fix this bug:

Issue: {issue.get('title', 'N/A')}
{context}

File: {file_path}

Current Code:
```
{file_content[:3000]}  # Truncate if very long
```

Generate a fix:
1. Identify the exact lines that need changing
2. Provide the fixed code
3. Explain why this fixes the bug

Format your response as:
## Lines to Change
[line numbers]

## Fixed Code
```
[complete fixed code or diff]
```

## Explanation
[why this fixes the bug]

## Testing Strategy
[how to verify the fix works]
"""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.2,  # Lower temp for code generation
                max_tokens=3000,
            )
            
            fix = response.choices[0].message.content
            self.conversation.append({
                "role": "assistant",
                "content": fix,
                "type": "fix",
                "file": file_path
            })
            
            return {
                "fix": fix,
                "file_path": file_path,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def generate_tests(self,
                      issue: Dict,
                      fix_description: str,
                      test_framework: str = "pytest") -> Dict[str, str]:
        """
        Generate tests for the fix.
        
        Args:
            issue: GitHub issue dict
            fix_description: Description of what was fixed
            test_framework: Testing framework (pytest, unittest, etc.)
            
        Returns:
            Dictionary with test_code, test_file_name
        """
        if not self.client:
            return {"error": "AI Co-Pilot requires GROQ_API_KEY"}
        
        prompt = f"""Generate tests for this bug fix:

Issue: {issue.get('title', 'N/A')}
Fix: {fix_description}

Framework: {test_framework}

Create comprehensive tests that:
1. Test the bug was fixed
2. Test edge cases
3. Ensure no regression
4. Follow best practices

Provide:
- Complete test code
- Test file name
- Instructions to run
"""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.2,
                max_tokens=2048,
            )
            
            tests = response.choices[0].message.content
            self.conversation.append({
                "role": "assistant",
                "content": tests,
                "type": "tests"
            })
            
            return {
                "tests": tests,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def generate_pr_description(self,
                               issue: Dict,
                               changes_summary: str,
                               testing_done: str) -> Dict[str, str]:
        """
        Generate comprehensive PR description.
        
        Args:
            issue: GitHub issue dict
            changes_summary: Summary of changes made
            testing_done: Testing that was performed
            
        Returns:
            Dictionary with pr_description
        """
        if not self.client:
            return {"error": "AI Co-Pilot requires GROQ_API_KEY"}
        
        prompt = f"""Create a professional Pull Request description:

Issue: {issue.get('title', 'N/A')}
Issue URL: {issue.get('html_url', 'N/A')}
Issue Body:
{issue.get('body', 'N/A')[:500]}

Changes Made:
{changes_summary}

Testing Done:
{testing_done}

Create a PR description with:
## Description
[Clear overview]

## Problem
[What bug was fixed]

## Solution
[How it was fixed]

## Changes
[List of changes]

## Testing
[How it was tested]

## Impact
[Who this helps]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Follows project style

Resolves #{issue.get('number', '')}
"""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.4,
                max_tokens=2048,
            )
            
            pr_desc = response.choices[0].message.content
            
            return {
                "pr_description": pr_desc,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def review_changes(self,
                      original_code: str,
                      fixed_code: str,
                      file_path: str) -> Dict[str, any]:
        """
        AI reviews the changes before you commit.
        
        Args:
            original_code: Original code
            fixed_code: Fixed code
            file_path: File path
            
        Returns:
            Dictionary with review, concerns, suggestions
        """
        if not self.client:
            return {"error": "AI Co-Pilot requires GROQ_API_KEY"}
        
        prompt = f"""Review these code changes:

File: {file_path}

Original:
```
{original_code[:2000]}
```

Fixed:
```
{fixed_code[:2000]}
```

Provide a code review:
1. Does this fix look correct?
2. Any potential issues or bugs?
3. Code quality concerns?
4. Security considerations?
5. Performance impact?
6. Suggestions for improvement?

Rate the fix: APPROVE / NEEDS_WORK / REJECT
"""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.3,
                max_tokens=1500,
            )
            
            review = response.choices[0].message.content
            
            # Determine approval status
            review_lower = review.lower()
            if "approve" in review_lower and "needs_work" not in review_lower:
                status = "APPROVED"
            elif "reject" in review_lower:
                status = "REJECTED"
            else:
                status = "NEEDS_WORK"
            
            return {
                "review": review,
                "status": status,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def interactive_fix(self, issue: Dict) -> Dict[str, any]:
        """
        Interactive bug fixing session.
        
        Guides you through:
        1. Analysis
        2. Fix generation
        3. Review
        4. Testing
        5. PR creation
        
        Args:
            issue: GitHub issue to fix
            
        Returns:
            Complete fixing session results
        """
        session = {
            "issue": issue,
            "steps": [],
            "completed": False
        }
        
        print("\n🤖 AI Co-Pilot: Let's fix this bug together!\n")
        print(f"Issue: {issue.get('title')}")
        print(f"URL: {issue.get('html_url', 'N/A')}\n")
        
        # Step 1: Analysis
        print("Step 1: Analyzing the bug...")
        analysis_result = self.analyze_bug(issue)
        
        if analysis_result.get("success"):
            session["steps"].append({"step": "analysis", "result": analysis_result})
            print("\n✅ Analysis complete!")
            print("\n" + "="*60)
            print(analysis_result.get("analysis", ""))
            print("="*60 + "\n")
        else:
            print(f"❌ Analysis failed: {analysis_result.get('error')}")
            return session
        
        # Additional steps would be interactive with user input
        session["completed"] = True
        return session
    
    def estimate_difficulty(self, issue: Dict) -> Dict[str, any]:
        """
        Estimate how hard the bug is to fix.
        
        Args:
            issue: GitHub issue dict
            
        Returns:
            Dictionary with difficulty, time_estimate, reasoning
        """
        if not self.client:
            return {"error": "AI Co-Pilot requires GROQ_API_KEY"}
        
        prompt = f"""Estimate the difficulty of fixing this bug:

Issue: {issue.get('title', 'N/A')}

Description:
{issue.get('body', 'N/A')[:1000]}

Labels: {', '.join(issue.get('labels', []))}

Provide:
1. Difficulty: EASY / MEDIUM / HARD / EXPERT
2. Estimated time: X hours/days
3. Reasoning: Why this difficulty?
4. Prerequisites: What knowledge needed?
5. Similar fixes: Have you seen this before?

Be realistic and helpful."""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.3,
                max_tokens=1000,
            )
            
            estimate = response.choices[0].message.content
            
            # Extract difficulty level
            estimate_lower = estimate.lower()
            if "easy" in estimate_lower:
                difficulty = "EASY"
            elif "medium" in estimate_lower:
                difficulty = "MEDIUM"
            elif "expert" in estimate_lower:
                difficulty = "EXPERT"
            else:
                difficulty = "HARD"
            
            return {
                "estimate": estimate,
                "difficulty": difficulty,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}




