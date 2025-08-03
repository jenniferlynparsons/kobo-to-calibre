"""
Library Manager - Discover and manage multiple Calibre libraries
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class CalibreLibrary:
    """Represents a Calibre library."""
    name: str
    path: Path
    metadata_db_path: Path
    is_primary: bool = False  # MCR library will be primary


class LibraryManager:
    """Manages discovery and access to multiple Calibre libraries."""
    
    def __init__(self):
        """Initialize library manager."""
        self.logger = logging.getLogger(__name__)
        self.libraries: List[CalibreLibrary] = []
        self.primary_library: Optional[CalibreLibrary] = None
    
    def discover_libraries(self, search_paths: List[str] = None) -> List[CalibreLibrary]:
        """
        Discover Calibre libraries by searching for metadata.db files.
        
        Args:
            search_paths: List of paths to search. If None, searches common locations.
        """
        if search_paths is None:
            # Default search paths for macOS
            search_paths = [
                str(Path.home() / "Documents"),
                str(Path.home() / "Downloads"), 
                str(Path.cwd()),  # Current directory
                "/Users/jenniferparsons/Engineering/Projects/kobo-to-calibre"  # Project samples
            ]
        
        libraries = []
        seen_paths = set()  # Track paths to avoid duplicates
        
        for search_path in search_paths:
            path = Path(search_path)
            if not path.exists():
                continue
            
            # Search for metadata.db files
            for metadata_file in path.rglob("metadata.db"):
                library_path = metadata_file.parent.resolve()  # Resolve to absolute path
                library_name = library_path.name
                
                # Skip if this is a backup or temporary file
                if any(skip in str(library_path).lower() for skip in ['backup', 'temp', '.git']):
                    continue
                
                # Skip if we've already found this library path
                if library_path in seen_paths:
                    continue
                
                # Verify it's a valid Calibre library
                if self._is_valid_calibre_library(library_path):
                    library = CalibreLibrary(
                        name=library_name,
                        path=library_path,
                        metadata_db_path=metadata_file
                    )
                    libraries.append(library)
                    seen_paths.add(library_path)
                    self.logger.info(f"Found Calibre library: {library_name} at {library_path}")
        
        # Set MCR library as primary if found
        for library in libraries:
            if "mcr" in library.name.lower():
                library.is_primary = True
                self.primary_library = library
                self.logger.info(f"Set {library.name} as primary library")
                break
        
        self.libraries = libraries
        return libraries
    
    def _is_valid_calibre_library(self, library_path: Path) -> bool:
        """Check if a directory contains a valid Calibre library."""
        metadata_db = library_path / "metadata.db"
        
        if not metadata_db.exists():
            return False
        
        try:
            # Try to connect and check for expected tables
            conn = sqlite3.connect(metadata_db)
            cursor = conn.cursor()
            
            # Check for key Calibre tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('books', 'authors', 'custom_columns')
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Should have at least books table
            return 'books' in tables
            
        except sqlite3.Error:
            return False
    
    def get_library_by_name(self, name: str) -> Optional[CalibreLibrary]:
        """Get library by name."""
        for library in self.libraries:
            if library.name.lower() == name.lower():
                return library
        return None
    
    def get_primary_library(self) -> Optional[CalibreLibrary]:
        """Get the primary library (MCR library)."""
        return self.primary_library
    
    def get_secondary_libraries(self) -> List[CalibreLibrary]:
        """Get all non-primary libraries."""
        return [lib for lib in self.libraries if not lib.is_primary]
    
    def get_all_libraries(self) -> List[CalibreLibrary]:
        """Get all discovered libraries."""
        return self.libraries
    
    def add_library(self, name: str, path: str) -> bool:
        """Manually add a library path."""
        library_path = Path(path)
        metadata_db = library_path / "metadata.db"
        
        if not self._is_valid_calibre_library(library_path):
            self.logger.error(f"Invalid Calibre library at {path}")
            return False
        
        library = CalibreLibrary(
            name=name,
            path=library_path,
            metadata_db_path=metadata_db
        )
        
        self.libraries.append(library)
        self.logger.info(f"Added library: {name} at {path}")
        return True
    
    def get_library_info(self, library: CalibreLibrary) -> Dict:
        """Get basic information about a library."""
        try:
            conn = sqlite3.connect(library.metadata_db_path)
            cursor = conn.cursor()
            
            # Get book count
            cursor.execute("SELECT COUNT(*) FROM books")
            book_count = cursor.fetchone()[0]
            
            # Get custom columns
            cursor.execute("SELECT label, name FROM custom_columns")
            custom_columns = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'book_count': book_count,
                'custom_columns': custom_columns,
                'has_my_ratings': 'myratings' in custom_columns or '#my_ratings' in custom_columns,
                'has_my_genres': 'my_genres' in custom_columns or '#my_genres' in custom_columns
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error reading library info: {e}")
            return {}