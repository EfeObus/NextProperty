# NextProperty Auto Git Update System

This system automatically commits and pushes changes to your GitHub repository when modifications are detected in your NextProperty AI project.

## Features

- **Automatic Change Detection**: Monitors file system for changes
- **Intelligent Commit Messages**: Generates meaningful commit messages based on file changes
- **File Filtering**: Ignores temporary files, logs, and other non-essential files
- **Multiple Operation Modes**: One-time update, watch mode, or interactive mode
- **Error Handling**: Robust error handling and logging
- **Background Service**: Can run as a system service
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Quick Start

### 1. Initial Setup

```bash
# Navigate to your project directory
cd "/Users/efeobukohwo/Desktop/Nextproperty Real Estate"

# Run the setup script
./scripts/git_auto_update.sh setup
```

### 2. Basic Usage

```bash
# Check for changes
./scripts/git_auto_update.sh check

# Update now (commit and push)
./scripts/git_auto_update.sh update

# Start watching for changes (runs continuously)
./scripts/git_auto_update.sh watch

# Show Git status
./scripts/git_auto_update.sh status
```

## Installation

### Manual Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r scripts/requirements_auto_update.txt
   ```

2. **Make scripts executable**:
   ```bash
   chmod +x scripts/auto_git_update.py
   chmod +x scripts/git_auto_update.sh
   ```

### Using the Setup Script

```bash
./scripts/git_auto_update.sh setup
```

This will:
- Create a virtual environment if needed
- Install all required dependencies
- Make scripts executable
- Prepare the system for use

## Usage Modes

### 1. One-Time Update
Run once and exit:
```bash
python scripts/auto_git_update.py --once --repo-path .
```

### 2. Watch Mode
Continuously monitor for changes:
```bash
python scripts/auto_git_update.py --watch --repo-path . --delay 30
```

### 3. Interactive Mode
Menu-driven interface:
```bash
python scripts/auto_git_update.py
```

### 4. Shell Script Interface
Easy-to-use commands:
```bash
./scripts/git_auto_update.sh [command]
```

Available commands:
- `setup` - Initial setup
- `check` - Check for changes
- `update` - Update now
- `watch` - Start watching
- `status` - Show Git status
- `install` - Install/update requirements

## Configuration

### Config File
Edit `scripts/config_auto_update.json` to customize:

```json
{
  "repository": {
    "remote_url": "https://github.com/EfeObus/NextProperty.git",
    "branch": "main",
    "auto_pull": true
  },
  "monitoring": {
    "watch_enabled": true,
    "update_delay": 30,
    "ignore_patterns": ["*.log", "__pycache__/", "*.pyc"]
  },
  "commit_settings": {
    "auto_generate_message": true,
    "include_file_count": true,
    "categorize_changes": true
  }
}
```

### Command Line Options

```bash
python scripts/auto_git_update.py --help
```

Options:
- `--repo-path`: Path to Git repository
- `--remote-url`: GitHub repository URL
- `--branch`: Git branch to use (default: main)
- `--watch`: Watch for file changes
- `--delay`: Delay in seconds before auto-update
- `--once`: Run once and exit

## Running as a Background Service

### macOS (LaunchAgent)

1. **Copy the plist file**:
   ```bash
   cp scripts/com.nextproperty.autoupdate.plist ~/Library/LaunchAgents/
   ```

2. **Load and start the service**:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.nextproperty.autoupdate.plist
   launchctl start com.nextproperty.autoupdate
   ```

3. **Check if running**:
   ```bash
   launchctl list | grep nextproperty
   ```

### Linux (SystemD)

1. **Copy the service file**:
   ```bash
   sudo cp scripts/nextproperty-auto-update.service /etc/systemd/system/
   ```

2. **Edit the service file** to update paths and username:
   ```bash
   sudo nano /etc/systemd/system/nextproperty-auto-update.service
   ```

3. **Enable and start the service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable nextproperty-auto-update.service
   sudo systemctl start nextproperty-auto-update.service
   ```

4. **Check status**:
   ```bash
   sudo systemctl status nextproperty-auto-update.service
   ```

## Intelligent Commit Messages

The system generates intelligent commit messages based on the types of files changed:

- **Security changes**: "Enhanced security features and XSS protection"
- **Model changes**: "Updated data models and database schema"
- **Route changes**: "Modified API routes and endpoints"
- **Template changes**: "Updated UI templates and views"
- **Documentation**: "Documentation updates and improvements"
- **Configuration**: "Configuration updates and settings"
- **Multiple categories**: "General updates and improvements - X files updated"

## File Filtering

The following files and directories are automatically ignored:

- Python bytecode (`__pycache__/`, `*.pyc`, `*.pyo`)
- Virtual environments (`venv/`, `.venv/`, `env/`)
- Log files (`*.log`, `logs/`)
- Database files (`*.db`, `*.sqlite`)
- Temporary files (`*.tmp`, `*.temp`)
- IDE files (`.vscode/`, `.idea/`)
- System files (`.DS_Store`)

## Logging

Logs are written to:
- Console output (if enabled)
- `logs/git_auto_update.log`

Log levels: DEBUG, INFO, WARNING, ERROR

## Troubleshooting

### Common Issues

1. **Permission denied**:
   ```bash
   chmod +x scripts/auto_git_update.py
   chmod +x scripts/git_auto_update.sh
   ```

2. **Module not found**:
   ```bash
   pip install -r scripts/requirements_auto_update.txt
   ```

3. **Git authentication**:
   - Ensure you have proper Git credentials configured
   - Use SSH keys or personal access tokens for HTTPS

4. **Service not starting**:
   - Check logs in `logs/` directory
   - Verify paths in service files
   - Check permissions

### Debugging

Enable debug logging by editing the Python script:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

View logs:
```bash
tail -f logs/git_auto_update.log
```

## Security Considerations

- The script only commits and pushes changes, never pulls destructive operations
- File filtering prevents sensitive files from being committed
- All operations are logged for audit purposes
- Service runs with user privileges, not root

## Integration with NextProperty AI

This auto-update system is designed specifically for the NextProperty AI project and:

- Understands the project structure
- Generates appropriate commit messages for different components
- Integrates with the existing logging system
- Respects the project's `.gitignore` patterns

## Support

For issues or questions:
1. Check the logs: `logs/git_auto_update.log`
2. Run in debug mode: `python scripts/auto_git_update.py --help`
3. Check Git status manually: `git status`

## License

This auto-update system is part of the NextProperty AI project and follows the same license terms.
