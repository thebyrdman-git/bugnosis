# Bugnosis

**Diagnose bugs. Help thousands. Automate giving back.**

Bugnosis is an AI-powered platform that turns open source contribution into a high-impact, gamified experience. It finds the bugs that matter most, helps you fix them with AI, and tracks the real-world impact of your work.

![Bugnosis Hero Dashboard](gui/public/bug-logo.png)

## The Mission

Most developers want to contribute to open source, but finding meaningful work is hard. "Good first issues" are often trivial.

Bugnosis focuses on **High-Impact Opportunities**: bugs that affect thousands of users, block major releases, or cause significant pain. We call this the **Hero Engine**.

[Read our Full Vision](VISION.md)

## Key Features

*   **Smart Search:** Type "Firefox" or "Linux Kernel", and our AI resolves the targets across GitHub, GitLab, and Bugzilla.
*   **Impact Scoring:** Every bug is scored (0-100) based on user base, severity, and time-to-fix.
*   **Hero Profile:** Earn XP, rank up from *Script Kiddie* to *Ecosystem Guardian*, and unlock badges.
*   **AI Co-Pilot:** An intelligent assistant that helps you diagnose issues and draft Pull Requests (you stay in control).
*   **Privacy First:** Works offline. Local-first database. You choose what to sync.

## Getting Started

### 1. Installation

*Currently in early development. Build from source:*

```bash
# Clone the repo
git clone https://github.com/thebyrdman-git/bugnosis.git
cd bugnosis

# Install CLI dependencies
cd cli
pip install -e .

# Run the GUI
cd ../gui
npm install
npm run tauri dev
```

### 2. Your First Scan

Use the CLI or the Desktop App to find your first target:

```bash
bugnosis smart-scan "python requests library"
```

## Roadmap

We are building the "Antivirus for Open Source Bugs".

*   **Phase 1:** Impact Engine & Smart Search (Current)
*   **Phase 2:** AI Co-Pilot & Rejection Coaching
*   **Phase 3:** Cloud Sync & Community Leaderboards

[View the full Roadmap](ROADMAP.md)

## Contributing

We welcome feedback on our vision and architecture!

Please check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get involved.

## License

MIT License. Free and open source forever.
