#!/bin/bash
# GRAPE Recorder Uninstallation Script
# Removes grape-recorder installation from /opt/grape-recorder

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== GRAPE Recorder Uninstallation ===${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: Do not run this script as root${NC}"
    echo "Run as a regular user. The script will use sudo when needed."
    exit 1
fi

# Installation paths
INSTALL_DIR="/opt/grape-recorder"
LOG_DIR="/var/log/grape-recorder"
DATA_DIR="/var/lib/grape-recorder"

# Check if installation exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}grape-recorder is not installed at $INSTALL_DIR${NC}"
    exit 0
fi

echo "This will remove:"
echo "  - Installation: $INSTALL_DIR"
echo "  - Symlinks in /usr/local/bin"
echo ""
echo "Optional (will prompt):"
echo "  - Logs: $LOG_DIR"
echo "  - Data: $DATA_DIR"
echo ""

read -p "Continue with uninstallation? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

# Remove symlinks
echo -e "${YELLOW}Removing symlinks...${NC}"
sudo rm -f /usr/local/bin/grape-recorder
sudo rm -f /usr/local/bin/grape-decimate
sudo rm -f /usr/local/bin/grape-spectrogram
sudo rm -f /usr/local/bin/grape-package-drf
sudo rm -f /usr/local/bin/grape-upload
echo -e "${GREEN}✓ Removed symlinks${NC}"

# Remove installation directory
echo -e "${YELLOW}Removing installation directory...${NC}"
sudo rm -rf "$INSTALL_DIR"
echo -e "${GREEN}✓ Removed $INSTALL_DIR${NC}"

# Ask about log directory
if [ -d "$LOG_DIR" ]; then
    echo ""
    read -p "Remove log directory $LOG_DIR? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -rf "$LOG_DIR"
        echo -e "${GREEN}✓ Removed $LOG_DIR${NC}"
    else
        echo -e "${YELLOW}Kept $LOG_DIR${NC}"
    fi
fi

# Ask about data directory
if [ -d "$DATA_DIR" ]; then
    echo ""
    echo -e "${RED}WARNING: This will delete all processed data!${NC}"
    read -p "Remove data directory $DATA_DIR? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -rf "$DATA_DIR"
        echo -e "${GREEN}✓ Removed $DATA_DIR${NC}"
    else
        echo -e "${YELLOW}Kept $DATA_DIR${NC}"
    fi
fi

echo ""
echo -e "${GREEN}=== Uninstallation Complete ===${NC}"
