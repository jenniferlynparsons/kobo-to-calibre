# Library Setup Guide

## Adding New Calibre Libraries to Kobo Sync

This guide explains how to add additional Calibre libraries to your Kobo-to-Calibre sync setup.

---

## Quick Setup (Recommended)

### Step 1: Update Configuration File

Edit `config/library_mappings.json` and add your new library:

```json
{
  "discovered_libraries": {
    "MCR library sample": {
      "path": "/Users/jenniferparsons/Engineering/Projects/kobo-to-calibre/MCR library sample",
      "is_primary": true,
      "book_count": 1720,
      "custom_columns": {
        "myratings": "My Ratings",
        "my_genres": "My Genres"
      }
    },
    "YOUR_NEW_LIBRARY_NAME": {
      "path": "/path/to/your/calibre/library",  
      "is_primary": false,
      "book_count": 0,
      "custom_columns": {
        "myratings": "My Ratings",
        "my_genres": "My Genres"
      }
    }
  }
}
```

### Step 2: Update Search Paths

Edit `config/sync_preferences.json` and add the parent directory of your library:

```json
{
  "search_paths": [
    "/Users/jenniferparsons/Engineering/Projects/kobo-to-calibre",
    "/path/to/parent/directory/of/your/library"
  ]
}
```

---

## Manual Code Setup (Advanced)

If you prefer to modify the code directly:

### Step 1: Edit config_manager.py

Find the `get_search_paths()` method in `config_manager.py` and add your library path:

```python
def get_search_paths(self) -> List[str]:
    """Get library search paths."""
    return [
        "/Users/jenniferparsons/Engineering/Projects/kobo-to-calibre",
        "/path/to/your/new/library/parent/directory",  # Add this line
        # Add more paths as needed
    ]
```

### Step 2: Edit library_manager.py (Optional)

For explicit library configuration, edit the `discover_libraries()` method:

```python
def discover_libraries(self, search_paths: List[str]) -> List[CalibreLibrary]:
    """Discover Calibre libraries in search paths."""
    # ... existing code ...
    
    # Add your library explicitly if auto-discovery doesn't work
    your_library_path = Path("/full/path/to/your/calibre/library")
    if your_library_path.exists():
        libraries.append(CalibreLibrary(
            name="Your Library Name",
            path=your_library_path,
            is_primary=False  # Set to True if this should be primary
        ))
```

---

## Common Library Locations

### macOS Default Locations:
- `~/Documents/Calibre Library`
- `~/Calibre Library`
- External drives: `/Volumes/[Drive Name]/Calibre Library`

### Custom Locations:
- Network drives
- External USB drives
- Dropbox/iCloud synced folders

---

## Library Configuration Options

### Primary vs Secondary Libraries

**Primary Library**: 
- Searched first for book matches
- Usually your main/largest library
- Set `"is_primary": true` in config

**Secondary Libraries**:
- Searched if book not found in primary
- Set `"is_primary": false` in config

### Custom Columns Required

Each library needs these custom columns:
- **myratings**: For storing Kobo rating collections
- **my_genres**: For storing Kobo genre collections

The sync tool will create these automatically if they don't exist.

---

## Testing New Library Setup

### Step 1: Run Discovery
1. Launch the sync tool
2. Click "Discover Libraries" button
3. Check that your new library appears in the status

### Step 2: Check Logs
Look in the logs tab for messages like:
```
✅ Found custom columns in [Your Library]: {'myratings': 'My Ratings', 'my_genres': 'My Genres'}
```

### Step 3: Test Sync (Dry Run)
1. Run a dry-run sync
2. Check if books are being matched in your new library
3. Look for any error messages in the logs

---

## Troubleshooting

### Library Not Found
- Check the path is correct and accessible
- Make sure the library contains a `metadata.db` file
- Verify permissions to read the library folder

### No Books Matched
- Your library might not contain books that exist on your Kobo
- Check the unmatched books report
- Consider if this library has different content than expected

### Custom Columns Not Created
- Check if Calibre is currently running (close it before sync)
- Verify write permissions to the library folder
- Look for error messages in the logs tab

### Permission Issues
- Make sure Calibre application is closed during sync
- Check folder permissions on the library directory
- Run the sync tool with appropriate user permissions

---

## Example: Adding a Network Library

If your library is on a network drive:

1. **Mount the network drive** in Finder
2. **Find the library path**: `/Volumes/NetworkDrive/Calibre Library`
3. **Add to config**:
   ```json
   "Network Library": {
     "path": "/Volumes/NetworkDrive/Calibre Library",
     "is_primary": false,
     "book_count": 0,
     "custom_columns": {
       "myratings": "My Ratings",
       "my_genres": "My Genres"
     }
   }
   ```

---

## Need Help?

1. **Check the logs** in the GUI logs tab
2. **Use the "Open Logs Folder" button** to see detailed logs
3. **Run with dry-run first** to test before making changes
4. **Check unmatched books report** to see what's not being found

The sync tool is designed to be safe - it always creates backups and has extensive logging to help troubleshoot issues.