#!/bin/bash
# GRAPE Recorder Installation Script
# Installs grape-recorder to /opt/grape-recorder with standard Linux paths

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== GRAPE Recorder Installation ===${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: Do not run this script as root${NC}"
    echo "Run as a regular user. The script will use sudo when needed."
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Installation paths
INSTALL_DIR="/opt/grape-recorder"
LOG_DIR="/var/log/grape-recorder"
DATA_DIR="/var/lib/timestd"
HF_TIMESTD_DIR="/opt/hf-timestd"

echo "Installation directories:"
echo "  Install: $INSTALL_DIR"
echo "  Logs:    $LOG_DIR"
echo "  Data:    $DATA_DIR"
echo ""

# Check for Python 3.9+
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo -e "${RED}Error: Python 3.9 or newer required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Create installation directory
echo -e "${YELLOW}Creating installation directory...${NC}"
sudo mkdir -p "$INSTALL_DIR"
sudo chown $USER:$USER "$INSTALL_DIR"
echo -e "${GREEN}✓ Created $INSTALL_DIR${NC}"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv "$INSTALL_DIR/venv"
echo -e "${GREEN}✓ Created virtual environment${NC}"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip > /dev/null
echo -e "${GREEN}✓ Upgraded pip${NC}"

# Install hf-timestd if available
echo -e "${YELLOW}Checking for hf-timestd...${NC}"

# First check if hf-timestd is already installed in the system
if python3 -c "import hf_timestd" 2>/dev/null; then
    echo -e "${GREEN}✓ hf-timestd already installed in system${NC}"
    echo "  Creating access to system packages..."
    # Allow venv to access system packages
    rm -f "$INSTALL_DIR/venv/pyvenv.cfg"
    python3 -m venv --system-site-packages "$INSTALL_DIR/venv"
elif [ -d "$HF_TIMESTD_DIR" ]; then
    echo -e "${YELLOW}Attempting to install hf-timestd from $HF_TIMESTD_DIR...${NC}"
    if "$INSTALL_DIR/venv/bin/pip" install -e "$HF_TIMESTD_DIR" > /tmp/hf-timestd-install.log 2>&1; then
        echo -e "${GREEN}✓ Installed hf-timestd from source${NC}"
    else
        echo -e "${YELLOW}Warning: Could not install hf-timestd from source${NC}"
        echo "  Error log saved to /tmp/hf-timestd-install.log"
        echo "  Checking if hf-timestd venv exists..."
        
        # Try to use hf-timestd's own venv if it exists
        if [ -d "$HF_TIMESTD_DIR/venv" ]; then
            echo -e "${YELLOW}Found hf-timestd venv, creating symlink...${NC}"
            # This is a workaround - we'll document that hf-timestd must be installed separately
            echo -e "${YELLOW}Please ensure hf-timestd is properly installed${NC}"
        fi
    fi
else
    echo -e "${YELLOW}Warning: hf-timestd not found${NC}"
    echo "  grape-recorder requires hf-timestd to be installed"
    echo "  You can install it later or ensure it's in your Python path"
fi

# Install grape-recorder
echo -e "${YELLOW}Installing grape-recorder...${NC}"
"$INSTALL_DIR/venv/bin/pip" install -e "$SCRIPT_DIR[drf]" > /dev/null
echo -e "${GREEN}✓ Installed grape-recorder${NC}"

# Create log directory
echo -e "${YELLOW}Creating log directory...${NC}"
sudo mkdir -p "$LOG_DIR"
sudo chown $USER:$USER "$LOG_DIR"
echo -e "${GREEN}✓ Created $LOG_DIR${NC}"

# Create data directory
echo -e "${YELLOW}Creating data directory...${NC}"
sudo mkdir -p "$DATA_DIR"
sudo chown $USER:$USER "$DATA_DIR"
echo -e "${GREEN}✓ Created $DATA_DIR${NC}"

# Create symlinks to binaries (optional)
echo ""
read -p "Create symlinks in /usr/local/bin? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Creating symlinks...${NC}"
    sudo ln -sf "$INSTALL_DIR/venv/bin/grape-recorder" /usr/local/bin/grape-recorder
    sudo ln -sf "$INSTALL_DIR/venv/bin/grape-decimate" /usr/local/bin/grape-decimate
    sudo ln -sf "$INSTALL_DIR/venv/bin/grape-spectrogram" /usr/local/bin/grape-spectrogram
    sudo ln -sf "$INSTALL_DIR/venv/bin/grape-package-drf" /usr/local/bin/grape-package-drf
    sudo ln -sf "$INSTALL_DIR/venv/bin/grape-upload" /usr/local/bin/grape-upload
    echo -e "${GREEN}✓ Created symlinks in /usr/local/bin${NC}"
fi

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Commands are available at:"
echo "  $INSTALL_DIR/venv/bin/grape-recorder"
echo "  $INSTALL_DIR/venv/bin/grape-decimate"
echo "  $INSTALL_DIR/venv/bin/grape-spectrogram"
echo "  $INSTALL_DIR/venv/bin/grape-package-drf"
echo "  $INSTALL_DIR/venv/bin/grape-upload"
echo ""
echo "Logs will be written to: $LOG_DIR/grape-recorder.log"
echo "Data will be stored in:  $DATA_DIR/products/"
echo ""
echo "To verify installation:"
echo "  $INSTALL_DIR/venv/bin/grape-recorder --help"
