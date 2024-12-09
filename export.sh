#!/bin/bash

# Strict mode
set -euo pipefail
IFS=$'\n\t'

# Global constants
readonly MARZBAN_ENV_ADDRESS="/opt/marzban/.env"
readonly MARZBAN_SQLITE_ADDRESS="/var/lib/marzban/db.sqlite3"
readonly EXPORT_DIR="/root/export"
readonly EXPORT_VENV_DIR="${EXPORT_DIR}/venv"
readonly GITHUB_REPO_URL="https://github.com/erfjab/migration/archive/refs/heads/refactor.zip"

# ANSI color codes
declare -r -A COLORS=(
    [RED]='\033[0;31m'
    [GREEN]='\033[0;32m'
    [YELLOW]='\033[0;33m'
    [BLUE]='\033[0;34m'
    [RESET]='\033[0m'
)

# Logging functions
log() { printf "${COLORS[BLUE]}[INFO]${COLORS[RESET]} %s\n" "$*"; }
warn() { printf "${COLORS[YELLOW]}[WARN]${COLORS[RESET]} %s\n" "$*" >&2; }
error() { printf "${COLORS[RED]}[ERROR]${COLORS[RESET]} %s\n" "$*" >&2; exit 1; }
success() { printf "${COLORS[GREEN]}[SUCCESS]${COLORS[RESET]} %s\n" "$*"; }

# Error handling
trap 'error "An error occurred. Exiting..."' ERR

# Utility functions
check_root() {
    [[ $EUID -eq 0 ]] || error "This script must be run as root"
}

# Prepare system dependencies
install_prerequisites() {
    log "Updating system and installing prerequisites..."
    apt update -y
    apt upgrade -y
    apt install -y python3 python3-pip python3-venv unzip wget
    success "Prerequisites installed successfully"
}

# Download export tool
download_export_tool() {
    log "Downloading Marzban export tool..."
    
    # Create export directory
    mkdir -p "${EXPORT_DIR}"
    cd /root

    # Download and extract
    wget -O refactor.zip "${GITHUB_REPO_URL}"
    unzip -o refactor.zip
    cp -r migration-refactor/export/* "${EXPORT_DIR}/"
    
    # Clean up
    rm -rf migration-refactor refactor.zip
    
    success "Export tool downloaded successfully"
}

# Set up Python virtual environment
setup_python_venv() {
    log "Setting up Python virtual environment..."
    
    cd "${EXPORT_DIR}"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment and install requirements
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    deactivate
    
    success "Python virtual environment set up successfully"
}

# Export Marzban data
export_marzban_data() {
    log "Exporting Marzban data..."
    
    cd "${EXPORT_DIR}"
    source venv/bin/activate
    
    # Run export script
    python3 export.py
    
    # Verify export file
    if [[ ! -f "marzban.json" ]]; then
        error "Export failed: marzban.json not generated"
    fi
    
    deactivate
    
    success "Marzban data exported successfully to ${EXPORT_DIR}/marzban.json"
}

# Main execution
main() {
    # Ensure script is run as root
    check_root
    
    # Execute steps
    install_prerequisites
    download_export_tool
    setup_python_venv
    export_marzban_data
    
    # Final success message
    success "Marzban data export process completed successfully!"
    log "Export file location: ${EXPORT_DIR}/marzban.json"
}

# Run the main function
main