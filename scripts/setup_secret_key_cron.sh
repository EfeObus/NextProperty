#!/bin/bash
#
# Cron Job Setup Script for Secret Key Auto-Generation
# This script sets up a cron job to automatically generate new secret keys every 30 days
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATOR_SCRIPT="$SCRIPT_DIR/generate_secret_key.sh"

# Cron job to run on the 1st of every month at 2:00 AM
CRON_SCHEDULE="0 2 1 * *"
CRON_COMMAND="$GENERATOR_SCRIPT >> /tmp/nextproperty_secret_key.log 2>&1"
CRON_JOB="$CRON_SCHEDULE $CRON_COMMAND"

echo "=== NextProperty AI Secret Key Cron Setup ==="
echo "This will set up automatic secret key generation every 30 days"
echo "Schedule: 1st of every month at 2:00 AM"
echo "Generator script: $GENERATOR_SCRIPT"
echo ""

# Check if generator script exists
if [ ! -f "$GENERATOR_SCRIPT" ]; then
    echo "Error: Generator script not found at $GENERATOR_SCRIPT"
    exit 1
fi

# Check if generator script is executable
if [ ! -x "$GENERATOR_SCRIPT" ]; then
    echo "Making generator script executable..."
    chmod +x "$GENERATOR_SCRIPT"
fi

echo "Current crontab entries:"
crontab -l 2>/dev/null | grep -v "nextproperty.*secret" || echo "No existing NextProperty secret key cron jobs found"
echo ""

# Ask for confirmation
read -p "Do you want to add the cron job? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cron job setup cancelled"
    exit 0
fi

# Backup current crontab
echo "Backing up current crontab..."
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null

# Add the new cron job
echo "Adding cron job..."
(crontab -l 2>/dev/null; echo "# NextProperty AI Secret Key Auto-Generation"; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo ""
    echo "Cron job details:"
    echo "  Schedule: $CRON_SCHEDULE (1st of every month at 2:00 AM)"
    echo "  Command: $CRON_COMMAND"
    echo "  Log file: /tmp/nextproperty_secret_key.log"
    echo ""
    echo "To view logs: tail -f /tmp/nextproperty_secret_key.log"
    echo "To remove this cron job: crontab -e"
    echo ""
    echo "Current crontab:"
    crontab -l | grep -A1 -B1 "NextProperty"
else
    echo "❌ Failed to add cron job"
    exit 1
fi

echo ""
echo "You can also run the secret key generator manually:"
echo "  $GENERATOR_SCRIPT"
