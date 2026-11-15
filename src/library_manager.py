"""
Library Manager - Discover and manage multiple Calibre libraries
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Optional
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

    def discover_libraries(self, search_paths: List[str]) -> List[CalibreLibrary]:
        """Discover Calibre libraries by searching for metadata.db files."""
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
                if self._is_valid_calibre_library(metadata_file):
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

    def _is_valid_calibre_library(self, metadata_db: Path) -> bool:
        """Check that metadata.db has a Calibre 'books' table."""
        try:
            conn = sqlite3.connect(metadata_db)
            found = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='books'"
            ).fetchone()
            conn.close()
            return found is not None
        except sqlite3.Error:
            return False

    def get_primary_library(self) -> Optional[CalibreLibrary]:
        """Get the primary library (MCR library)."""
        return self.primary_library

    def get_secondary_libraries(self) -> List[CalibreLibrary]:
        """Get all non-primary libraries."""
        return [lib for lib in self.libraries if not lib.is_primary]
