# Bugnosis Desktop GUI

Beautiful desktop application for finding and fixing high-impact open source bugs.

## Features

- **System Tray Icon**: Quick access from your system tray
- **Repository Scanning**: Scan any GitHub repository for high-impact bugs
- **Watch List**: Monitor multiple repositories
- **Real-time Statistics**: Track your impact and contributions
- **Analytics Dashboard**: Insights on bug distribution and recommendations
- **Desktop Notifications**: Get notified when scans complete

## Prerequisites

1. **Rust** (already installed)
2. **Node.js** (already installed)
3. **Bugnosis CLI** must be installed and in PATH:
   ```bash
   cd ../cli
   pip install -e .
   ```

4. **System dependencies** (Fedora/RHEL):
   ```bash
   sudo dnf install gtk3-devel webkit2gtk4.1-devel libappindicator-gtk3-devel
   ```

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run tauri dev
```

## Building

```bash
# Build for production
npm run tauri build
```

The built application will be in `src-tauri/target/release/bundle/`.

## Usage

1. Launch the application
2. The system tray icon will appear (look for the Bugnosis icon)
3. Click the icon to open the main window
4. Use the tabs to:
   - **Scan**: Scan individual repositories
   - **Watch List**: Add repos to monitor regularly
   - **Saved Bugs**: View all saved high-impact bugs
   - **Insights**: Get analytics on your bug database

## Tray Menu

Right-click the system tray icon for quick actions:
- **Show Window**: Open the main application window
- **Scan Watched Repos**: Trigger a scan of all watched repositories
- **Quit**: Exit the application

## Configuration

The GUI uses the same configuration as the CLI:
- Database: `~/.config/bugnosis/bugnosis.db`
- Config: `~/.config/bugnosis/config.json`
- Cache: `~/.cache/bugnosis/`

Set your API keys:
```bash
export GITHUB_TOKEN="ghp_..."
export GROQ_API_KEY="gsk_..."
```

## Technology Stack

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Rust + Tauri
- **CLI Integration**: Calls `bugnosis` commands via shell

## Troubleshooting

### "bugnosis command not found"
Make sure the CLI is installed and in your PATH:
```bash
which bugnosis
```

### System tray icon not showing
Some desktop environments require additional setup for system tray support.

### Build fails
Make sure you have all system dependencies installed (see Prerequisites).

## License

MIT
