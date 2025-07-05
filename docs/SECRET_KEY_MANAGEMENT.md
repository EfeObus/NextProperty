# Secret Key Management System

This system automatically generates and manages SECRET_KEY rotation for the NextProperty AI application with 30-day expiry periods.

## Files Overview

### 1. `generate_secret_key.py`
Main Python script that:
- Generates cryptographically secure 64-character secret keys
- Checks if current key has expired
- Updates `.env` file with new SECRET_KEY and EXPIRY_DATE
- Provides interactive prompts for manual execution

### 2. `generate_secret_key.sh`
Shell wrapper script for:
- Automated execution via cron jobs
- Optional application restart functionality
- Error handling and logging

### 3. `setup_secret_key_cron.sh`
Cron job setup script that:
- Configures automatic secret key generation every 30 days
- Schedules execution for 1st of every month at 2:00 AM
- Provides backup and logging functionality

## Quick Start

### Manual Secret Key Generation
```bash
# Navigate to project directory
cd "/Users/efeobukohwo/Desktop/Nextproperty Real Estate"

# Run the Python script directly
python3 scripts/generate_secret_key.py

# Or use the shell wrapper
./scripts/generate_secret_key.sh
```

### Automated Setup (Recommended)
```bash
# Set up automatic secret key rotation
./scripts/setup_secret_key_cron.sh
```

## Features

### 🔐 Security
- Uses `secrets.token_hex()` for cryptographically secure key generation
- 64-character (256-bit) secret keys
- No key reuse or predictable patterns

### ⏰ Automatic Expiry
- 30-day expiry period from generation date
- Automatic expiry checking before generation
- ISO format date storage (YYYY-MM-DD)

### 🔄 Smart Updates
- Regex-based .env file updating
- Preserves file structure and comments
- Handles existing shell command formats

### 📝 Logging
- Execution logs stored in `/tmp/nextproperty_secret_key.log`
- Detailed status messages and error reporting
- Cron job activity tracking

## Configuration

### Environment File Format
The system expects the following format in `.env`:
```properties
SECRET_KEY=your_secret_key_here
EXPIRY_DATE=2025-08-04
```

### Cron Schedule
Default schedule: `0 2 1 * *` (1st of every month at 2:00 AM)

To modify the schedule, edit the `CRON_SCHEDULE` variable in `setup_secret_key_cron.sh`.

## Manual Operations

### Check Current Key Status
```bash
python3 scripts/generate_secret_key.py
# Will show expiry status without generating new key if not expired
```

### Force New Key Generation
```bash
python3 scripts/generate_secret_key.py
# Answer 'y' when prompted if key is not expired
```

### View Cron Jobs
```bash
crontab -l | grep nextproperty
```

### View Logs
```bash
tail -f /tmp/nextproperty_secret_key.log
```

### Remove Cron Job
```bash
crontab -e
# Delete the NextProperty secret key lines
```

## Application Restart

The shell script includes optional application restart functionality. To enable:

1. Edit `scripts/generate_secret_key.sh`
2. Uncomment the restart section at the bottom
3. Adjust the process detection pattern if needed

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x scripts/*.sh
   ```

2. **Python Script Not Found**
   - Ensure you're running from the project root directory
   - Check that `scripts/generate_secret_key.py` exists

3. **Cron Job Not Running**
   - Check cron service: `sudo launchctl list | grep cron`
   - Verify cron job: `crontab -l`
   - Check logs: `tail /tmp/nextproperty_secret_key.log`

4. **Invalid Date Format**
   - The system handles shell command formats automatically
   - Manually fix `.env` if needed: `EXPIRY_DATE=2025-08-04`

### Log Locations
- Cron execution: `/tmp/nextproperty_secret_key.log`
- Application logs: `logs/` directory
- Cron system logs: `/var/log/cron` (if available)

## Security Best Practices

1. **Never commit `.env` to version control**
2. **Regularly check log files for unauthorized access**
3. **Use file permissions to protect scripts**:
   ```bash
   chmod 750 scripts/
   chmod 740 scripts/*.py scripts/*.sh
   ```
4. **Monitor secret key rotation in application logs**

## Dependencies

- Python 3.6+
- Standard library modules: `os`, `secrets`, `re`, `datetime`, `pathlib`
- Unix-like system with cron support
- Bash shell for automation scripts

## Integration Notes

After secret key rotation:
1. Application must be restarted to use new key
2. Existing sessions may become invalid
3. Consider graceful restart mechanisms for production

## Support

For issues or questions about the secret key management system, check:
1. Application logs in `logs/` directory
2. Cron execution logs in `/tmp/nextproperty_secret_key.log`
3. Verify `.env` file format and permissions
