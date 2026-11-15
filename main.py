"""
Kobo-to-Calibre Sync Tool
Main entry point for the multi-library sync application.
"""

import json
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from gui import KoboSyncGUI


def main():
    """Main entry point for the Kobo-to-Calibre sync tool."""
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('logs/kobo_sync.log', maxBytes=5_000_000, backupCount=5),
            logging.StreamHandler()
        ]
    )
    logging.getLogger(__name__).info("Starting Kobo-to-Calibre Sync Tool")

    config = json.loads(Path("config/library_mappings.json").read_text())
    KoboSyncGUI(config).run()


if __name__ == "__main__":
    main()
