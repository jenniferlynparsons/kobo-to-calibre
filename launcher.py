#!/usr/bin/env python3
"""
Kobo-to-Calibre Sync Tool Launcher
Simple launcher script that can be run to start the GUI application.
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    """Launch the Kobo-to-Calibre sync tool."""
    
    print("🚀 Kobo-to-Calibre Sync Tool Launcher")
    print("=" * 50)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    main_script = script_dir / "main.py"
    
    print(f"📁 Project directory: {script_dir}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    
    # Check if main.py exists
    if not main_script.exists():
        print(f"❌ Error: main.py not found at {main_script}")
        print("Please make sure you're running this from the kobo-to-calibre project folder")
        input("Press Enter to exit...")
        return 1
    
    # Change to project directory
    os.chdir(script_dir)
    
    try:
        print("🔄 Starting application...")
        print("")
        
        # Launch the main application
        result = subprocess.run([sys.executable, "main.py"], cwd=script_dir)
        
        print("")
        if result.returncode == 0:
            print("✅ Application finished successfully")
        else:
            print(f"⚠️ Application exited with code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        return 130
        
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        return 1
    
    print("")
    print("Press Enter to close...")
    input()
    return 0

if __name__ == "__main__":
    sys.exit(main())