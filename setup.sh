
#!/bin/bash
# ============================================================
# UAMS Framework - Complete Setup Script
# Installs all dependencies and initializes the system
# ============================================================

set -e

echo "╔════════════════════════════════════════════╗"
echo "║    UAMS Framework - Complete Setup         ║"
echo "║    Cybersec-Red Red Team Tools             ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "[*] Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "[✓] Working directory: $SCRIPT_DIR"
echo ""

# Step 1: Install system dependencies
echo "[1/6] Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-dev python3-pip python3-venv build-essential libssl-dev libffi-dev
elif command -v brew &> /dev/null; then
    brew install python3
else
    echo "[!] Neither apt nor brew found. Please install dependencies manually."
fi
echo "[✓] System dependencies installed"
echo ""

# Step 2: Create Python virtual environment (optional but recommended)
echo "[2/6] Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[✓] Virtual environment created"
else
    echo "[✓] Virtual environment already exists"
fi
echo ""

# Step 3: Activate virtual environment
echo "[3/6] Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
echo "[✓] Virtual environment activated"
echo ""

# Step 4: Upgrade pip and install requirements
echo "[4/6] Installing Python packages..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
echo "[✓] All packages installed successfully"
echo ""

# Step 5: Create necessary directories
echo "[5/6] Creating directory structure..."
mkdir -p payloads/bind_shell payloads/reverse_shell payloads/persistence
mkdir -p builder_engine/templates/base_app/smali/com/example/app
mkdir -p crypter_engine/templates web_server/logs web_server/ssl
mkdir -p c2_listener/commands c2_listener/logs c2_listener/web_interface
mkdir -p backend/templates backend/static backend/database
mkdir -p output apk_files phishing_sites generated_pages
echo "[✓] Directory structure created"
echo ""

# Step 6: Initialize database (will be done by the app on first run)
echo "[6/6] Preparing database..."
python -c "
import os
os.makedirs('backend/database', exist_ok=True)
print('[✓] Database directory ready')
"
echo ""

echo "╔════════════════════════════════════════════╗"
echo "║    ✅ Setup Complete!                      ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "To start the application, run:"
echo "  python run.py"
echo ""
echo "Or if you didn't activate the venv:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
