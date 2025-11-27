# Release Notes - v1.0.0 "Hero Engine"

We are proud to announce the first public release of **Bugnosis**, the AI-powered platform that turns open-source contribution into a high-impact, gamified experience.

<img src="gui/public/bug-logo.png" alt="Bugnosis Hero Dashboard" width="150px" />

## 🚀 Key Features

### 1. Impact Engine
*   **Smart Search:** Simply type "Firefox", "Linux Kernel", or "Ansible" to find high-impact bugs instantly.
*   **Impact Scoring:** Every bug is scored (0-100) based on user base, severity, and complexity. Prioritize the bugs that matter.
*   **Federated Search:** Searches across GitHub, GitLab, and Bugzilla (beta) simultaneously.

### 2. Hero Profile
*   **Gamification:** Earn XP, rank up from *Script Kiddie* to *Ecosystem Guardian*, and unlock achievements.
*   **Mission Control:** Get curated missions like "First Blood" or "Python Charmer" to guide your journey.
*   **Impact Dashboard:** Track total users helped and estimated time saved for the community.

### 3. Developer Power Tools
*   **AI Co-Pilot:** Get deep root cause analysis and fix strategies for any bug.
*   **Doctor:** `bugnosis doctor` checks your environment health (Podman, Git, Python).
*   **Offline Mode:** Full functionality for viewing saved bugs and stats without an internet connection.
*   **Cloud Sync:** Sync your Hero Profile across machines using private GitHub Gists.

### 4. User Experience
*   **"Antivirus" Aesthetic:** A clean, professional interface inspired by classic security tools.
*   **Light/Dark Mode:** Fully supported themes for late-night coding sessions.
*   **Privacy First:** Local-first architecture. Your data stays on your machine unless you choose to sync.

## 📦 Installation

### Build from Source (Linux/macOS)
```bash
git clone https://github.com/thebyrdman-git/bugnosis.git
cd bugnosis
./install.sh  # (Coming soon, use manual steps for now)

# Manual:
cd cli && pip install -e .
cd ../gui && npm install && npm run tauri dev
```

## 🤝 Contributing

We are looking for:
*   **Rust Developers** to optimize the backend.
*   **React/TypeScript** wizards to polish the UI.
*   **AI Engineers** to improve the Co-Pilot's diagnosis accuracy.

See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## 🙏 Special Thanks

*   To the open-source community for building the software that runs the world.
*   To all future heroes who will use this tool to fix the bugs that matter.

