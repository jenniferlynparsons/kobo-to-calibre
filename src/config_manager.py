"""
Configuration Manager - Handle configuration and library mappings
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional


class ConfigManager:
    """Manages configuration files and user preferences."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize configuration manager."""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Configuration file paths
        self.library_mappings_file = self.config_dir / "library_mappings.json"
        self.rating_collections_file = self.config_dir / "rating_collections.json"
        self.sync_preferences_file = self.config_dir / "sync_preferences.json"
        
        # Initialize default configurations
        self._create_default_configs()
    
    def _create_default_configs(self):
        """Create default configuration files if they don't exist."""
        
        # Default library mappings
        if not self.library_mappings_file.exists():
            default_mappings = {
                "search_paths": [
                    str(Path.home() / "Documents"),
                    str(Path.home() / "Downloads"),
                    str(Path.cwd()),
                    "/Users/jenniferparsons/Engineering/Projects/kobo-to-calibre"
                ],
                "discovered_libraries": {},
                "primary_library": "",
                "kobo_database_path": "KoboReader.sqlite"
            }
            self._save_json(self.library_mappings_file, default_mappings)
        
        # Default rating collections
        if not self.rating_collections_file.exists():
            default_ratings = {
                "rating_collections": {
                    "Evergreen": "Evergreen",
                    "Absolute Favorite": "Absolute Favorite",
                    "Favorites": "Favorites", 
                    "Great": "Great"
                },
                "custom_columns": {
                    "ratings_column": "my_ratings",
                    "genres_column": "my_genres"
                }
            }
            self._save_json(self.rating_collections_file, default_ratings)
        
        # Default sync preferences
        if not self.sync_preferences_file.exists():
            default_prefs = {
                "matching": {
                    "strict_matching": True,
                    "manual_conflict_resolution": True,
                    "skip_uncertain_matches": True
                },
                "backup": {
                    "backup_metadata_db": True,
                    "backup_directory": "backups"
                },
                "logging": {
                    "level": "INFO",
                    "file_logging": True,
                    "console_logging": True
                },
                "ui": {
                    "dry_run_optional": True,
                    "verbose_progress": True,
                    "gui_enabled": True
                },
                "conflict_resolution": {
                    "default_action": "ask_user",
                    "remember_choices": True,
                    "auto_apply_similar": False
                }
            }
            self._save_json(self.sync_preferences_file, default_prefs)
    
    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON configuration file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return {}
    
    def _save_json(self, file_path: Path, data: Dict) -> bool:
        """Save data to JSON configuration file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {e}")
            return False
    
    def get_library_mappings(self) -> Dict:
        """Get library mappings configuration."""
        return self._load_json(self.library_mappings_file)
    
    def save_library_mappings(self, mappings: Dict) -> bool:
        """Save library mappings configuration."""
        return self._save_json(self.library_mappings_file, mappings)
    
    def get_rating_collections(self) -> Dict:
        """Get rating collections configuration."""
        return self._load_json(self.rating_collections_file)
    
    def get_sync_preferences(self) -> Dict:
        """Get sync preferences configuration."""
        return self._load_json(self.sync_preferences_file)
    
    def save_sync_preferences(self, preferences: Dict) -> bool:
        """Save sync preferences configuration."""
        return self._save_json(self.sync_preferences_file, preferences)
    
    def get_kobo_database_path(self) -> str:
        """Get path to Kobo database."""
        mappings = self.get_library_mappings()
        return mappings.get("kobo_database_path", "KoboReader.sqlite")
    
    def get_search_paths(self) -> List[str]:
        """Get list of paths to search for Calibre libraries."""
        mappings = self.get_library_mappings()
        return mappings.get("search_paths", [])
    
    def update_discovered_libraries(self, libraries: Dict) -> bool:
        """Update the list of discovered Calibre libraries."""
        mappings = self.get_library_mappings()
        mappings["discovered_libraries"] = libraries
        return self.save_library_mappings(mappings)
    
    def set_primary_library(self, library_name: str) -> bool:
        """Set the primary library name."""
        mappings = self.get_library_mappings()
        mappings["primary_library"] = library_name
        return self.save_library_mappings(mappings)
    
    def get_primary_library_name(self) -> str:
        """Get the primary library name."""
        mappings = self.get_library_mappings()
        return mappings.get("primary_library", "")
    
    def is_strict_matching_enabled(self) -> bool:
        """Check if strict matching is enabled."""
        prefs = self.get_sync_preferences()
        return prefs.get("matching", {}).get("strict_matching", True)
    
    def is_backup_enabled(self) -> bool:
        """Check if backup is enabled."""
        prefs = self.get_sync_preferences()
        return prefs.get("backup", {}).get("backup_metadata_db", True)
    
    def get_logging_config(self) -> Dict:
        """Get logging configuration."""
        prefs = self.get_sync_preferences()
        return prefs.get("logging", {
            "level": "INFO",
            "file_logging": True,
            "console_logging": True
        })
    
    def get_ui_config(self) -> Dict:
        """Get UI configuration."""
        prefs = self.get_sync_preferences()
        return prefs.get("ui", {
            "dry_run_optional": True,
            "verbose_progress": True,
            "gui_enabled": True
        })
    
    def get_conflict_resolution_config(self) -> Dict:
        """Get conflict resolution configuration."""
        prefs = self.get_sync_preferences()
        return prefs.get("conflict_resolution", {
            "default_action": "ask_user",
            "remember_choices": True,
            "auto_apply_similar": False
        })