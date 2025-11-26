# Writing Guide - Keeping Bugnosis Authentic

This guide helps contributors write documentation that sounds natural and human.

---

## Red Flags to Avoid

### 1. Emoji Overload
**Bad:**
```markdown
## Features 🚀
- Bug scanning 🔍
- AI diagnosis 🤖
- Impact tracking 📊
- Community features 👥
```

**Good:**
```markdown
## Features
- Bug scanning
- AI diagnosis  
- Impact tracking
- Community features
```

**Rule:** Use emojis sparingly, if at all. Not in headers or lists.

---

### 2. Excessive Enthusiasm

**Bad:**
```
This is AMAZING! You'll be absolutely blown away by how INCREDIBLE 
this feature is! It's a total game-changer that will REVOLUTIONIZE 
everything!
```

**Good:**
```
This feature helps you find bugs faster by automatically scanning
repositories and scoring them by impact.
```

**Rule:** State facts clearly. Let the value speak for itself.

---

### 3. The "Perfect Three" Pattern

**Bad (always 3 items):**
```
Why Bugnosis?
1. It's fast
2. It's easy
3. It's powerful

Benefits:
- Save time
- Help people
- Build skills
```

**Good (vary the count):**
```
Why Bugnosis?
1. Automated bug discovery
2. AI-powered diagnosis
3. Impact scoring (0-100)
4. Community features
5. Open source

Benefits vary by user. Some save time, others enjoy the community
aspect, and many appreciate seeing their real impact on thousands of users.
```

**Rule:** Real lists aren't always 3 items. Vary it. Sometimes 2, sometimes 5.

---

### 4. Formulaic Headers

**Bad:**
```
## 🎯 The Problem
## 💡 The Solution  
## 🚀 Getting Started
## ✨ Key Features
```

**Good:**
```
## The Problem
## How It Works
## Installation
## Features
```

**Rule:** Skip the emoji headers. Use straightforward names.

---

### 5. Overly Structured Formatting

**Bad:**
```
**Key Point 1:** This is important
**Key Point 2:** This is also important  
**Key Point 3:** Don't forget this

**Pro Tip:** Here's a tip!
**Note:** Pay attention to this
**Important:** Really important!
```

**Good:**
```
Three things to know:

First, the impact scoring system ranges from 0-100 based on users affected.

Second, AI diagnosis is optional. You can use it or fix bugs manually.

Third, all data stays local. We don't track your activity.
```

**Rule:** Write naturally. Bold formatting for every other sentence looks robotic.

---

### 6. The "Let's" Trap

**Bad:**
```
Let's get started! Let's dive in! Let's explore the features! 
Let's build something amazing together!
```

**Good:**
```
To get started, install the CLI tool:

    pip install bugnosis

Run your first scan:

    bugnosis scan --high-impact
```

**Rule:** Give instructions directly. Skip the cheerleading.

---

### 7. Marketing Speak

**Bad:**
```
Leveraging cutting-edge AI technology, Bugnosis revolutionizes the 
paradigm of open source contribution, enabling synergistic collaboration 
at scale while maximizing impact velocity.
```

**Good:**
```
Bugnosis uses AI to find bugs that affect many users, then helps you
fix them faster.
```

**Rule:** Plain language wins. Explain what it does, not how revolutionary it is.

---

### 8. Fake Informality

**Bad:**
```
Hey there! 👋 So, here's the thing - we've built this super cool
tool that's gonna totally change how you contribute! Pretty neat, right?
```

**Good:**
```
Bugnosis helps you find high-impact bugs and fix them efficiently.
```

**Rule:** Professional doesn't mean corporate. Natural doesn't mean forced casual.

---

### 9. Every Sentence Starts the Same

**Bad:**
```
This tool helps you find bugs.
This tool analyzes impact.
This tool generates PRs.
This tool tracks your contributions.
```

**Good:**
```
Bugnosis finds bugs worth fixing by analyzing their impact on users.
Impact scores range from 0-100. The AI can analyze bugs and suggest
fixes, but you're always in control.
```

**Rule:** Vary sentence structure. Don't repeat patterns.

---

### 10. Exclamation Mark Overuse

**Bad:**
```
Welcome to Bugnosis! We're excited to have you! This is going to be
great! Let's get started!
```

**Good:**
```
Welcome to Bugnosis. This guide walks you through installation and
your first bug fix.
```

**Rule:** One exclamation mark per document max. Period.

---

## Writing Style Guidelines

### Be Direct
**Bad:** "One of the things that Bugnosis does is it helps you to be able to..."  
**Good:** "Bugnosis helps you..."

### Use Active Voice
**Bad:** "Bugs are found by the scanning engine"  
**Good:** "The engine scans for bugs"

