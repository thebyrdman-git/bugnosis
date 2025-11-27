# AI Co-Pilot Mode

Revolutionary bug fixing where AI does the heavy lifting, but YOU stay in control.

## Philosophy

Most AI tools either:
- Do everything automatically (you lose control)
- Give suggestions you have to implement yourself (slow)

Bugnosis Co-Pilot is different:
- **AI does the research** - Deep analysis, code review, difficulty estimation
- **AI generates the code** - Fix suggestions, tests, PR descriptions
- **YOU make decisions** - Approve, reject, or modify at each step
- **YOU stay in control** - It's your fix, AI just accelerates you

---

## 🎓 Rejection Coaching (Post-Mortem)

Rejections hurt. But they are the fastest way to learn.

Bugnosis includes a **Coaching Engine** that analyzes closed or rejected Pull Requests.

```bash
# Analyze a rejected PR
bugnosis coach pytorch/pytorch 12345
```

**What it does:**
1.  Reads maintainer comments and code review.
2.  Identifies the **Root Cause** (e.g., "Code Style", "Duplicate", "Wrong Approach").
3.  Provides **Actionable Advice** for next time.
4.  Awards "Resilience XP" (because trying matters).

---

## How It Works

```bash
# Start an interactive fixing session
bugnosis copilot owner/repo 12345
```

The Co-Pilot walks you through:

### 1. Deep Analysis
AI reads the issue, related code, and provides:
- What the bug is
- Root cause analysis
- Fix strategy
- Files that need changes
- Edge cases to consider

**YOU DECIDE**: Continue or stop

### 2. Difficulty Estimation
AI estimates:
- Difficulty level (EASY/MEDIUM/HARD/EXPERT)
- Time estimate
- Prerequisites needed
- Similar bugs it has seen

**YOU DECIDE**: Is this worth your time?

### 3. Code Fix Generation
AI generates:
- Exact code changes
- Line-by-line diff
- Explanation of why it works
- Testing strategy

**YOU DECIDE**: Accept, modify, or reject the fix

### 4. AI Code Review
Before you commit, AI reviews:
- Is the fix correct?
- Any potential bugs?
- Code quality issues?
- Security considerations?
- Performance impact?

**YOU DECIDE**: Commit or revise

### 5. Test Generation
AI creates:
- Tests for the fix
- Edge case tests
- Regression tests
- Instructions to run

**YOU DECIDE**: Use these tests or write your own

### 6. PR Description
AI writes a professional PR with:
- Problem description
- Solution explanation
- Testing done
- Impact statement
- Proper formatting

**YOU DECIDE**: Edit and submit

## Commands

### Full Co-Pilot Session
```bash
bugnosis copilot pytorch/pytorch 12345
```
Interactive session through all steps above.

### Quick Difficulty Check
```bash
bugnosis difficulty rust-lang/rust 54321
```
Just estimate how hard the bug is to fix.

### Standalone Features
```bash
# Deep diagnosis
bugnosis diagnose microsoft/vscode 23991

# Generate PR description
bugnosis generate-pr owner/repo 123 "Fixed memory leak in cache"
```

## Example Session

```bash
$ bugnosis copilot leon3s/wireguard-gui 42

🤖 Starting AI Co-Pilot for leon3s/wireguard-gui#42...

======================================================================
Issue: Snap package fails to build on Ubuntu 22.04
URL: https://github.com/leon3s/wireguard-gui/issues/42
======================================================================

📊 Step 1: Deep Analysis
----------------------------------------------------------------------
The issue appears to be related to the snap package configuration...

[AI provides detailed analysis]

👉 Continue to difficulty estimation? (y/n): y

⚡ Step 2: Difficulty Estimation
----------------------------------------------------------------------
Difficulty: MEDIUM
Estimated time: 2-3 hours
Reasoning: Requires understanding snap packaging and build systems...

[AI provides full estimate]

======================================================================
🎯 Co-Pilot Analysis Complete!
======================================================================

Next steps:
1. Clone the repository
2. Create a new branch
3. Use the analysis above to implement the fix
4. Test your changes
5. Run: bugnosis generate-pr leon3s/wireguard-gui 42 'Your fix description'

💡 Tip: The Co-Pilot analyzed the bug for you. You implement the fix!
     This keeps YOU in control while AI does the research.
```

## Why This Approach?

### Traditional Autonomous AI
```
❌ AI fixes bug automatically
❌ You don't learn anything
❌ You don't know what changed
❌ You can't verify the fix
❌ You're not in control
```

### Traditional AI Suggestions
```
❌ AI says "you should fix X"
❌ You do all the work
❌ AI doesn't help much
❌ Still slow
```

### Bugnosis Co-Pilot
```
✅ AI does deep research for you
✅ AI generates code for you
✅ You review and approve
✅ You learn from the analysis
✅ You stay in control
✅ 10x faster than solo
✅ Higher quality than full automation
```

## API Requirements

The Co-Pilot requires:
- **GROQ_API_KEY**: Free AI API (https://console.groq.com/keys)
- **GITHUB_TOKEN**: For fetching issues (optional but recommended)

```bash
export GROQ_API_KEY=your_groq_key
export GITHUB_TOKEN=your_github_token
```

## Perfect For

- **Learning**: See how experts would approach the fix
- **Speed**: Get analysis and code in minutes, not hours
- **Quality**: AI review catches issues before you commit
- **Confidence**: Know your fix is solid before submitting

## Advanced Usage

### Use in API
```python
from bugnosis import BugFixCopilot

copilot = BugFixCopilot(api_key="your_groq_key")

# Analyze a bug
issue = {...}  # GitHub issue dict
analysis = copilot.analyze_bug(issue)
print(analysis['analysis'])

# Estimate difficulty
difficulty = copilot.estimate_difficulty(issue)
print(f"This is a {difficulty['difficulty']} fix")

# Generate code fix
fix = copilot.generate_fix(
    issue=issue,
    file_path="src/main.rs",
    file_content=open("src/main.rs").read()
)
print(fix['fix'])

# Review changes
review = copilot.review_changes(
    original_code=old_code,
    fixed_code=new_code,
    file_path="src/main.rs"
)
print(f"Review: {review['status']}")

# Generate tests
tests = copilot.generate_tests(
    issue=issue,
    fix_description="Fixed memory leak",
    test_framework="pytest"
)
print(tests['tests'])

# Generate PR description
pr = copilot.generate_pr_description(
    issue=issue,
    changes_summary="Updated memory management in cache",
    testing_done="Added 5 new tests, all passing"
)
print(pr['pr_description'])
```

## Future Enhancements

Ideas for making Co-Pilot even better:
- Multi-file fixes (handle complex bugs across files)
- Integration with local git workflow
- VS Code extension for in-editor Co-Pilot
- Learning mode (AI explains concepts as it works)
- Pair programming mode (real-time collaboration)
- Custom fix strategies (teach Co-Pilot your style)

## Philosophy

This is how AI should work with humans:
- AI amplifies human capability
- Humans maintain control and responsibility
- Both learn from each other
- Result is better than either alone

You're not replacing developers. You're making developers superhuman.
