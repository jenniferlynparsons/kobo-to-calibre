# Phase 1: Kobo Database Analysis

## Database Overview
- **File**: KoboReader.sqlite
- **Location**: Root of project directory
- **Total Tables**: 31 tables identified
- **Key Tables for Sync**: content, Shelf, ShelfContent, Event

## Table Analysis

### content Table
**Purpose**: Main book information and reading metadata
**Key Fields**:
- `ContentID` (Primary Key) - Unique identifier for each book
- `BookID` - Book identifier 
- `BookTitle` - Title of the book
- `Title` - Display title
- `Attribution` - Author information
- `ReadStatus` - Reading status (2 = finished/read)
- `___PercentRead` - Reading progress percentage
- `DateLastRead` - Last reading date
- `FavouritesIndex` - Favorites ranking (-1 = not favorited)
- `BookshelfTags` - Text field for shelf/tag associations

**Sample Data Found**:
- Books include mix of fanfiction and published works
- ReadStatus values observed: 2 (appears to be "read")
- ___PercentRead ranges from 0-100

### Shelf Table
**Purpose**: Collection/shelf definitions (user-created categories)
**Key Fields**:
- `Id` (Primary Key) - Unique shelf identifier
- `Name` - Display name of the shelf
- `Type` - Shelf type ("UserTag" for user-created collections)
- `InternalName` - Internal reference name
- `_IsDeleted` - Deletion flag (0 = active, 1 = deleted)
- `_IsVisible` - Visibility flag
- `LastModified` - Last modification timestamp

**Sample Collections Found**:
- "new jersey" (location-based tag)
- "mix" (content type)
- "sweet fluff" (genre/mood tag)
- "fix" (possibly fix-it fics)
- "kink" (content warning/genre)
- "> no band" (fandom categorization)
- "killjoys" (My Chemical Romance era/theme)
- "historic au" (historical alternate universe)
- "little" (age play/little space content)
- "sickfic" (hurt/comfort genre)

**Total Active Shelves**: 30 collections

### ShelfContent Table
**Purpose**: Many-to-many relationship between books and shelves
**Key Fields**:
- `ShelfName` - References Shelf.Name
- `ContentId` - References content.ContentID
- `DateModified` - When book was added to shelf
- `_IsDeleted` - Deletion flag

**Usage**: This table links books to their collections, allowing books to be in multiple categories.

### Event Table
**Purpose**: Reading events and progress tracking
**Key Fields**:
- `EventType` - Type of reading event
- `ContentID` - References content.ContentID
- `FirstOccurrence` - First time event occurred
- `LastOccurrence` - Most recent occurrence
- `EventCount` - Number of times event occurred

## Key Insights for Sync Project

### Collection Structure
- User has **30 active collections** covering various genres, moods, and content types
- Collections are **genre/content-based** rather than rating-based
- **No explicit rating collections found** (no "1-star", "2-star", etc.)
- Collections cover:
  - **Content types**: "mix", "killjoys", "> no band"
  - **Genres**: "sweet fluff", "sickfic", "historic au" 
  - **Content warnings**: "kink", "little"
  - **Technical**: "fix" (likely fix-it fics)
  - **Location**: "new jersey"

### Reading Status Tracking
- `ReadStatus` field in content table tracks completion
- `___PercentRead` provides granular progress
- `DateLastRead` tracks reading activity
- `FavouritesIndex` could be used for rating/favoriting system

### Book Matching Considerations
- `Title` and `Attribution` fields available for matching
- `BookID` and `ContentID` provide unique identifiers
- No ISBN field observed in sample data
- Title/Author combination will likely be primary matching method

## Questions for User Based on Analysis

1. **Rating System**: Since no star-rating collections were found, how do you currently rate books? Do you use:
   - Favorites system (`FavouritesIndex`)?
   - Specific collection names for ratings?
   - External system not in Kobo?

2. **Collection Priorities**: Which of these 30 collections are most important to sync to Calibre?
   - All collections?
   - Only specific content-type collections?
   - Genre-based collections only?

3. **Collection Handling**: How should books in multiple collections be handled in Calibre?
   - Combine as comma-separated tags?
   - Use only primary collection?
   - Create custom columns for different collection types?

## Technical Recommendations

### Book Matching Strategy
**Primary**: Title + Author matching (using `Title` and `Attribution` fields)
**Fallback**: Manual review for unmatched books

### Metadata Mapping
- **Collections → Calibre Tags**: Map Shelf.Name to Calibre tags
- **Reading Status**: Use `ReadStatus` to determine if book was completed
- **Reading Progress**: `___PercentRead` for completion tracking
- **Reading Date**: `DateLastRead` for "date read" metadata

### Sync Scope
Focus initial implementation on:
1. Collection membership (ShelfContent relationships)
2. Reading completion status
3. Basic metadata enhancement

Next phase can add:
- Reading progress percentages
- Reading date tracking
- Custom rating system (if desired)