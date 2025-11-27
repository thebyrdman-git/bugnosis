# Developer Guide

Technical documentation for building and contributing to Bugnosis.

---

## Architecture Overview

Bugnosis consists of three main components:

1. **Discovery Engine** (Rust)
   - Background scanning of GitHub/GitLab
   - Impact scoring algorithm
   - Bug database (SQLite)

2. **Desktop App** (Tauri + React/Svelte)
   - User interface
   - AI integration
   - PR workflow automation

3. **System Tray** (Cross-platform)
   - Background service
   - Notifications
   - Quick actions

---

## Technology Stack

### Backend
- **Language:** Rust 1.70+
- **Database:** SQLite 3.40+
- **API Client:** reqwest, octocrab
- **Async Runtime:** tokio

### Frontend
- **Framework:** React 18+ or Svelte 4+
- **Desktop:** Tauri 1.5+
- **Styling:** Tailwind CSS
- **State:** Zustand or similar

### AI Integration
- **Primary:** Groq API (llama-3.1-70b)
- **Fallback:** OpenAI GPT-4
- **Local:** Ollama (optional)

---

## Development Setup

### Prerequisites

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Node.js 18+
# Use nvm, fnm, or your package manager

# System dependencies (Linux)
sudo dnf install webkit2gtk4.1-devel openssl-devel
```

### Clone and Build

```bash
git clone https://github.com/thebyrdman-git/bugnosis.git
cd bugnosis

# Install dependencies
npm install

# Build discovery engine
cd engine && cargo build --release

# Run desktop app in dev mode
npm run tauri dev
```

---

## Project Structure

```
bugnosis/
├── engine/                 # Rust discovery engine
│   ├── src/
│   │   ├── main.rs
│   │   ├── scanner.rs     # GitHub/GitLab scanning
│   │   ├── scoring.rs     # Impact calculation
│   │   └── db.rs          # SQLite interface
│   └── Cargo.toml
│
├── src/                    # Frontend (React/Svelte)
│   ├── components/
│   │   ├── Radar.tsx      # Bug list view
│   │   ├── Impact.tsx     # Analytics dashboard
│   │   └── AIAssist.tsx   # AI workflow
│   ├── lib/
│   │   ├── api.ts         # Backend communication
│   │   └── scoring.ts     # Impact score utilities
│   └── App.tsx
│
├── src-tauri/              # Tauri backend
│   ├── src/
│   │   ├── main.rs
│   │   ├── tray.rs        # System tray
│   │   └── commands.rs    # Frontend commands
│   └── Cargo.toml
│
├── docs/                   # Documentation
├── .github/                # CI/CD workflows
└── tests/                  # Test suites
```

---

## Core Components

### Impact Scoring Algorithm

Location: `engine/src/scoring.rs`

```rust
pub struct ImpactScore {
    pub total: u8,          // 0-100
    pub user_base: u8,      // 0-40 points
    pub severity: u8,       // 0-30 points
    pub ease: u8,           // 0-20 points
    pub time: u8,           // 0-10 points
}

impl ImpactScore {
    pub fn calculate(bug: &Bug) -> Self {
        let user_base = score_user_base(bug.affected_users);
        let severity = score_severity(bug.severity);
        let ease = score_ease(bug.complexity);
        let time = score_time(bug.estimated_hours);
        
        Self {
            total: user_base + severity + ease + time,
            user_base,
            severity,
            ease,
            time,
        }
    }
}
```

### Bug Scanner

Location: `engine/src/scanner.rs`

Scans repositories for:
- Open issues with "bug" label
- High comment/reaction count
- Recent activity
- Platform-specific breaks

### Database Schema

Location: `engine/src/db.rs`

```sql
CREATE TABLE bugs (
    id INTEGER PRIMARY KEY,
    repo TEXT NOT NULL,
    issue_number INTEGER,
    title TEXT,
    impact_score INTEGER,
    affected_users INTEGER,
    discovered_at TIMESTAMP,
    status TEXT
);

CREATE TABLE scans (
    id INTEGER PRIMARY KEY,
    repo TEXT NOT NULL,
    scanned_at TIMESTAMP,
    bugs_found INTEGER
);
```

---

## Building Components

### Discovery Engine

```bash
cd engine
cargo build --release
cargo test

# Run standalone
./target/release/bugnosis-engine scan --repo owner/repo
```

### Desktop App

```bash
# Development (hot reload)
npm run tauri dev

# Production build
npm run tauri build

