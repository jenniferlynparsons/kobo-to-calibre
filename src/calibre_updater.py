"""
Calibre Updater - Update custom columns in Calibre libraries
"""

import subprocess
import sqlite3
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from book_matcher import BookMatch
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
        """Find calibredb executable path."""
        # Common paths where calibredb might be found
        possible_paths = [
            'calibredb',  # If in PATH
            '/Applications/calibre.app/Contents/MacOS/calibredb',  # macOS app install
            '/usr/bin/calibredb',  # Linux system install
            '/usr/local/bin/calibredb',  # Linux user install
            'C:\\Program Files\\Calibre2\\calibredb.exe',  # Windows
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.logger.info(f"Found calibredb at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        self.logger.error("calibredb not found in any common locations")
        raise RuntimeError("calibredb executable not found. Please ensure Calibre is installed.")
    
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
    
    def check_custom_columns(self, library: CalibreLibrary) -> Dict[str, bool]:
        """Check if required custom columns exist in library."""
        try:
            conn = sqlite3.connect(library.metadata_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT label, name FROM custom_columns")
            existing_columns = cursor.fetchall()
            conn.close()
            
            # Create mapping of labels to display names for debugging
            column_map = {row[0]: row[1] for row in existing_columns}
            labels = [row[0] for row in existing_columns]
            
            self.logger.info(f"📋 Found custom columns in {library.name}: {column_map}")
            
            result = {
                'my_ratings': 'myratings' in labels,
                'my_genres': 'my_genres' in labels
            }
            
            self.logger.info(f"✅ Column check results for {library.name}: {result}")
            return result
            
        except sqlite3.Error as e:
            self.logger.error(f"Error checking custom columns: {e}")
            return {'my_ratings': False, 'my_genres': False}
    
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
        columns = self.check_custom_columns(library)
        
        success = True
        
        if not columns['my_ratings']:
            self.logger.info(f"⚠️ Creating missing 'myratings' column in {library.name}")
            if not self.create_custom_column(library, 'myratings', 'My Ratings'):
                success = False
        else:
            self.logger.info(f"✅ 'myratings' column already exists in {library.name}")
        
        if not columns['my_genres']:
            self.logger.info(f"⚠️ Creating missing 'my_genres' column in {library.name}")
            if not self.create_custom_column(library, 'my_genres', 'My Genres'):
                success = False
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
            if genre_collections:
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
        """Filter collections to get only rating collections."""
        # Handle both prefixed and non-prefixed collection names from Kobo
        rating_patterns = [
            "| evergreen", "| absolute favorite", "| favorite", "| good",
            "evergreen", "absolute favorite", "favorites", "great", "favorite"
        ]
        matched_collections = []
        for col in collections:
            col_lower = col.lower().strip()
            if col_lower in [p.lower() for p in rating_patterns]:
                # Clean up the collection name for Calibre
                clean_name = col_lower.replace("| ", "").title()
                if clean_name == "Favorite":
                    clean_name = "Favorites"
                elif clean_name == "Good":
                    clean_name = "Great"
                matched_collections.append(clean_name)
        
        self.logger.debug(f"Rating collections found: {matched_collections} from {collections}")
        return matched_collections
    
    def _get_genre_collections(self, collections: List[str]) -> List[str]:
        """Filter collections to get only genre collections."""
        # Get rating collections to exclude them
        rating_collections = self._get_rating_collections(collections)
        rating_patterns_lower = [r.lower() for r in rating_collections]
        
        genre_collections = []
        for col in collections:
            col_clean = col.replace("| ", "").strip()
            if col_clean.lower() not in rating_patterns_lower and col_clean.lower() not in [
                "evergreen", "absolute favorite", "favorites", "great", "favorite", "good"
            ]:
                genre_collections.append(col_clean)
        
        self.logger.debug(f"Genre collections found: {genre_collections} from {collections}")
        return genre_collections
    
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
        
        # Group matches by library for efficient processing
        by_library = {}
        for match in matches:
            lib_name = match.library.name
            if lib_name not in by_library:
                by_library[lib_name] = []
            by_library[lib_name].append(match)
        
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
    
    def _verify_column_exists(self, library: CalibreLibrary, column_name: str) -> bool:
        """Verify that a custom column actually exists in the library."""
        try:
            conn = sqlite3.connect(library.metadata_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT label FROM custom_columns WHERE label = ?", (column_name,))
            result = cursor.fetchone()
            conn.close()
            
            exists = result is not None
            self.logger.debug(f"Column {column_name} exists in {library.name}: {exists}")
            return exists
            
        except sqlite3.Error as e:
            self.logger.error(f"Error verifying column {column_name} exists: {e}")
            return False
    
    def _verify_column_update(self, library: CalibreLibrary, book_id: int, column: str, expected_value: str) -> bool:
        """Verify that a custom column update actually worked by reading it back."""
        try:
            conn = sqlite3.connect(library.metadata_db_path)
            cursor = conn.cursor()
            
            # Find the custom column table name
            cursor.execute("SELECT id FROM custom_columns WHERE label = ?", (column,))
            column_result = cursor.fetchone()
            if not column_result:
                conn.close()
                self.logger.debug(f"Column {column} not found in custom_columns table")
                return False
            
            column_id = column_result[0]
            table_name = f"custom_column_{column_id}"
            
            # Get the current value
            cursor.execute(f"SELECT value FROM {table_name} WHERE book = ?", (book_id,))
            value_result = cursor.fetchone()
            conn.close()
            
            if value_result:
                current_value = value_result[0] or ""
                matches = current_value == expected_value
                self.logger.debug(f"Book {book_id} {column}: expected '{expected_value}', got '{current_value}', matches: {matches}")
                return matches
            else:
                self.logger.debug(f"No value found for book {book_id} in {column}")
                return False
                
        except sqlite3.Error as e:
            self.logger.debug(f"Error verifying column update (non-critical): {e}")
            return False  # Non-critical, don't fail the update
        except Exception as e:
            self.logger.debug(f"Error verifying column update (non-critical): {e}")
            return False
    
    def test_column_update(self, library: CalibreLibrary, test_book_id: int = 1) -> bool:
        """Test updating a custom column to verify the fix works."""
        try:
            self.logger.info(f"🧪 Testing column update capability for {library.name}")
            
            # Test with a simple rating value
            test_result = self._update_custom_column(library, test_book_id, 'myratings', ['Test'])
            
            if test_result:
                self.logger.info(f"✅ Column update test PASSED for {library.name}")
            else:
                self.logger.error(f"❌ Column update test FAILED for {library.name}")
            
            return test_result
            
        except Exception as e:
            self.logger.error(f"❌ Column update test ERROR for {library.name}: {e}")
            return False