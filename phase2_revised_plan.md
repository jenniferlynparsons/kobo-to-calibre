# Phase 2: Revised Implementation Plan

## Key Adjustments Made

### 1. Primary Library Target
- **Changed**: MCR library as primary development target (not Misc library)
- **Reason**: KoboReader.sqlite directly corresponds to MCR library content
- **Impact**: Development will focus on fanfiction-specific metadata patterns

### 2. Multi-Library Architecture
- **Requirement**: Kobo device syncs to multiple Calibre libraries
- **Approach**: Cross-library book discovery and matching
- **Priority**: MCR library first, then search other libraries
- **Conflict handling**: Manual resolution when books exist in multiple libraries

### 3. Rating System Implementation
- **Changed**: Keep rating collections as text (not convert to stars)
- **Examples**:
  - "Evergreen" → "Evergreen" in My Ratings column
  - "Absolute Favorite" → "Absolute Favorite" in My Ratings column
  - "Favorites" → "Favorites" in My Ratings column
  - "Great" → "Great" in My Ratings column

## Updated Technical Architecture

### Project Structure
```
kobo-to-calibre/
├── src/
│   ├── kobo_reader.py          # Extract from KoboReader.sqlite
│   ├── library_manager.py      # Discover & manage multiple libraries
│   ├── calibre_updater.py      # Update custom columns across libraries
│   ├── book_matcher.py         # Cross-library book matching
│   ├── config_manager.py       # Library paths & collection mappings
│   ├── conflict_resolver.py    # Handle multi-library conflicts
│   ├── gui.py                  # Multi-library progress tracking
│   └── sync_engine.py          # Orchestrate multi-library sync
├── config/
│   ├── library_mappings.json   # Calibre library paths
│   ├── rating_collections.json # Rating vs genre classification
│   └── sync_preferences.json   # User preferences from Phase 1
├── logs/
└── main.py
```

### Core Components

#### 1. Library Manager
```python
class LibraryManager:
    def discover_libraries(self) -> List[Library]
    def get_primary_library(self) -> Library  # MCR library
    def search_all_libraries(self, book) -> List[Match]
    def handle_multi_library_conflicts(self, matches) -> Resolution
```

#### 2. Collection Classification
```python
# Rating collections (→ My Ratings column)
RATING_COLLECTIONS = {
    "Evergreen": "Evergreen",
    "Absolute Favorite": "Absolute Favorite", 
    "Favorites": "Favorites",
    "Great": "Great"
}

# Genre collections (→ My Genres column)
GENRE_COLLECTIONS = [
    "sweet fluff", "killjoys", "historic au", 
    "sickfic", "kink", "little", etc.
]
```

#### 3. Cross-Library Book Matching
```python
def find_book_across_libraries(kobo_book):
    # 1. Search MCR library first (primary)
    # 2. Search other libraries if not found
    # 3. Return all matches with library info
    # 4. Handle conflicts if found in multiple
```

## Implementation Priorities

### Phase 2a: Core Multi-Library Support
1. **Library Discovery**: Scan for Calibre libraries, identify MCR as primary
2. **Kobo Collection Analysis**: Separate rating vs genre collections  
3. **Cross-Library Matching**: Search MCR first, fallback to others
4. **Basic Sync**: Update My Ratings and My Genres columns

### Phase 2b: Conflict Resolution & Safety
5. **Conflict Detection**: Identify books in multiple libraries
6. **Manual Resolution**: GUI prompts for user decisions
7. **Backup System**: metadata.db backup for each library
8. **Comprehensive Logging**: Multi-library operation tracking

### Phase 2c: User Experience
9. **GUI Enhancement**: Library selection and progress per library
10. **Skip List Generation**: Report unmatched books by library
11. **Configuration Management**: Save library mappings and preferences

## Success Criteria for Revised Phase 2

### Technical Success
- [ ] Successfully discover MCR library and other Calibre libraries
- [ ] Correctly classify Kobo collections into rating vs genre categories
- [ ] Match books across multiple libraries with MCR priority
- [ ] Update My Ratings column with text values (not stars)
- [ ] Update My Genres column with non-rating collections
- [ ] Generate comprehensive logs for multi-library operations

### User Experience Success
- [ ] GUI shows progress across multiple libraries
- [ ] Manual conflict resolution works for multi-library matches
- [ ] Skip list clearly identifies which library search failed
- [ ] All library metadata.db files backed up before changes
- [ ] User can review and approve changes before applying

### Data Integrity Success
- [ ] No data loss across any Calibre library
- [ ] Rating collections preserved as text (not converted to numbers)
- [ ] Books correctly updated in their respective libraries
- [ ] Conflicts resolved without duplicate entries

## Key Differences from Original Plan

1. **Library Strategy**: Multi-library from start (not single library MVP)
2. **Primary Target**: MCR library (not Misc library) 
3. **Rating Format**: Text preservation (not star conversion)
4. **Architecture**: Cross-library search built-in (not add-on feature)
5. **Conflict Resolution**: Core feature (not edge case handling)

## Next Steps

1. **Start with Task p2_1**: Create multi-library project structure
2. **Focus on MCR library**: Use as primary development and testing target
3. **Text-based ratings**: Implement My Ratings column with preserved text
4. **Multi-library GUI**: Design interface for library selection and progress
5. **Conservative approach**: Strict matching with comprehensive skip lists

**Ready to begin Phase 2 implementation with multi-library, text-rating approach.**