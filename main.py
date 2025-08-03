"""
Kobo-to-Calibre Sync Tool
Main entry point for the multi-library sync application.
"""

import sys
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from gui import KoboSyncGUI
from config_manager import ConfigManager
from sync_engine import SyncEngine


def main():
    """Main entry point for the Kobo-to-Calibre sync tool."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/kobo_sync.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Kobo-to-Calibre Sync Tool")
    
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        
        # Create and run GUI
        app = KoboSyncGUI(config_manager)
        app.run()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()