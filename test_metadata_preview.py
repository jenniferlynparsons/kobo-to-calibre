"""
Preview what metadata would be updated
"""

import sys
sys.path.append('./src')

from config_manager import ConfigManager
from sync_engine import SyncEngine

def preview_metadata_updates():
    print('=== Preview of Metadata Updates ===')
    config_manager = ConfigManager()
    sync_engine = SyncEngine(config_manager)
    
    # Get all the components
    sync_engine.discover_libraries()
    sync_engine.load_kobo_data()
    matches, unmatched = sync_engine.match_books()
    
    print(f'Found {len(matches)} books to update\n')
    
    # Show sample of what would be updated
    sample_matches = matches[:10]  # First 10 matches
    
    for i, match in enumerate(sample_matches, 1):
        book = match.kobo_book
        rating_cols = [col for col in book.collections if col in sync_engine.kobo_reader.rating_collections]
        genre_cols = [col for col in book.collections if col not in sync_engine.kobo_reader.rating_collections]
        
        print(f'{i}. "{book.title}" by {book.author}')
        print(f'   Library: {match.library.name}')
        print(f'   Calibre Book ID: {match.calibre_book_id}')
        
        if rating_cols:
            # Convert to display values
            rating_display = [sync_engine.kobo_reader.rating_collections[col] for col in rating_cols]
            print(f'   My Ratings → {", ".join(rating_display)}')
        else:
            print(f'   My Ratings → (no rating collections)')
            
        if genre_cols:
            print(f'   My Genres → {", ".join(genre_cols)}')
        else:
            print(f'   My Genres → (no genre collections)')
            
        print(f'   Read Status: {book.read_status}, Progress: {book.percent_read}%')
        print()

if __name__ == '__main__':
    preview_metadata_updates()