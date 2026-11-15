"""
Calibre Updater - Update custom columns in Calibre libraries
"""

import subprocess
import sqlite3
import logging
import shutil
from pathlib import Path
from collections import defaultdict
from typing import List, Dict
from datetime import datetime

from book_matcher import BookMatch
from kobo_reader import RATINGS
from library_manager import CalibreLibrary


class CalibreUpdater:
    """Updates Calibre metadata using calibredb commands."""
    
    def __init__(self):
        """Initialize Calibre updater."""
        self.logger = logging.getLogger(__name__)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.calibredb_path = self._find_calibredb_path()
    
    def _find_calibredb_path(self) -> str:
        """Find calibredb on PATH or in the macOS app bundle."""
        path = shutil.which('calibredb') or shutil.which('/Applications/calibre.app/Contents/MacOS/calibredb')
        if not path:
            raise RuntimeError("calibredb executable not found. Please ensure Calibre is installed.")
        self.logger.info(f"Found calibredb at: {path}")
        return path
    
    def _log_calibredb_error(self, operation: str, cmd: List[str], result: subprocess.CompletedProcess):
        """Log detailed error information for calibredb command failures."""
        self.logger.error(f"Failed to {operation}")
        self.logger.error(f"Command: {' '.join(cmd)}")
        self.logger.error(f"Return code: {result.returncode}")
        if result.stderr:
            self.logger.error(f"Error output: {result.stderr.strip()}")
        if result.stdout:
            self.logger.error(f"Standard output: {result.stdout.strip()}")
    
    def test_calibredb_connection(self, library: CalibreLibrary) -> bool:
        """Test if calibredb can connect to the library."""
        try:
            cmd = [self.calibredb_path, 'list', '--library-path', str(library.path), '--limit', '1']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.debug(f"Successfully connected to {library.name}")
                return True
            else:
                # Check for specific Calibre running error
                if "Another calibre program" in result.stderr:
                    self.logger.error(
                        f"❌ Cannot access {library.name}: Calibre GUI or server is running.\n"
                        f"   Please close the Calibre application and try again.\n"
                        f"   You cannot run this sync tool while Calibre is open."
                    )
                else:
                    self._log_calibredb_error(f"connect to library {library.name}", cmd, result)
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout testing connection to {library.name}")
            return False
        except Exception as e:
            self.logger.error(f"Error testing connection to {library.name}: {e}")
            return False
    
    def backup_library(self, library: CalibreLibrary) -> bool:
        """Create backup of library's metadata.db file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{library.name}_metadata_{timestamp}.db"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(library.metadata_db_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup {library.name}: {e}")
            return False
    
    def _column_labels(self, library: CalibreLibrary) -> set:
        """Labels of the library's custom columns (empty on error)."""
        try:
            conn = sqlite3.connect(library.metadata_db_path)
            labels = {row[0] for row in conn.execute("SELECT label FROM custom_columns")}
            conn.close()
            return labels
        except sqlite3.Error as e:
            self.logger.error(f"Error checking custom columns: {e}")
            return set()
    
    def create_custom_column(self, library: CalibreLibrary, column_name: str, display_name: str) -> bool:
        """Create a custom column using calibredb."""
        try:
            self.logger.info(f"Creating custom column '{column_name}' ({display_name}) in {library.name}")
            
            cmd = [
                self.calibredb_path, 'add_custom_column',
                '--library-path', str(library.path),
                column_name,
                display_name,
                'text',
                '--display', '{}',
                '--is-multiple'
            ]
            
            self.logger.debug(f"Column creation command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Successfully created custom column {column_name} in {library.name}")
                return True
            else:
                # Check if column already exists
                if "already exists" in result.stderr.lower():
                    self.logger.info(f"✅ Custom column {column_name} already exists in {library.name}")
                    return True
                self._log_calibredb_error("create custom column", cmd, result)
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout creating custom column {column_name} (command took > 30s)")
            return False
        except Exception as e:
            self.logger.error(f"Error creating custom column {column_name}: {e}")
            return False
    
    def ensure_custom_columns(self, library: CalibreLibrary) -> bool:
        """Ensure required custom columns exist."""
        labels = self._column_labels(library)
        self.logger.info(f"📋 Found custom columns in {library.name}: {sorted(labels)}")
        
        success = True
        
        if 'myratings' not in labels:
            self.logger.info(f"⚠️ Creating missing 'myratings' column in {library.name}")
            if not self.create_custom_column(library, 'myratings', 'My Ratings'):
                success = False
        else:
            self.logger.info(f"✅ 'myratings' column already exists in {library.name}")
        
        # Genres are opt-in per library: never create 'my_genres', only write to it if it exists
        if 'my_genres' not in labels:
            self.logger.info(f"⏭️ No 'my_genres' column in {library.name}, genres will be skipped")
        else:
            self.logger.info(f"✅ 'my_genres' column already exists in {library.name}")
        
        return success
    
    def update_book_metadata(self, match: BookMatch) -> bool:
        """Update a single book's metadata."""
        try:
            # Separate rating and genre collections
            rating_collections = self._get_rating_collections(match.kobo_book.collections)
            genre_collections = self._get_genre_collections(match.kobo_book.collections)
            
            # Update My Ratings column
            if rating_collections:
                if not self._update_custom_column(
                    match.library, 
                    match.calibre_book_id, 
                    'myratings', 
                    rating_collections
                ):
                    return False
            
            # Update My Genres column
            if genre_collections and 'my_genres' in self._column_labels(match.library):
                if not self._update_custom_column(
                    match.library, 
                    match.calibre_book_id, 
                    'my_genres', 
                    genre_collections
                ):
                    return False
            
            self.logger.debug(f"Updated book ID {match.calibre_book_id} in {match.library.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating book metadata: {e}")
            return False
    
    def _get_rating_collections(self, collections: List[str]) -> List[str]:
        """Rating collections (KoboReader already renamed them to RATINGS values)."""
        return [c for c in collections if c in RATINGS.values()]
    
    def _get_genre_collections(self, collections: List[str]) -> List[str]:
        """Every non-rating collection, without a leading '| '."""
        return [c.replace("| ", "").strip() for c in collections if c not in RATINGS.values()]
    
    def _update_custom_column(self, library: CalibreLibrary, book_id: int, column: str, values: List[str]) -> bool:
        """Update a custom column for a specific book."""
        try:
            # Join values with comma for multiple values (Calibre expects comma-separated values)
            if not values:
                self.logger.debug(f"No values to update for {column} on book {book_id}")
                return True
                
            value_string = ','.join(values)
            self.logger.debug(f"Updating book {book_id} {column} with: {value_string}")
            
            # Use proper calibredb syntax with #column_name: prefix for custom columns
            cmd = [
                self.calibredb_path, 'set_metadata',
                '--library-path', str(library.path),
                str(book_id),
                '--field', f'#{column}:{value_string}'
            ]
            
            self.logger.debug(f"Update command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.debug(f"✅ Successfully updated #{column} for book {book_id} with: {value_string}")
                return True
            else:
                self._log_calibredb_error(f"update {column}", cmd, result)
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout updating {column} for book {book_id} (command took > 30s)")
            return False
        except Exception as e:
            self.logger.error(f"Error updating custom column {column} for book {book_id}: {e}")
            return False
    
    def bulk_update(self, matches: List[BookMatch]) -> Dict[str, int]:
        """Update multiple books and return statistics."""
        stats = {
            'total': len(matches),
            'successful': 0,
            'failed': 0,
            'libraries_updated': set()
        }
        
        by_library = defaultdict(list)
        for match in matches:
            by_library[match.library.name].append(match)
        
        # Process each library
        for library_name, library_matches in by_library.items():
            library = library_matches[0].library  # Get library object
            
            self.logger.info(f"Updating {len(library_matches)} books in {library_name}")
            
            # Test calibredb connection to library
            if not self.test_calibredb_connection(library):
                self.logger.error(f"Skipping {library_name} due to connection failure")
                stats['failed'] += len(library_matches)
                continue
            
            # Backup library before changes
            if not self.backup_library(library):
                self.logger.error(f"Skipping {library_name} due to backup failure")
                stats['failed'] += len(library_matches)
                continue
            
            # Ensure custom columns exist
            if not self.ensure_custom_columns(library):
                self.logger.error(f"Failed to ensure custom columns in {library_name}")
                stats['failed'] += len(library_matches)
                continue
            
            # Update each book
            for match in library_matches:
                if self.update_book_metadata(match):
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1
            
            stats['libraries_updated'].add(library_name)
        
        self.logger.info(f"Bulk update complete: {stats['successful']} successful, {stats['failed']} failed")
        return stats
