# Contributing to Bugnosis

Thank you for wanting to help build this.

---

## The Mission

Help people contribute to open source by:
- Making it easy to find high-impact bugs
- Using AI to assist with the hard parts
- Celebrating successes
- Building community

Every contribution to this project helps thousands contribute to others.

---

## 📣 Feedback on Vision

We are currently shaping the core philosophy of the **Hero Engine**. We want your thoughts!

*   Do you like the "Antivirus" aesthetic?
*   Is the "Impact Score" methodology fair?
*   How should "Rejection Coaching" work?

Please share your thoughts in [GitHub Discussions](https://github.com/thebyrdman-git/bugnosis/discussions).

---

## What We Need

### Rust Developers
- Discovery engine (core scanning)
- Impact scoring algorithm
- System tray implementation
- Performance optimization

### AI/ML Developers
- LLM integration (Groq, OpenAI, etc.)
- Bug analysis prompts
- PR description generation
- Impact prediction models

### Technical Writers
- Documentation
- Tutorials
- Blog posts
- Video scripts

### Designers
- Achievement badges
- Social sharing cards
- CLI output formatting
- Web dashboard (future)

### Testers
- Try features
- Report bugs
- Suggest improvements
- User experience feedback

---

## Getting Started

### 1. Fork & Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/bugnosis.git
cd bugnosis
```

### 2. Set Up Development Environment

```bash
# Install Rust dependencies
cd gui
npm install
npm run tauri dev

# Install CLI dependencies
cd ../cli
pip install -e .
```

See [DEVELOPERS.md](DEVELOPERS.md) for detailed setup instructions.

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
# Run CLI tests
cd cli
pytest

# Run GUI linting
cd ../gui
npm run lint
```

### 6. Submit PR

```bash
git push origin feature/your-feature-name

# Then create PR on GitHub
gh pr create --fill
```

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
- Comment on existing issues
- Start a GitHub Discussion

**No idea is too small!**

---

## 🚀 Development Roadmap

See [ROADMAP.md](ROADMAP.md) for our plans.

Want to work on something? Comment on the issue or create one!

---

## 🙏 Thank You!

Every contribution makes this tool better.  
Every improvement helps more people contribute to open source.  
Every bug fix creates ripple effects of impact.

**You're helping build a movement. Thank you!** 💚
