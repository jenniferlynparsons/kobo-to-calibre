# Phase 1: Technical Findings and Assessment

## Environment Analysis

### Current Setup Assessment
- **Platform**: macOS (Darwin 24.5.0)
- **Kobo Database**: KoboReader.sqlite present and accessible
- **Calibre Libraries**: Two sample libraries identified
  - MCR library sample: ~250+ fanfiction books, organized by author
  - Misc library sample: ~200+ mixed content (fanfiction and published works)

### Database Accessibility
✅ **Kobo Database**: Successfully accessed via sqlite3
✅ **Calibre Libraries**: Standard Calibre structure with metadata.db files
✅ **File Permissions**: No access restrictions encountered

## Kobo Database Technical Details

### Database Structure
- **SQLite Version**: Compatible with standard sqlite3 tools
- **Size**: Manageable for programmatic access
- **Performance**: Fast queries on indexed fields (ContentID, BookID, ShelfName)
- **Indexes**: Well-indexed for collection and content lookups

### Key Relationships Identified
```
content (books) ←→ ShelfContent ←→ Shelf (collections)
        ↓
      Event (reading events)
```

### Data Quality Assessment
**High Quality Fields**:
- `content.Title` - Consistently populated, clean data
- `content.Attribution` - Author information well-formatted
- `Shelf.Name` - User-friendly collection names
- `content.ReadStatus` - Reliable completion tracking

**Potential Challenges**:
- No standardized rating system in collections
- Some collection names may need normalization for Calibre tags
- Date fields use text format, need parsing for date operations

## Calibre Integration Options

### Option 1: Command Line Interface (calibredb)
**Pros**:
- Official Calibre tool, guaranteed compatibility
- Safe, validated operations
- No direct database manipulation

**Cons**:
- Limited batch operation efficiency
- Requires parsing command output
- Slower for large collections

**Implementation**: Shell commands via subprocess

### Option 2: Direct Database Access
**Pros**:
- Fast bulk operations
- Direct SQL control
- Efficient for large libraries

**Cons**:
- Risk of database corruption
- Must understand Calibre schema deeply
- Bypasses Calibre's validation

**Implementation**: SQLite connections to metadata.db

### Option 3: Calibre Python API
**Pros**:
- Uses Calibre's internal methods
- Safe metadata operations
- Access to all Calibre functionality

**Cons**:
- Requires Calibre installation as dependency
- More complex setup
- Version compatibility concerns

**Implementation**: Import calibre modules directly

### **Recommended Approach**: Hybrid Strategy
1. **Phase 2 (MVP)**: Command line interface for safety
2. **Phase 3**: Direct database access for performance
3. **Phase 5**: Full API integration for plugin

## Book Matching Analysis

### Available Matching Fields
**Primary Fields**:
- `content.Title` vs Calibre title
- `content.Attribution` vs Calibre authors

**Secondary Fields**:
- `content.BookID` (Kobo-specific)
- File path analysis (if needed)

### Matching Challenges Identified
1. **Title Variations**: Subtitle handling, punctuation differences
2. **Author Format**: "LastName, FirstName" vs "FirstName LastName"
3. **Multiple Authors**: Comma separation, "&" vs "and"
4. **Fanfiction Specifics**: Username vs real name attribution

### Recommended Matching Strategy
```python
def match_books(kobo_book, calibre_books):
    # 1. Exact title + author match
    # 2. Normalized title + author match  
    # 3. Fuzzy string matching with threshold
    # 4. Manual review queue for uncertainties
```

## Data Migration Mapping

### Collections → Calibre Tags
```
Kobo Shelf.Name → Calibre tags (comma-separated)
Examples:
  "sweet fluff" → "sweet-fluff" tag
  "historic au" → "historic-au" tag
  "killjoys" → "killjoys" tag
```

### Reading Status → Calibre Metadata
```
Kobo ReadStatus → Calibre custom column or built-in rating
  2 (read) → Mark as read, potentially 3-5 star rating
  0/1 (unread/reading) → Mark as unread
```

### Date Tracking
```
Kobo DateLastRead → Calibre "Date read" field
Kobo ___PercentRead → Custom column for reading progress
```

## Development Environment Setup

### Required Dependencies
```python
# Core requirements
sqlite3  # Built into Python
subprocess  # For calibredb commands
pathlib  # File path handling
logging  # Progress tracking
configparser  # Configuration management

# Optional/future requirements  
fuzzy-wuzzy  # String matching
python-Levenshtein  # String similarity
calibre  # For direct API access (Phase 5)
tkinter  # GUI interface (Phase 4)
```

### Project Structure Recommendation
```
kobo-to-calibre/
├── src/
│   ├── kobo_reader.py      # Kobo database access
│   ├── calibre_updater.py  # Calibre metadata updates
│   ├── book_matcher.py     # Book matching logic
│   ├── config_manager.py   # Configuration handling
│   └── sync_engine.py      # Main orchestration
├── config/
│   ├── library_mappings.json
│   └── collection_mappings.json
├── tests/
├── docs/
└── main.py
```

## Risk Assessment

### Data Safety Risks
**High Risk**: Direct Calibre database modification
**Mitigation**: Always backup metadata.db before changes

**Medium Risk**: Book matching errors
**Mitigation**: Conservative matching + manual review

**Low Risk**: Kobo database access
**Mitigation**: Read-only operations, no modifications

### Performance Considerations
**Large Libraries**: 1000+ books may need batch processing
**Multiple Libraries**: Parallel processing opportunities
**Database Locks**: Handle Calibre database in-use scenarios

## Next Phase Readiness

### Phase 2 Prerequisites Met
✅ Database schemas documented
✅ Sample data analyzed  
✅ Integration options identified
✅ Matching strategy planned
✅ Risk mitigations defined

### Phase 2 Recommended Focus
1. **Single library sync** (start with smaller "Misc" library)
2. **Conservative matching** (exact matches only initially)
3. **Command line interface** for safety
4. **Dry-run mode** for all operations
5. **Comprehensive logging** for debugging

### Configuration Requirements for Phase 2
- Library path mappings
- Collection filtering preferences  
- Book matching thresholds
- Backup preferences
- Logging levels

**Ready to proceed to Phase 2 development upon user configuration completion.**