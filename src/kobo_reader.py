"""
Kobo Reader - Extract collections and reading data from KoboReader.sqlite
"""

import sqlite3
import logging
from pathlib import Path
from collections import defaultdict
from typing import List, Optional
from dataclasses import dataclass

# Only stat()-ed to check the Desktop copy's age; never opened
DEVICE_DB = Path("/Volumes/KOBOeReader/.kobo/KoboReader.sqlite")

# Kobo rating shelf name -> Calibre #myratings value
RATINGS = {
    "| evergreen": "Evergreen",
    "| absolute favorite": "Absolute Favorite",
    "| favorite": "Favorites",
    "| good": "Great",
}


@dataclass
class KoboBook:
    """Represents a book from the Kobo database."""
    content_id: str
    title: str
    author: str
    read_status: int
    percent_read: int
    date_last_read: Optional[str]
    collections: List[str]


class KoboReader:
    """Reads and extracts data from KoboReader.sqlite database."""
    
    def __init__(self, kobo_db_path: str = "KoboReader.sqlite"):
        """Initialize with path to Kobo database."""
        self.db_path = Path(kobo_db_path)
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> sqlite3.Connection:
        """Create connection to Kobo database."""
        # Never read the mounted device DB; always work from a Desktop copy
        if self.db_path.resolve().parts[1:2] == ('Volumes',):
            raise ValueError(f"Refusing mounted Kobo DB {self.db_path}; copy it to ~/Desktop first")
        if not self.db_path.exists():
            raise FileNotFoundError(f"Kobo database not found: {self.db_path}")
        # A stale copy would overwrite newer calibre ratings with old ones
        if not DEVICE_DB.exists():
            self.logger.warning("Kobo not mounted, cannot check if the Desktop copy is current")
        elif DEVICE_DB.stat().st_mtime > self.db_path.stat().st_mtime + 2:  # FAT32 mtime is 2s
            raise ValueError(f"{self.db_path} is older than the Kobo DB; copy it to ~/Desktop again")

        conn = sqlite3.connect(f"{self.db_path.resolve().as_uri()}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def get_books_with_collections(self) -> List[KoboBook]:
        """Extract all books with their collection memberships."""
        books = []
        
        with self.connect() as conn:
            # Get all books with basic info
            cursor = conn.execute("""
                SELECT 
                    ContentID, 
                    Title, 
                    Attribution, 
                    ReadStatus, 
                    ___PercentRead,
                    DateLastRead
                FROM content 
                WHERE ContentType = 6  -- Books only
                ORDER BY Title
            """)
            
            book_data = {row['ContentID']: row for row in cursor}
            
            # Get collection memberships
            cursor = conn.execute("""
                SELECT sc.ContentId, s.Name as ShelfName
                FROM ShelfContent sc
                JOIN Shelf s ON sc.ShelfName = s.Name
                WHERE sc._IsDeleted = 'false' AND s._IsDeleted = 'false'
                ORDER BY sc.ContentId, s.Name
            """)
            
            # Group collections by book, rating shelves renamed to their display names
            book_collections = defaultdict(list)
            for row in cursor:
                book_collections[row['ContentId']].append(RATINGS.get(row['ShelfName'], row['ShelfName']))
            
            # Create KoboBook objects
            for content_id, book_info in book_data.items():
                book = KoboBook(
                    content_id=content_id,
                    title=book_info['Title'] or "",
                    author=book_info['Attribution'] or "",
                    read_status=book_info['ReadStatus'] or 0,
                    percent_read=book_info['___PercentRead'] or 0,
                    date_last_read=book_info['DateLastRead'],
                    collections=book_collections[content_id]
                )
                books.append(book)
        
        self.logger.info(f"Found {len(books)} books")
        return books
