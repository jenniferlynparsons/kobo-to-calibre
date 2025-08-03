"""
Book Matcher - Cross-library book matching logic
"""

import sqlite3
import logging
import re
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from kobo_reader import KoboBook
from library_manager import CalibreLibrary


@dataclass
class BookMatch:
    """Represents a potential match between Kobo and Calibre book."""
    kobo_book: KoboBook
    calibre_book_id: int
    calibre_title: str
    calibre_authors: str
    library: CalibreLibrary
    match_confidence: float
    match_type: str  # 'exact', 'normalized', 'fuzzy'


@dataclass
class BookConflict:
    """Represents a book found in multiple libraries."""
    kobo_book: KoboBook
    matches: List[BookMatch]
    resolution: Optional[str] = None  # 'primary', 'all', 'skip', 'specific_library'
    chosen_library: Optional[str] = None


class BookMatcher:
    """Handles matching books between Kobo and Calibre libraries."""
    
    def __init__(self, library_manager):
        """Initialize with library manager."""
        self.library_manager = library_manager
        self.logger = logging.getLogger(__name__)
        self.unmatched_books = []
        self.conflicts = []
    
    def normalize_title(self, title: str) -> str:
        """Normalize title for matching."""
        if not title:
            return ""
        
        # Convert to lowercase
        normalized = title.lower()
        
        # Remove common punctuation and extra spaces
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common articles at the beginning
        articles = ['the ', 'a ', 'an ']
        for article in articles:
            if normalized.startswith(article):
                normalized = normalized[len(article):]
                break
        
        return normalized.strip()
    
    def normalize_author(self, author: str) -> str:
        """Normalize author name for matching."""
        if not author:
            return ""
        
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', author.lower().strip())
        
        # Handle "Last, First" vs "First Last" format
        if ',' in normalized:
            parts = [part.strip() for part in normalized.split(',')]
            if len(parts) == 2:
                # Convert "Last, First" to "First Last"
                normalized = f"{parts[1]} {parts[0]}"
        
        return normalized
    
    def find_book_in_library(self, kobo_book: KoboBook, library: CalibreLibrary) -> Optional[BookMatch]:
        """Find a book in a specific Calibre library."""
        try:
            conn = sqlite3.connect(library.metadata_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all books with authors
            cursor.execute("""
                SELECT 
                    b.id,
                    b.title,
                    GROUP_CONCAT(a.name, ' & ') as authors
                FROM books b
                LEFT JOIN books_authors_link ba ON b.id = ba.book
                LEFT JOIN authors a ON ba.author = a.id
                GROUP BY b.id, b.title
            """)
            
            calibre_books = cursor.fetchall()
            conn.close()
            
            # Try exact match first
            kobo_title_norm = self.normalize_title(kobo_book.title)
            kobo_author_norm = self.normalize_author(kobo_book.author)
            
            for book in calibre_books:
                calibre_title_norm = self.normalize_title(book['title'])
                calibre_author_norm = self.normalize_author(book['authors'] or "")
                
                # Exact normalized match
                if (kobo_title_norm == calibre_title_norm and 
                    kobo_author_norm == calibre_author_norm):
                    
                    return BookMatch(
                        kobo_book=kobo_book,
                        calibre_book_id=book['id'],
                        calibre_title=book['title'],
                        calibre_authors=book['authors'] or "",
                        library=library,
                        match_confidence=1.0,
                        match_type='exact'
                    )
            
            # If no exact match found, return None (strict matching only)
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Error searching library {library.name}: {e}")
            return None
    
    def find_book_across_libraries(self, kobo_book: KoboBook) -> List[BookMatch]:
        """Find a book across all libraries, prioritizing primary library."""
        matches = []
        
        # Search primary library (MCR) first
        primary_library = self.library_manager.get_primary_library()
        if primary_library:
            match = self.find_book_in_library(kobo_book, primary_library)
            if match:
                matches.append(match)
                # For strict matching, return immediately if found in primary
                return matches
        
        # Search secondary libraries
        for library in self.library_manager.get_secondary_libraries():
            match = self.find_book_in_library(kobo_book, library)
            if match:
                matches.append(match)
        
        return matches
    
    def match_all_books(self, kobo_books: List[KoboBook]) -> Tuple[List[BookMatch], List[KoboBook], List[BookConflict]]:
        """
        Match all Kobo books against Calibre libraries.
        
        Returns:
            Tuple of (successful_matches, unmatched_books, conflicts)
        """
        successful_matches = []
        unmatched_books = []
        conflicts = []
        
        self.logger.info(f"Starting to match {len(kobo_books)} books")
        
        for i, kobo_book in enumerate(kobo_books):
            if i % 10 == 0:
                self.logger.info(f"Processing book {i+1}/{len(kobo_books)}: {kobo_book.title}")
            
            matches = self.find_book_across_libraries(kobo_book)
            
            if matches:
                if len(matches) == 1:
                    # Single match - add to successful matches
                    successful_matches.append(matches[0])
                else:
                    # Multiple matches - this is a conflict
                    conflict = BookConflict(
                        kobo_book=kobo_book,
                        matches=matches
                    )
                    conflicts.append(conflict)
                    
                    self.logger.warning(
                        f"CONFLICT: '{kobo_book.title}' by {kobo_book.author} found in {len(matches)} libraries: "
                        f"{[match.library.name for match in matches]}"
                    )
            else:
                unmatched_books.append(kobo_book)
                self.logger.debug(f"No match found for '{kobo_book.title}' by {kobo_book.author}")
        
        self.logger.info(f"Matching complete: {len(successful_matches)} matched, {len(unmatched_books)} unmatched, {len(conflicts)} conflicts")
        
        self.unmatched_books = unmatched_books
        self.conflicts = conflicts
        return successful_matches, unmatched_books, conflicts
    
    def get_unmatched_books(self) -> List[KoboBook]:
        """Get list of books that couldn't be matched."""
        return self.unmatched_books
    
    def get_conflicts(self) -> List[BookConflict]:
        """Get list of books with conflicts (found in multiple libraries)."""
        return self.conflicts
    
    def generate_skip_report(self) -> Dict[str, str]:
        """Generate a report of unmatched books for user review and save to file."""
        # Filter to only books with collections (these are the ones that should have matched)
        books_with_collections = [book for book in self.unmatched_books if book.collections]
        
        if not books_with_collections:
            return {
                "summary": "All books with collections were successfully matched!",
                "file_path": None
            }
        
        # Create detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = f"Books with Collections - No Match Found\n"
        report += f"======================================\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Books with collections but no match: {len(books_with_collections)}\n"
        report += f"Total unmatched books: {len(self.unmatched_books)}\n"
        report += f"Books without collections (expected): {len(self.unmatched_books) - len(books_with_collections)}\n\n"
        
        report += f"These books have collections in Kobo but could not be matched to any Calibre library.\n"
        report += f"This usually indicates title/author differences or missing books in Calibre.\n\n"
        
        # Add detailed book list
        report += f"Detailed Analysis:\n"
        report += f"{'='*60}\n\n"
        
        for i, book in enumerate(books_with_collections, 1):
            report += f"{i:3d}. Title: {book.title}\n"
            report += f"     Author: {book.author}\n"
            report += f"     Collections: {', '.join(book.collections) if book.collections else 'None'}\n"
            report += f"     Read Status: {book.read_status} (0=unread, 1=reading, 2=finished)\n"
            report += f"     Progress: {book.percent_read}%\n"
            if book.date_last_read:
                report += f"     Last Read: {book.date_last_read}\n"
            report += f"     Possible reasons for no match:\n"
            report += f"       - Title or author name differs between Kobo and Calibre\n"
            report += f"       - Book may not exist in any Calibre library\n"
            report += f"       - Author name format differences (e.g., 'Last, First' vs 'First Last')\n"
            report += "-" * 70 + "\n\n"
        
        # Save to file
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        file_path = logs_dir / f"unmatched_books_{timestamp}.txt"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"Unmatched books report saved to: {file_path}")
            
            # Return summary for display + file path
            no_collections = len(self.unmatched_books) - len(books_with_collections)
            
            summary = f"Found {len(books_with_collections)} books with collections that need investigation.\n"
            summary += f"({no_collections} books without collections were excluded as expected.)\n"
            summary += f"Detailed report saved to: {file_path}\n\n"
            summary += f"These books have collections in Kobo but couldn't be matched:\n"
            
            for book in books_with_collections[:5]:
                collections_preview = ', '.join(book.collections[:3])
                if len(book.collections) > 3:
                    collections_preview += f" (+{len(book.collections)-3} more)"
                summary += f"  • '{book.title}' by {book.author} [{collections_preview}]\n"
            
            if len(books_with_collections) > 5:
                summary += f"  ... and {len(books_with_collections) - 5} more (see file for complete list)\n"
            
            return {
                "summary": summary,
                "file_path": str(file_path)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to save unmatched books report: {e}")
            return {
                "summary": f"Failed to save detailed report. {len(self.unmatched_books)} books unmatched.",
                "file_path": None
            }