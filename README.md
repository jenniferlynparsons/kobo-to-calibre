# Kobo-to-Calibre Sync

Copies Kobo collections into Calibre custom columns. Rating collections go to `#myratings`.
Other collections go to `#my_genres`, but only in libraries that already have that column.

Python 3 standard library only. Calibre must be installed (the tool runs `calibredb`).

## Run

1. Copy `/Volumes/KOBOeReader/.kobo/KoboReader.sqlite` to `~/Desktop`. The tool does not open the
   device DB, and it stops if the Desktop copy is older than the device DB.
2. Close Calibre.
3. Double-click `launch_kobo_sync.command` (or run `python3 main.py`).
4. Click **Discover Libraries**, then run a preview (dry run). Clear **DRY RUN** to write.

The tool backs up each `metadata.db` to `backups/` before it writes. Logs and the unmatched-books
report go to `logs/`.

## Configuration

`config/library_mappings.json`:

- `search_paths`: folders to scan for Calibre libraries (any folder with a `metadata.db`).
- `kobo_database_path`: the Desktop copy of the Kobo DB.

A library with `mcr` in its name is the primary library. The tool searches it first. If a book
is not there, the tool searches the other libraries and asks you when a book is in more than one.

## Check

`python3 test_desktop_db.py`
