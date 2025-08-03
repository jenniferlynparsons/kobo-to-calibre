"""
Create test Kobo database for development and testing
"""

import sqlite3
import os

def create_test_kobo_database():
    """Create a test KoboReader.sqlite with sample data."""
    
    # Remove existing empty database
    if os.path.exists('KoboReader.sqlite'):
        os.remove('KoboReader.sqlite')
    
    # Create new database
    conn = sqlite3.connect('KoboReader.sqlite')
    cursor = conn.cursor()
    
    # Create content table
    cursor.execute('''
        CREATE TABLE content(
            ContentID TEXT NOT NULL,
            ContentType TEXT NOT NULL,
            MimeType TEXT NOT NULL,
            BookID TEXT,
            BookTitle TEXT,
            ImageId TEXT,
            Title TEXT COLLATE NOCASE,
            Attribution TEXT COLLATE NOCASE,
            Description TEXT,
            DateCreated TEXT,
            ShortCoverKey TEXT,
            adobe_location TEXT,
            Publisher TEXT,
            IsEncrypted BOOL,
            DateLastRead TEXT,
            FirstTimeReading BOOL,
            ChapterIDBookmarked TEXT,
            ParagraphBookmarked INTEGER,
            BookmarkWordOffset INTEGER,
            NumShortcovers INTEGER,
            VolumeIndex INTEGER,
            ___NumPages INTEGER,
            ReadStatus INTEGER,
            ___SyncTime TEXT,
            ___UserID TEXT NOT NULL,
            PublicationId TEXT,
            ___FileOffset INTEGER,
            ___FileSize INTEGER,
            ___PercentRead INTEGER,
            ___ExpirationStatus INTEGER,
            FavouritesIndex NOT NULL DEFAULT -1,
            Accessibility INTEGER DEFAULT 1,
            ContentURL TEXT,
            Language TEXT,
            BookshelfTags TEXT,
            IsDownloaded BIT NOT NULL DEFAULT 1,
            PRIMARY KEY (ContentID)
        );
    ''')
    
    # Create Shelf table
    cursor.execute('''
        CREATE TABLE Shelf (
            CreationDate TEXT,
            Id TEXT,
            InternalName TEXT,
            LastModified TEXT,
            Name TEXT,
            Type TEXT,
            _IsDeleted BOOL,
            _IsVisible BOOL,
            _IsSynced BOOL,
            _SyncTime TEXT,
            LastAccessed TEXT,
            PRIMARY KEY(Id)
        );
    ''')
    
    # Create ShelfContent table
    cursor.execute('''
        CREATE TABLE ShelfContent (
            ShelfName TEXT,
            ContentId TEXT,
            DateModified TEXT,
            _IsDeleted BOOL,
            _IsSynced BOOL,
            PRIMARY KEY(ShelfName, ContentId)
        );
    ''')
    
    # Create Event table
    cursor.execute('''
        CREATE TABLE Event ( 
            EventType INTEGER NOT NULL,
            FirstOccurrence TEXT,
            LastOccurrence TEXT,
            EventCount INTEGER DEFAULT 0,
            ContentID TEXT,
            ExtraData BLOB,
            Checksum TEXT,
            PRIMARY KEY (EventType, ContentID)
        );
    ''')
    
    # Insert sample collections (rating and genre)
    collections = [
        ('evergreen-id', 'Evergreen', 'Evergreen', 'UserTag', False, True),
        ('absolute-favorite-id', 'Absolute Favorite', 'Absolute Favorite', 'UserTag', False, True),
        ('favorites-id', 'Favorites', 'Favorites', 'UserTag', False, True),
        ('great-id', 'Great', 'Great', 'UserTag', False, True),
        ('sweet-fluff-id', 'sweet fluff', 'sweet fluff', 'UserTag', False, True),
        ('killjoys-id', 'killjoys', 'killjoys', 'UserTag', False, True),
        ('historic-au-id', 'historic au', 'historic au', 'UserTag', False, True),
        ('sickfic-id', 'sickfic', 'sickfic', 'UserTag', False, True),
        ('kink-id', 'kink', 'kink', 'UserTag', False, True),
        ('little-id', 'little', 'little', 'UserTag', False, True),
    ]
    
    for shelf_id, name, internal_name, shelf_type, is_deleted, is_visible in collections:
        cursor.execute('''
            INSERT INTO Shelf (Id, Name, InternalName, Type, _IsDeleted, _IsVisible, CreationDate, LastModified)
            VALUES (?, ?, ?, ?, ?, ?, '2024-01-01T00:00:00.000', '2024-01-01T00:00:00.000')
        ''', (shelf_id, name, internal_name, shelf_type, is_deleted, is_visible))
    
    # Insert sample books
    books = [
        ('book1', '6', 'application/epub+zip', 'book1', 'You and I in Unison', 'You and I in Unison', '0P3NY0UR3Y3SANDL00KN0RTH', 2, 100, '2024-01-15T10:30:00.000'),
        ('book2', '6', 'application/epub+zip', 'book2', 'Family Camping Trip with a Twist', 'Family Camping Trip with a Twist', '0_gloustt', 2, 85, '2024-01-20T14:15:00.000'),
        ('book3', '6', 'application/epub+zip', 'book3', 'Bad thoughts', 'Bad thoughts', '3l15am', 1, 45, '2024-01-25T09:00:00.000'),
        ('book4', '6', 'application/epub+zip', 'book4', 'Handsy', 'Handsy', '4ngelgutzz', 2, 100, '2024-02-01T16:20:00.000'),
        ('book5', '6', 'application/epub+zip', 'book5', 'The Desert Here and the Desert Far Away', 'The Desert Here and the Desert Far Away', '7iris', 0, 0, None),
    ]
    
    for content_id, content_type, mime_type, book_id, title, book_title, author, read_status, percent_read, date_last_read in books:
        cursor.execute('''
            INSERT INTO content (
                ContentID, ContentType, MimeType, BookID, Title, BookTitle, Attribution,
                ReadStatus, ___PercentRead, DateLastRead, ___UserID
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'test-user')
        ''', (content_id, content_type, mime_type, book_id, title, book_title, author, read_status, percent_read, date_last_read))
    
    # Insert shelf content relationships
    shelf_contents = [
        # Book 1: Evergreen + sweet fluff + killjoys
        ('Evergreen', 'book1'),
        ('sweet fluff', 'book1'),
        ('killjoys', 'book1'),
        
        # Book 2: Absolute Favorite + historic au
        ('Absolute Favorite', 'book2'),
        ('historic au', 'book2'),
        
        # Book 3: Great + sickfic + kink (unfinished book)
        ('Great', 'book3'),
        ('sickfic', 'book3'),
        ('kink', 'book3'),
        
        # Book 4: Favorites + little + killjoys
        ('Favorites', 'book4'),
        ('little', 'book4'),
        ('killjoys', 'book4'),
        
        # Book 5: sweet fluff only (unread)
        ('sweet fluff', 'book5'),
    ]
    
    for shelf_name, content_id in shelf_contents:
        cursor.execute('''
            INSERT INTO ShelfContent (ShelfName, ContentId, DateModified, _IsDeleted, _IsSynced)
            VALUES (?, ?, '2024-01-01T00:00:00.000', 0, 1)
        ''', (shelf_name, content_id))
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("Test KoboReader.sqlite database created successfully!")
    print("Collections created:")
    for _, name, _, _, _, _ in collections:
        print(f"  - {name}")
    print(f"Books created: {len(books)}")
    print(f"Shelf relationships created: {len(shelf_contents)}")

if __name__ == '__main__':
    create_test_kobo_database()