# Outputs:
# - Linux: .deb, .rpm, .AppImage
# - macOS: .dmg, .app
# - Windows: .exe, .msi
```

### System Tray

Built into Tauri app. See `src-tauri/src/tray.rs`.

Platform-specific implementations:
- Linux: AppIndicator
- macOS: NSStatusBar  
- Windows: System Tray API

---

## Testing

### Rust Tests

```bash
cd engine
cargo test

# With coverage
cargo tarpaulin --out Html
```

### Frontend Tests

```bash
npm test              # Unit tests
npm run test:e2e      # End-to-end tests
```

### Integration Tests

```bash
npm run test:integration
```

---

## AI Integration

### API Keys

```bash
# Set environment variables
export GROQ_API_KEY="your-key"
export OPENAI_API_KEY="backup-key"
```

### Rate Limits

- Groq: 30 requests/minute (free tier)
- OpenAI: Varies by plan
- Implement exponential backoff

### Prompt Engineering

Location: `src/lib/prompts.ts`

Keep prompts focused:
- Bug diagnosis: What's broken and why
- Fix suggestions: How to fix it
- PR generation: Professional description

---

## Configuration

### User Config

Location: `~/.config/bugnosis/config.toml`

```toml
[scanning]
interval_minutes = 60
auto_scan = true

[ai]
provider = "groq"
model = "llama-3.1-70b-versatile"

[notifications]
enabled = true
min_impact_score = 70
```

### Developer Config

Location: `.env.development`

```bash
GROQ_API_KEY=your-key
LOG_LEVEL=debug
DATABASE_PATH=./dev.db
```

---

## Database Migrations

Using sqlx-cli:

```bash
cargo install sqlx-cli

# Create migration
sqlx migrate add create_bugs_table

# Run migrations
sqlx migrate run

# Rollback
sqlx migrate revert
```

---

## Debugging

### Rust Debugging

```bash
# With logs
RUST_LOG=debug cargo run

# With debugger
rust-gdb ./target/debug/bugnosis-engine
```

### Frontend Debugging

Chrome DevTools built into Tauri:
- Right-click → Inspect Element
- Or enable via config

### System Tray Debugging

```bash
# Linux - check logs
journalctl -f | grep bugnosis

# macOS - check Console.app
# Windows - check Event Viewer
```

---

## Performance Optimization

### Scanning Performance

- Parallel requests (tokio)
- Request batching
- Cache API responses
- Rate limit handling

### Database Performance

- Indexes on common queries
- Batch inserts
- Connection pooling
- Periodic vacuuming

### Frontend Performance

- Virtual scrolling for large lists
- Lazy loading
- Memoization
- Code splitting

---

## Release Process

1. Update version in Cargo.toml and package.json
2. Update CHANGELOG.md
3. Run full test suite
4. Build for all platforms
5. Create GitHub release
6. Upload binaries
7. Update documentation

### Versioning

Follow semantic versioning:
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

---

## CI/CD

GitHub Actions workflows:

- **Test:** Run on every PR
- **Build:** Create binaries for releases
- **Deploy:** Update GitHub Pages leaderboard

Location: `.github/workflows/`

---

## Contributing Code

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key points:
- Follow Rust style guide (rustfmt)
- Write tests for new features
- Update documentation
- Keep commits focused

---

## Common Tasks

### Add New Data Source

1. Create module in `engine/src/sources/`
2. Implement `BugSource` trait
3. Add to scanner registry
4. Write tests
5. Update docs

### Add New Impact Factor

1. Update `ImpactScore` struct
2. Add scoring function
3. Adjust weights
4. Update tests
5. Document in scoring guide

### Add New UI Tab

1. Create component in `src/components/`
2. Add route
3. Update navigation
4. Connect to backend API
5. Write tests

---

## Resources

### Documentation
- [Tauri Docs](https://tauri.app)
- [Rust Book](https://doc.rust-lang.org/book/)
- [React Docs](https://react.dev)

### Community
- GitHub Discussions
- Discord (coming soon)

### Tools
- rust-analyzer (IDE support)
- Tauri CLI
- cargo-watch (auto-rebuild)

---

## Getting Help

1. Check existing issues
2. Read documentation
3. Ask in GitHub Discussions
4. Join Discord community

For bugs, include:
- OS and version
- Bugnosis version
- Steps to reproduce
- Logs if available

---

## License

MIT - See [LICENSE](LICENSE) for details.

---

## Quick Reference

```bash
# Development
npm run tauri dev

# Build
npm run tauri build

# Test
cargo test && npm test

# Format
cargo fmt && npm run format

# Lint
cargo clippy && npm run lint
```

---

Last updated: November 2025


