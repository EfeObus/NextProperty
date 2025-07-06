#!/bin/bash

# Auto Git Update Script for NextProperty AI
# This script provides easy commands to manage automatic Git updates

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_SCRIPT="$SCRIPT_DIR/auto_git_update.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements_auto_update.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created at $VENV_DIR"
    fi
}

# Function to install requirements
install_requirements() {
    print_info "Installing requirements..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install main project requirements if they exist
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip install -r "$PROJECT_DIR/requirements.txt"
    fi
    
    # Install auto-update specific requirements
    pip install -r "$REQUIREMENTS_FILE"
    
    print_success "Requirements installed successfully"
}

# Function to setup the auto-update system
setup() {
    print_info "Setting up Auto Git Update system..."
    
    check_venv
    install_requirements
    
    # Make the Python script executable
    chmod +x "$PYTHON_SCRIPT"
    
    print_success "Auto Git Update system setup complete!"
    print_info "You can now use the following commands:"
    echo "  $0 check    - Check for changes"
    echo "  $0 update   - Update now"
    echo "  $0 watch    - Start watching for changes"
    echo "  $0 status   - Show Git status"
}

# Function to check for changes
check_changes() {
    print_info "Checking for changes..."
    source "$VENV_DIR/bin/activate"
    python "$PYTHON_SCRIPT" --once --repo-path "$PROJECT_DIR"
}

# Function to update now
update_now() {
    print_info "Performing auto-update..."
    source "$VENV_DIR/bin/activate"
    python "$PYTHON_SCRIPT" --once --repo-path "$PROJECT_DIR"
}

# Function to start watching
start_watching() {
    print_info "Starting file watcher..."
    print_warning "Press Ctrl+C to stop watching"
    source "$VENV_DIR/bin/activate"
    python "$PYTHON_SCRIPT" --watch --repo-path "$PROJECT_DIR"
}

# Function to show Git status
show_status() {
    print_info "Git status:"
    cd "$PROJECT_DIR"
    git status
    echo ""
    print_info "Recent commits:"
    git log --oneline -10
}

# Function to show help
show_help() {
    echo "NextProperty Auto Git Update Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup     - Setup the auto-update system (run this first)"
    echo "  check     - Check for uncommitted changes"
    echo "  update    - Commit and push changes now"
    echo "  watch     - Start watching for file changes"
    echo "  status    - Show Git repository status"
    echo "  install   - Install/update requirements"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup     # Initial setup"
    echo "  $0 watch     # Start automatic monitoring"
    echo "  $0 update    # Manual update"
}

# Main script logic
case "${1:-help}" in
    "setup")
        setup
        ;;
    "check")
        check_changes
        ;;
    "update")
        update_now
        ;;
    "watch")
        start_watching
        ;;
    "status")
        show_status
        ;;
    "install")
        check_venv
        install_requirements
        ;;
    "help"|*)
        show_help
        ;;
esac
