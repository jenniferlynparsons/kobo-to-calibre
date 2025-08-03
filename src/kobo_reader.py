"""
Kobo Reader - Extract collections and reading data from KoboReader.sqlite
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


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


@dataclass
class KoboCollection:
    """Represents a collection/shelf from the Kobo database."""
    name: str
    internal_name: str
    collection_type: str
    is_rating: bool


class KoboReader:
    """Reads and extracts data from KoboReader.sqlite database."""
    
    def __init__(self, kobo_db_path: str = "KoboReader.sqlite"):
        """Initialize with path to Kobo database."""
        self.db_path = Path(kobo_db_path)
        self.logger = logging.getLogger(__name__)
        
        # Rating collections mapping based on actual database content
        self.rating_collections = {
            "| evergreen": "Evergreen",
            "| absolute favorite": "Absolute Favorite", 
            "| favorite": "Favorites",
            "| good": "Great"
        }
    
    def connect(self) -> sqlite3.Connection:
        """Create connection to Kobo database."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Kobo database not found: {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def get_collections(self) -> List[KoboCollection]:
        """Extract all active collections from Kobo database."""
        collections = []
        
        with self.connect() as conn:
            cursor = conn.execute("""
                SELECT Name, InternalName, Type
                FROM Shelf 
                WHERE _IsDeleted = 'false' AND _IsVisible = 'true'
                ORDER BY Name
            """)
            
            for row in cursor:
                name = row['Name']
                is_rating = name in self.rating_collections
                
                collection = KoboCollection(
                    name=name,
                    internal_name=row['InternalName'],
                    collection_type=row['Type'],
                    is_rating=is_rating
                )
                collections.append(collection)
        
        self.logger.info(f"Found {len(collections)} collections")
        return collections
    
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
            
            # Group collections by book
            book_collections = {}
            for row in cursor:
                content_id = row['ContentId']
                shelf_name = row['ShelfName']
                
                if content_id not in book_collections:
                    book_collections[content_id] = []
                book_collections[content_id].append(shelf_name)
            
            # Create KoboBook objects
            for content_id, book_info in book_data.items():
                raw_collections = book_collections.get(content_id, [])
                # Convert rating collections to display names
                converted_collections = self._convert_collections(raw_collections)
                
                book = KoboBook(
                    content_id=content_id,
                    title=book_info['Title'] or "",
                    author=book_info['Attribution'] or "",
                    read_status=book_info['ReadStatus'] or 0,
                    percent_read=book_info['___PercentRead'] or 0,
                    date_last_read=book_info['DateLastRead'],
                    collections=converted_collections
                )
                books.append(book)
        
        self.logger.info(f"Found {len(books)} books")
        return books
    
    def _convert_collections(self, raw_collections: List[str]) -> List[str]:
        """Convert collections from database format to display format."""
        converted = []
        for collection in raw_collections:
            # Convert rating collections to display names
            if collection in self.rating_collections:
                converted.append(self.rating_collections[collection])
            else:
                # Keep non-rating collections as-is
                converted.append(collection)
        return converted
    
    def get_rating_collections(self) -> List[str]:
        """Get list of collections that represent ratings."""
        return list(self.rating_collections.keys())
    
    def get_genre_collections(self) -> List[str]:
        """Get list of collections that represent genres/categories."""
        all_collections = self.get_collections()
        return [c.name for c in all_collections if not c.is_rating]