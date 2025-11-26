# Bugnosis

**Diagnose bugs. Help thousands. Automate giving back.**

AI-powered platform for finding and fixing high-impact open source bugs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Early Development](https://img.shields.io/badge/Status-Early%20Development-orange)](https://github.com/thebyrdman-git/bugnosis)

---

## The Problem

You want to contribute to open source, but:
- Finding bugs worth fixing is hard
- You don't know which bugs help the most people
- Writing PRs takes time
- It's hard to track your impact

## The Solution

**Bugnosis** is an AI-powered platform that:
- Finds high-impact bugs for you (background scanning)
- Scores bugs 0-100 by impact (users affected)
- Uses AI to diagnose and suggest fixes
- Shows you exactly how many people you're helping
- Makes giving back fun with gamification

---

## Real Example

**First contribution using this approach:**

- **Project:** [wireguard-gui](https://github.com/0xle0ne/wireguard-gui)
- **PR:** [#399](https://github.com/0xle0ne/wireguard-gui/pull/399)
- **Time:** 4 hours
- **Impact Score:** 77/100 (High Impact)
- **Users Helped:** ~50,000

**What was fixed:**
1. Broken snap package (completely non-functional)
2. CSS animation typo
3. Import dialog not showing hidden files

**Result:** 50,000 snap users can now use the application.

That's **25,000 hours of human time saved** from one afternoon of work.

---

## How It Works

### 1. Background Discovery (System Tray)

Bugnosis runs quietly in your system tray, continuously scanning for high-impact bugs.

```
Radar Alert!

Bug detected: Broken snap package
Project: wireguard-gui
Impact: 92/100 (Critical!)
Users: ~50,000
Time to fix: ~2 hours

[View Details] [Start Fix]
```

### 2. AI Diagnosis (Desktop App)

AI analyzes the bug and tells you:
- What's broken and why
- How to fix it
- Expected impact
- Testing recommendations

### 3. Automated PRs (Optional)

Choose your automation level:
- **Manual + AI Assist:** You code, AI helps write PR description
- **AI Draft:** AI creates draft PR, you review/edit
- **Auto:** AI fixes simple bugs (typos, configs) automatically

### 4. Track Your Impact

See exactly how you're giving back:
- 👥 Users helped
- ⏰ Time saved (collective)
- 🎯 Impact score
- 🏆 Achievements unlocked

---

## Features

### Smart Discovery
- Background scanning of GitHub/GitLab
- Impact scoring (0-100)
- Skill matching (finds bugs you can fix)
- Time estimation

### Desktop App

**4 Tabs:**
1. **Radar** - High-impact bugs detected
2. **Impact** - Your contribution analytics
3. **AI Assistant** - Automated PR workflow
4. **Learn** - Tutorials & community

### System Tray
- Radar notifications
- Quick actions
- Always accessible
- Minimal distraction

### Community Features
- Public leaderboards (GitHub Pages)
- Squad competitions
- Company challenges
- Mentor matching
- Contribution parties

---

## Impact Scoring System

Not all bugs are equal. Bugnosis scores them 0-100 based on:

```
Impact Score = User Base (40) + Severity (30) + Ease (20) + Time (10)
```

**Example scores:**
- **92/100** - Broken installation affecting 50,000 users (Critical)
- **75/100** - UI bug affecting all users, easy fix (High Impact)
- **45/100** - Edge case affecting 100 users (Low Impact)

Focus on high-impact bugs (70+) for maximum giving back.

[Full scoring details](docs/IMPACT_SCORING.md)

---

## Status

**Early Development** - Building in public!

**What exists:**
- Impact scoring framework
- Complete vision documented
- Proof of concept (WireGuard PR)
- Open source logos

**What's being built:**
- Background discovery engine
- System tray app
- Desktop app (Tauri + React)
- AI integration (Groq)
- GitHub Pages leaderboard

---

## Vision

[Read the complete vision](BUGNOSIS_VISION.md)

**Key innovations:**
1. **Impact-first** - Focus on bugs that help the most people
2. **AI-powered** - Diagnose, fix, and write PRs with AI
3. **Gamified** - Make giving back fun and competitive
4. **Community** - Squads, challenges, leaderboards
5. **Automated** - From discovery to PR submission

---

## Technology Stack

- **Desktop:** Tauri (Rust + React/Svelte)
- **System Tray:** Cross-platform (AppIndicator/NSStatusBar/System Tray API)
- **Discovery Engine:** Rust
- **AI:** Groq (llama-3.1-70b) with OpenAI fallback
- **Database:** SQLite (local-first)
- **Leaderboard:** GitHub Pages + Actions

---

## Getting Started

**Not ready for users yet!** But you can:

1. **Star this repo** - Get updates
2. **Join discussions** - Share ideas
3. **Contribute** - Help build it
4. **Follow progress** - Watch development

Want to help build Bugnosis? See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Philosophy

### Impact-Driven
> "Your time is valuable. Spend it helping the most people possible."

### Open & Transparent
> "Built in public. Progress tracked publicly. Leaderboards public."

### AI-Assisted, Not AI-Replaced
> "AI helps you contribute better. You're always in control."

### Community-First
> "Make giving back fun, social, and rewarding."

---

## Roadmap

### Phase 1: MVP (Current)
- Impact scoring system
- Basic bug discovery
- Desktop app prototype
- System tray notifications

### Phase 2: AI Integration
- AI diagnosis engine
- PR description generation
- Automated fork/push
- Impact dashboard

### Phase 3: Community
- GitHub Pages leaderboard
- Squad system
- Achievement badges
- Social sharing

### Phase 4: Automation
- AI Draft PRs
- Auto-fix simple bugs
- PR tracking
- Contribution parties

---

## Contributing

We need help building this! Areas to contribute:

- **Rust developers** - Discovery engine, system tray
- **Frontend developers** - Desktop app (React/Svelte)
- **AI/ML folks** - Impact prediction, bug diagnosis
- **Technical writers** - Documentation, tutorials
- **Designers** - UI/UX, badges, certificates

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Community

- **GitHub Discussions:** [Ask questions, share ideas](https://github.com/thebyrdman-git/bugnosis/discussions)
- **Twitter:** Coming soon
- **Discord:** Coming soon

---

## License

MIT © 2025 Bugnosis Contributors

---

## Inspiration

This project was inspired by a simple realization:

> "I spent 4 hours fixing bugs and helped 50,000 people. What if this was easy for everyone?"

That one contribution proved high-impact open source work doesn't take forever - it just takes focus on the right bugs.

**Bugnosis makes finding those bugs automatic.**

---

## Status

**Early Development** - Building in public, iterating fast.

Follow along as we build a platform to help thousands contribute to open source.

---

**Built by contributors who care about impact**

