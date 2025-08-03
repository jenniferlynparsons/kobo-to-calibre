# Kobo-to-Calibre Sync Automation Project Plan

## Project Overview
Automate the transfer of reading data, ratings, and collection metadata from Kobo e-reader to Calibre libraries, eliminating the current manual process of database queries, collection filtering, and individual book metadata updates.

## Current Manual Process (To Be Automated)
1. Mount Kobo device on computer
2. Open Kobo database in SQLite browser
3. Filter by collections to find read books
4. For each book, find corresponding entry in Calibre
5. Manually add rating and category metadata
6. Repeat across multiple Calibre libraries

## Project Goals
- **Primary**: One-click sync of Kobo reading data to Calibre
- **Secondary**: Support multiple Calibre libraries with different metadata granularity
- **Stretch**: Auto-detect device connection and run sync automatically
- **Ultimate**: Package as Calibre plugin for seamless integration

---

## Phase 1: Research & Discovery

### Understanding Current Setup
**Questions to Answer:**
- What exactly are the collection names you use for ratings? (1-star, 2-star, etc.)
- What are your category collection names? (fluff, omegaverse, hurt/comfort, etc.)
- How do you want to handle books that are in multiple collections?
- What's your current Calibre library structure? (MCR, Other Fandoms, Catchall)
- Are there any collections you want to ignore/not sync?

### Technical Investigation
- **Kobo Database Structure**: Map out relevant tables (ShelfContent, Shelf, content)
- **Calibre Database Structure**: Understand metadata.db schema and custom columns
- **Book Matching Logic**: How to reliably match Kobo books to Calibre entries
- **Calibre API Options**: Command line vs. Python library vs. plugin API

### Deliverables
- Documentation of Kobo database schema relevant to collections
- Documentation of current collection naming conventions
- Test data set for development (backup of small Kobo database)

---

## Phase 2: Core Script Development

### MVP Script Features
- Read Kobo database and extract collection data
- Match books between Kobo and specific Calibre library
- Update Calibre metadata (tags/custom fields) based on collections
- Handle rating collections (convert collection names to 1-5 star ratings)
- Log what was updated for verification

### Script Architecture
```
kobo_sync.py
├── kobo_reader.py (read Kobo database)
├── calibre_updater.py (update Calibre metadata)
├── book_matcher.py (match books between systems)
├── config.py (library paths, collection mappings)
└── main.py (orchestrate the sync)
```

### Key Technical Decisions
- **Book Matching Strategy**: Title+Author vs. ISBN vs. file hash
- **Metadata Storage**: Use existing tags vs. create custom columns
- **Conflict Resolution**: What happens if book is in multiple rating collections?
- **Logging Level**: How much detail to track for troubleshooting

### Development Questions
- Should ratings be stored as Calibre ratings (1-5 stars) or as tags?
- How to handle books that exist on Kobo but not in Calibre?
- What to do with books that have been removed from Kobo since last sync?
- Should the script be idempotent (safe to run multiple times)?

---

## Phase 3: Multi-Library Support

### Configuration System
- Map different Calibre libraries to different sync behaviors
- MCR library: Full metadata sync (ratings + detailed categories)
- Other libraries: Minimal sync (ratings + read/unread only)
- Flexible collection-to-tag mapping per library

### Technical Challenges
- Handle different Calibre library schemas
- Batch processing for efficiency
- Error handling when a library is missing or corrupted
- Progress reporting for long-running syncs

---

## Phase 4: User Experience Improvements

### Standalone Script Enhancements
- GUI interface (tkinter or similar) for non-technical users
- Configuration wizard for first-time setup
- Dry-run mode to preview changes before applying
- Backup/restore functionality for safety

### Auto-Detection Features
- Detect when Kobo is connected to computer
- Auto-discover Calibre library locations
- Smart defaults for collection mappings

---

## Phase 5: Calibre Plugin Development

### Plugin Architecture
- Integrate with Calibre's existing device management
- Add menu items for manual sync
- Preferences panel for configuration
- Status reporting in Calibre's job system

### Plugin Features
- **Device Detection**: Automatically recognize connected Kobo
- **Library Integration**: Work with currently selected Calibre library
- **Progress Reporting**: Use Calibre's built-in progress dialogs
- **Error Handling**: Graceful failure with user-friendly messages

### Plugin Development Resources
- Calibre Plugin Development Guide
- Example plugins from Calibre source
- MobileRead forum plugin development section
- Calibre API documentation

---

## Technical Specifications

### Kobo Database Tables (To Investigate)
- `content` - Main book information
- `Shelf` - Collection definitions  
- `ShelfContent` - Books in collections
- `Event` - Reading progress/completion

### Calibre Integration Options
1. **Command Line**: Use `calibredb` commands
2. **Python API**: Direct database manipulation
3. **Plugin API**: Full Calibre integration

### Development Environment
- Python 3.8+ (Calibre compatibility)
- SQLite3 for database access
- Calibre development environment for plugin testing

---

## Success Metrics

### Phase 1 Success
- Complete understanding of data structures
- Working proof-of-concept for single book sync

### Phase 2 Success  
- Script successfully syncs entire Kobo collection to one Calibre library
- No data loss or corruption
- Process takes under 2 minutes for 200+ books

### Phase 3 Success
- Multi-library sync works reliably
- Different metadata granularity per library
- Configuration system is flexible and maintainable

### Plugin Success
- One-click sync from Calibre interface
- Seamless integration with existing Calibre workflow
- Documentation good enough for other users

---

## Risk Assessment & Mitigation

### Data Safety Risks
- **Risk**: Corrupting Calibre database
- **Mitigation**: Always backup before sync, test extensively on copies

### Development Risks  
- **Risk**: Kobo database structure changes with firmware updates
- **Mitigation**: Version detection, graceful degradation

### Usability Risks
- **Risk**: Too complex for actual daily use
- **Mitigation**: Prioritize simplicity, good defaults, clear error messages

---

## Resources & Next Steps

### Immediate Actions
1. Backup current Kobo database for development
2. Document current collection naming conventions
3. Set up development environment with test Calibre libraries
4. Research existing solutions on MobileRead forums

### Key Resources
- MobileRead Forums (Calibre Plugin Development)
- Calibre source code and documentation
- Kobo database documentation/reverse engineering posts
- SQLite documentation and tools

### Project Timeline Estimate
- **Phase 1**: 1-2 weeks (part-time)
- **Phase 2**: 2-3 weeks (part-time)  
- **Phase 3**: 1-2 weeks (part-time)
- **Phase 4**: 2-3 weeks (part-time)
- **Phase 5**: 3-4 weeks (part-time)

**Total: 2-3 months of part-time development**

---

## Questions for Initial Planning Session

### Workflow Questions
1. What's your ideal workflow? Plug in Kobo → automatic sync, or manual trigger?
2. How often do you want to sync? After every reading session or weekly batch?
3. What should happen if the same book exists in multiple Calibre libraries?

### Metadata Questions  
4. Do you want to preserve existing Calibre ratings/tags, or overwrite with Kobo data?
5. Should the script add a "synced from Kobo" tag for tracking?
6. How do you want to handle books with multiple genre/category collections?

### Technical Questions
7. Are you comfortable running Python scripts, or do you need a GUI?
8. Do you want to share this tool with other people eventually?
9. How important is backwards compatibility if you change your collection system?

### Safety Questions
10. How often do you backup your Calibre libraries currently?
11. What's your comfort level with beta software modifying your book database?
12. Do you want verbose logging for troubleshooting, or just success/failure?