### Vary Sentence Length
**Bad:** All sentences same length. Everything feels robotic. Nothing has variety.  
**Good:** Bugnosis scans repositories for bugs. When it finds one, it calculates an impact score based on several factors: users affected, severity, and fix difficulty. High-scoring bugs go to the top.

### Show, Don't Just Tell
**Bad:** "Bugnosis is easy to use"  
**Good:** "Install: `pip install bugnosis`. Run: `bugnosis scan`. That's it."

### Use Specific Numbers
**Bad:** "Helps many users"  
**Good:** "Helped 50,000 users" or "Helped between 10,000-50,000 users"

### Don't Explain Every Obvious Thing
**Bad:**
```
Click the button. The button will then be clicked. After clicking,
the button will have been clicked and you will see the result.
```

**Good:**
```
Click the button to see results.
```

---

## Real Examples from Bugnosis

### Before (Too AI-sounding)
```markdown
## 🚀 Welcome to Bugnosis!

Hey there! 👋 We're super excited to have you join our amazing community
of contributors! 

### Why Bugnosis? ✨

1. **It's Fast!** ⚡
2. **It's Easy!** 👍
3. **It's Powerful!** 💪

Let's dive in and start making an impact together! 🎉
```

### After (More Natural)
```markdown
## Getting Started

Bugnosis helps you find and fix bugs that affect thousands of users.

First, install the tool:

    pip install bugnosis

Then run your first scan:

    bugnosis scan --high-impact

The tool will show you bugs ranked by how many people they affect.
```

---

## Code Comments

### Bad (Over-explained)
```python
# This function calculates the impact score
# It takes a bug as input
# It returns a score from 0-100
# Higher scores mean more impact
def calculate_impact(bug):
    # First we get the user count
    users = bug.affected_users
    # Then we multiply by severity
    score = users * bug.severity
    # Finally we return the score
    return min(score, 100)
```

### Good (Natural)
```python
def calculate_impact(bug):
    """Calculate impact score (0-100) based on users affected and severity."""
    score = bug.affected_users * bug.severity
    return min(score, 100)
```

---

## Commit Messages

### Bad
```
feat: ✨ Add amazing new feature! 🚀

This incredible new feature is going to revolutionize everything!
It's super awesome and users will absolutely love it!
```

### Good
```
feat: add impact scoring for bug discovery

Scores bugs 0-100 based on users affected, severity, and fix difficulty.
High-scoring bugs appear first in scan results.
```

---

## Issue/PR Templates

### Bad
```markdown
## 🎯 What does this do?
This absolutely amazing PR adds...

## ✨ Why is this awesome?
Because it's going to revolutionize...

## 🚀 How to test
Let's test this together!
```

### Good
```markdown
## Changes
Added impact scoring to bug discovery

## Why
Users wanted to prioritize bugs by potential impact

## Testing
Run `bugnosis scan` and verify bugs are sorted by score
```

---

## The Golden Rules

1. **Remove emojis** from documentation
2. **Cut enthusiasm** by 80%
3. **Vary list lengths** (not always 3)
4. **Use plain language** (not marketing speak)
5. **Be specific** (use real numbers)
6. **Stay technical** when appropriate
7. **Don't over-explain** obvious things
8. **Mix sentence lengths** 
9. **One exclamation mark** per doc max
10. **Read it out loud** - does it sound like you?

---

## The "Read Aloud" Test

Before committing documentation:

1. Read it out loud
2. Does it sound like something you'd say?
3. Would you cringe hearing this at a conference?
4. Does every sentence feel necessary?

If any answer is "no," revise.

---

## Examples from Real Open Source

### Good Examples (Study These)

**Rust Documentation:**
```
Rust is a systems programming language focused on safety, speed, 
and concurrency.
```
Clean. Direct. No fluff.

**Linux Kernel Docs:**
```
This document describes the kernel's memory management subsystem.
```
Gets right to the point.

**Git Docs:**
```
git-add - Add file contents to the index
```
Functional. Clear. Done.

---

## When to Break These Rules

Sometimes you DO want personality:
- Blog posts (can be more casual)
- Community forum (natural conversation)
- Social media (appropriate place for enthusiasm)

But core documentation? Keep it clean and professional.

---

## Review Checklist

Before pushing docs:

- [ ] Removed unnecessary emojis
- [ ] Cut excessive enthusiasm  
- [ ] Varied list lengths
- [ ] Used active voice
- [ ] Mixed sentence lengths
- [ ] Removed "Let's" statements
- [ ] Cut marketing speak
- [ ] Removed excessive formatting
- [ ] Read it out loud
- [ ] Sounds human

---

## tl;dr

Write like you're explaining something to a colleague over coffee. Not like you're selling something on late-night TV.

**Be clear. Be direct. Be professional. Be human.**

That's it.

