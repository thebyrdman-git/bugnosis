# 🤝 Contributing to ANSAI Pull Requests

**Thank you for wanting to help build this!**

---

## 💚 The Mission

Help people contribute to open source by:
- Making it easy to find high-impact bugs
- Using AI to assist with the hard parts
- Celebrating successes
- Building community

**Every contribution to this project helps thousands contribute to others!**

---

## 🎯 What We Need

### 🐍 Python Developers
- CLI tools (`ansai-pr-*` commands)
- Impact scoring algorithm
- GitHub/GitLab API integration
- Testing infrastructure

### 🤖 AI/ML Folks
- LLM integration (Groq, OpenAI, etc.)
- Bug analysis prompts
- PR description generation
- Impact prediction models

### 📝 Technical Writers
- Documentation
- Tutorials
- Blog posts
- Video scripts

### 🎨 Designers
- Achievement badges
- Social sharing cards
- CLI output formatting
- Web dashboard (future)

### 🧪 Testers
- Try features
- Report bugs
- Suggest improvements
- User experience feedback

---

## 🚀 Getting Started

### 1. Fork & Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/ansai-pull-requests.git
cd ansai-pull-requests
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 4. Make Your Changes

Follow our [code style](#code-style) and [commit guidelines](#commit-guidelines).

### 5. Test

```bash
# Run tests
pytest

# Run linters
black .
flake8 .
mypy .
```

### 6. Submit PR

```bash
git push origin feature/your-feature-name

# Then create PR on GitHub
gh pr create --fill
```

---

## 📋 How to Find Tasks

### Good First Issues
Start here: [good first issue label](https://github.com/thebyrdman-git/ansai-pull-requests/labels/good%20first%20issue)

### High Impact Issues
Help us build impactful features: [high-impact label](https://github.com/thebyrdman-git/ansai-pull-requests/labels/high-impact)

### Documentation
Always needed: [documentation label](https://github.com/thebyrdman-git/ansai-pull-requests/labels/documentation)

---

## 💻 Code Style

### Python
- **Formatter:** Black (line length: 100)
- **Linter:** Flake8
- **Type hints:** Use mypy
- **Docstrings:** Google style

```python
def calculate_impact_score(
    users_affected: int,
    severity: Severity,
    fix_difficulty: Difficulty,
    time_estimate: float,
) -> int:
    """Calculate impact score for a bug.
    
    Args:
        users_affected: Estimated number of users affected
        severity: Bug severity level
        fix_difficulty: Estimated difficulty to fix
        time_estimate: Estimated hours to fix
        
    Returns:
        Impact score from 0-100
        
    Example:
        >>> calculate_impact_score(50000, Severity.CRITICAL, Difficulty.EASY, 2.0)
        92
    """
    # Implementation...
```

### Commits
Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add impact scoring algorithm
fix: correct user count estimation
docs: add contributing guidelines
test: add tests for PR generation
chore: update dependencies
```

### PRs
- Clear title following conventional commits
- Description explaining what and why
- Link to related issues
- Screenshots/demos if UI changes

---

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# Specific test
pytest tests/test_impact_scoring.py

# With coverage
pytest --cov=ansai_pr
```

### Write Tests
Every feature needs tests:

```python
def test_impact_score_critical_bug():
    """Test that critical bugs affecting many users score high."""
    score = calculate_impact_score(
        users_affected=50000,
        severity=Severity.CRITICAL,
        fix_difficulty=Difficulty.EASY,
        time_estimate=2.0,
    )
    assert score >= 90, "Critical bugs should score 90+"
```

---

## 📚 Documentation

### Code Documentation
- Docstrings for all public functions
- Type hints everywhere
- Inline comments for complex logic

### User Documentation
- Clear explanations
- Lots of examples
- Beginner-friendly language
- No jargon without explanation

---

## 🎯 Pull Request Guidelines

### Before Submitting
- [ ] Tests pass
- [ ] Linters pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if significant)
- [ ] Commit messages follow convention

### PR Description Template

```markdown
## Description
Brief explanation of what this PR does.

## Motivation
Why is this change needed? What problem does it solve?

## Changes
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
How was this tested? What scenarios were covered?

## Breaking Changes
Any breaking changes? How should users adapt?

## Related Issues
Closes #123
Related to #456
```

---

## 🌟 First Contribution?

**We love first-time contributors!**

Look for issues labeled:
- `good first issue`
- `beginner-friendly`
- `documentation`

Don't hesitate to ask questions:
- Comment on the issue
- Join our [Discord](https://discord.gg/ansai-pr)
- Tag @thebyrdman-git

**Everyone starts somewhere. We're here to help!** 💚

---

## 🎁 Recognition

Contributors are celebrated in:
- README.md contributors section
- CONTRIBUTORS.md file
- Monthly community shoutouts
- Achievement badges (coming soon!)

**Every contribution matters!**

---

## 💬 Communication

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Ideas, questions, help
- **Discord:** Real-time chat, community
- **Twitter:** [@ansai_pr](https://twitter.com/ansai_pr)

---

## 🚫 Code of Conduct

### Our Pledge
We're committed to providing a welcoming, inclusive environment for everyone.

### Our Standards
- ✅ Be respectful and kind
- ✅ Welcome beginners
- ✅ Give constructive feedback
- ✅ Focus on what's best for the community
- ✅ Show empathy

### Not Acceptable
- ❌ Harassment of any kind
- ❌ Trolling or insulting comments
- ❌ Personal attacks
- ❌ Publishing others' private info
- ❌ Unwelcome sexual attention

### Enforcement
Violations can be reported to conduct@ansai.dev.  
We will review and take appropriate action.

---

## 🎯 Impact-Driven Contributions

**We practice what we preach!**

When contributing to this project:
1. **Focus on high-impact features** - What helps the most users?
2. **Keep it simple** - Easy to use > Feature-rich
3. **Document everything** - Help the next person
4. **Test thoroughly** - Quality over speed
5. **Be kind** - We're all learning

---

## 💡 Ideas & Feedback

Have ideas? We want to hear them!

- Open an issue for discussion
- Join Discord #ideas channel
- Comment on existing issues
- Start a GitHub Discussion

**No idea is too small!**

---

## 🚀 Development Roadmap

See [ROADMAP.md](ROADMAP.md) for our plans.

Want to work on something? Comment on the issue or create one!

---

## 📈 Growth Mindset

**We're building this together, learning as we go.**

- Never contributed before? Perfect!
- Not sure how something works? Ask!
- Made a mistake? We all do!
- Want to try something new? Go for it!

**The goal is progress, not perfection.** 💪

---

## 🙏 Thank You!

Every contribution makes this tool better.  
Every improvement helps more people contribute to open source.  
Every bug fix creates ripple effects of impact.

**You're helping build a movement. Thank you!** 💚

---

**Questions? Ask in [Discussions](https://github.com/thebyrdman-git/ansai-pull-requests/discussions) or [Discord](https://discord.gg/ansai-pr)!**

