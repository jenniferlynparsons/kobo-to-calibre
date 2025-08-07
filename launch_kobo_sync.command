#!/bin/bash
# Kobo-to-Calibre Sync Launcher for macOS
# Double-click this file to launch the sync tool

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python 3 is required but not found in PATH"
    echo "Please install Python 3 and try again"
    echo "Press any key to exit..."
    read -n 1 -s
    exit 1
fi

# Check if the main.py file exists
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found in project directory"
    echo "Please make sure you're running this from the kobo-to-calibre project folder"
    echo "Press any key to exit..."
    read -n 1 -s
    exit 1
fi

echo "🚀 Starting Kobo-to-Calibre Sync Tool..."
echo "📁 Working directory: $SCRIPT_DIR"
echo "🐍 Using Python: $PYTHON_CMD"
echo ""

# Launch the application
$PYTHON_CMD main.py

# If we get here, the application has exited
echo ""
echo "✅ Application finished"
echo "Press any key to close this window..."
read -n 1 -s