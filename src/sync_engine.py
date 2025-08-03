"""
Sync Engine - Main orchestration for multi-library sync operations
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

from config_manager import ConfigManager
from kobo_reader import KoboReader, KoboBook
from library_manager import LibraryManager, CalibreLibrary
from book_matcher import BookMatcher, BookMatch
from calibre_updater import CalibreUpdater


class SyncEngine:
    """Main orchestration engine for Kobo-to-Calibre sync."""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize sync engine with configuration."""
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.kobo_reader = None
        self.library_manager = LibraryManager()
        self.book_matcher = None
        self.calibre_updater = CalibreUpdater()
        
        # Data storage
        self.kobo_books: List[KoboBook] = []
        self.libraries: List[CalibreLibrary] = []
        self.matches: List[BookMatch] = []
        self.unmatched_books: List[KoboBook] = []
        self.conflicts: List = []
    
    def discover_libraries(self) -> List[CalibreLibrary]:
        """Discover Calibre libraries using configured search paths."""
        self.logger.info("Starting library discovery")
        
        search_paths = self.config_manager.get_search_paths()
        self.libraries = self.library_manager.discover_libraries(search_paths)
        
        if not self.libraries:
            raise Exception("No Calibre libraries found in search paths")
        
        # Update configuration with discovered libraries
        library_info = {}
        for lib in self.libraries:
            info = self.library_manager.get_library_info(lib)
            library_info[lib.name] = {
                'path': str(lib.path),
                'is_primary': lib.is_primary,
                'book_count': info.get('book_count', 0),
                'custom_columns': info.get('custom_columns', {})
            }
        
        self.config_manager.update_discovered_libraries(library_info)
        
        # Set primary library in config
        primary_lib = self.library_manager.get_primary_library()
        if primary_lib:
            self.config_manager.set_primary_library(primary_lib.name)
        
        self.logger.info(f"Discovered {len(self.libraries)} libraries")
        return self.libraries
    
    def load_kobo_data(self) -> List[KoboBook]:
        """Load books and collections from Kobo database."""
        self.logger.info("Loading Kobo data")
        
        kobo_db_path = self.config_manager.get_kobo_database_path()
        self.kobo_reader = KoboReader(kobo_db_path)
        
        # Get all books with collections
        self.kobo_books = self.kobo_reader.get_books_with_collections()
        
        if not self.kobo_books:
            raise Exception("No books found in Kobo database")
        
        self.logger.info(f"Loaded {len(self.kobo_books)} books from Kobo")
        
        # Log collection statistics
        all_collections = set()
        rating_collections = set()
        for book in self.kobo_books:
            all_collections.update(book.collections)
            rating_collections.update(
                col for col in book.collections 
                if col in self.kobo_reader.rating_collections
            )
        
        self.logger.info(f"Found {len(all_collections)} unique collections")
        self.logger.info(f"Rating collections: {rating_collections}")
        
        return self.kobo_books
    
    def match_books(self) -> tuple[List[BookMatch], List[KoboBook], List]:
        """Match Kobo books with Calibre libraries."""
        self.logger.info("Starting book matching")
        
        if not self.kobo_books:
            raise Exception("No Kobo books loaded. Call load_kobo_data() first.")
        
        if not self.libraries:
            raise Exception("No libraries discovered. Call discover_libraries() first.")
        
        self.book_matcher = BookMatcher(self.library_manager)
        self.matches, self.unmatched_books, self.conflicts = self.book_matcher.match_all_books(self.kobo_books)
        
        # Log matching statistics
        match_stats = {}
        for match in self.matches:
            lib_name = match.library.name
            match_stats[lib_name] = match_stats.get(lib_name, 0) + 1
        
        self.logger.info(f"Matching complete:")
        self.logger.info(f"  Matched: {len(self.matches)} books")
        self.logger.info(f"  Unmatched: {len(self.unmatched_books)} books")
        self.logger.info(f"  Conflicts: {len(self.conflicts)} books")
        for lib_name, count in match_stats.items():
            self.logger.info(f"  {lib_name}: {count} matches")
        
        return self.matches, self.unmatched_books, self.conflicts
    
    def update_calibre_metadata(self, dry_run: bool = True) -> Dict:
        """Update Calibre metadata for matched books."""
        if dry_run:
            self.logger.info("="*60)
            self.logger.info("RUNNING IN DRY RUN MODE")
            self.logger.info("No files will be modified")
            self.logger.info("No calibredb commands will be executed")
            self.logger.info("This is a preview only")
            self.logger.info("="*60)
            return self._simulate_updates()
        
        self.logger.info("Starting Calibre metadata updates")
        
        if not self.matches:
            raise Exception("No book matches found. Call match_books() first.")
        
        # Perform actual updates
        stats = self.calibre_updater.bulk_update(self.matches)
        
        self.logger.info(f"Metadata update complete:")
        self.logger.info(f"  Total books: {stats['total']}")
        self.logger.info(f"  Successful: {stats['successful']}")
        self.logger.info(f"  Failed: {stats['failed']}")
        self.logger.info(f"  Libraries updated: {list(stats['libraries_updated'])}")
        
        return stats
    
    def _simulate_updates(self) -> Dict:
        """Simulate updates for dry run mode."""
        stats = {
            'total': len(self.matches),
            'successful': len(self.matches),  # Assume all would succeed
            'failed': 0,
            'libraries_updated': set(),
            'dry_run': True
        }
        
        # Group by library to show what would be updated
        by_library = {}
        for match in self.matches:
            lib_name = match.library.name
            if lib_name not in by_library:
                by_library[lib_name] = []
            by_library[lib_name].append(match)
            stats['libraries_updated'].add(lib_name)
        
        # Log what would be updated
        for lib_name, lib_matches in by_library.items():
            self.logger.info(f"Would update {len(lib_matches)} books in {lib_name}:")
            for match in lib_matches[:5]:  # Show first 5 examples
                rating_cols = [col for col in match.kobo_book.collections 
                              if col in self.kobo_reader.rating_collections]
                genre_cols = [col for col in match.kobo_book.collections 
                             if col not in self.kobo_reader.rating_collections]
                
                self.logger.info(f"  '{match.kobo_book.title}' by {match.kobo_book.author}")
                if rating_cols:
                    self.logger.info(f"    My Ratings: {', '.join(rating_cols)}")
                if genre_cols:
                    self.logger.info(f"    My Genres: {', '.join(genre_cols)}")
            
            if len(lib_matches) > 5:
                self.logger.info(f"  ... and {len(lib_matches) - 5} more books")
        
        return stats
    
    def generate_reports(self) -> Dict[str, str]:
        """Generate reports for unmatched books and sync summary."""
        reports = {}
        
        # Unmatched books report
        if self.book_matcher:
            unmatched_report = self.book_matcher.generate_skip_report()
            reports['unmatched'] = unmatched_report['summary']
            reports['unmatched_file'] = unmatched_report['file_path']
        
        # Summary report
        summary = f"Kobo-to-Calibre Sync Summary\n"
        summary += f"============================\n\n"
        summary += f"Libraries discovered: {len(self.libraries)}\n"
        summary += f"Kobo books processed: {len(self.kobo_books)}\n"
        summary += f"Books matched: {len(self.matches)}\n"
        summary += f"Books unmatched: {len(self.unmatched_books)}\n\n"
        
        if self.libraries:
            summary += "Libraries:\n"
            for lib in self.libraries:
                primary = " (PRIMARY)" if lib.is_primary else ""
                summary += f"  • {lib.name}{primary}: {lib.path}\n"
        
        reports['summary'] = summary
        
        return reports
    
    def apply_conflict_resolutions(self, resolved_matches: List[BookMatch]) -> None:
        """Apply resolved matches from conflict resolution."""
        if resolved_matches:
            self.matches.extend(resolved_matches)
            self.logger.info(f"Applied {len(resolved_matches)} resolved matches from conflicts")
    
    def run_sync(self, dry_run: bool = True) -> Dict:
        """Run complete sync process."""
        self.logger.info(f"Starting full sync process (dry_run={dry_run})")
        
        try:
            # Step 1: Ensure libraries are discovered
            if not self.libraries:
                self.discover_libraries()
            
            # Step 2: Load Kobo data
            self.load_kobo_data()
            
            # Step 3: Match books
            self.match_books()
            
            # Step 4: Handle conflicts
            if self.conflicts:
                self.logger.info(f"Found {len(self.conflicts)} conflicts that need resolution")
                # Conflicts will be returned in results for GUI to handle
            
            # Step 5: Update metadata
            update_stats = self.update_calibre_metadata(dry_run=dry_run)
            
            # Step 6: Generate reports
            reports = self.generate_reports()
            
            # Combine results
            results = {
                **update_stats,
                'kobo_books_total': len(self.kobo_books),
                'libraries_found': len(self.libraries),
                'unmatched_count': len(self.unmatched_books),
                'conflicts_count': len(self.conflicts),
                'reports': reports
            }
            
            self.logger.info("Sync process completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Sync process failed: {e}")
            raise