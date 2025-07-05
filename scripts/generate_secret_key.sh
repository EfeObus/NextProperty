#!/bin/bash
#
# Shell wrapper for the secret key generator
# This script can be used for automated execution via cron jobs
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_ROOT"

# Check if Python script exists
PYTHON_SCRIPT="$SCRIPT_DIR/generate_secret_key.py"
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Run the Python script
echo "Running secret key generator..."
python3 "$PYTHON_SCRIPT"

# Check exit status
if [ $? -eq 0 ]; then
    echo "Secret key generation completed successfully"
    
    # Optional: Restart the application if it's running
    # Uncomment the following lines if you want to automatically restart your Flask app
    # echo "Checking if Flask app is running..."
    # if pgrep -f "python.*app.py" > /dev/null; then
    #     echo "Restarting Flask application..."
    #     pkill -f "python.*app.py"
    #     sleep 2
    #     nohup python3 app.py > /dev/null 2>&1 &
    #     echo "Flask application restarted"
    # fi
else
    echo "Secret key generation failed"
    exit 1
fi
