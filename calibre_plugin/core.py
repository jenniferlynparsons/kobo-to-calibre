"""Plan and apply Kobo rating writes for one Calibre library. No Qt, so it runs headless in tests."""

import shutil
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

try:
    from kobo_reader import DEVICE_DB, RATINGS, KoboReader
    from library_manager import CalibreLibrary, LibraryManager
    from book_matcher import BookMatcher
except ImportError:  # loaded as calibre_plugins.kobo_ratings inside the Calibre plugin
    from .kobo_reader import DEVICE_DB, RATINGS, KoboReader
    from .library_manager import CalibreLibrary, LibraryManager
    from .book_matcher import BookMatcher

COLUMN = '#myratings'


def read_device(device_db=DEVICE_DB):
    """Read Kobo books from a temp copy. SQLite never opens the device file itself."""
    device_db = Path(device_db)
    if not device_db.exists():
        raise FileNotFoundError(f"Kobo not connected: {device_db} not found")
    with tempfile.TemporaryDirectory() as d:
        copy = Path(d) / "KoboReader.sqlite"
        shutil.copy(device_db, copy)
        try:
            conn = sqlite3.connect(f"{copy.as_uri()}?mode=ro", uri=True)
            check = conn.execute("PRAGMA quick_check").fetchone()[0]
            conn.close()
        except sqlite3.DatabaseError as e:
            check = str(e)
        if check != "ok":
            raise ValueError(f"Kobo DB copy failed its integrity check ({check}). "
                             "Eject and reconnect the Kobo, then try again.")
        return KoboReader(str(copy)).get_books_with_collections()


def preview(api, library_path, device_db=DEVICE_DB):
    """Return (changes {book_id: ratings}, summary, details). Writes nothing."""
    if COLUMN not in api.field_metadata.custom_field_keys():
        raise ValueError(f"This library has no {COLUMN} column. Add it (text, multiple values) first.")

    books = read_device(device_db)
    library_path = Path(library_path)
    library = CalibreLibrary(library_path.name, library_path, library_path / "metadata.db", is_primary=True)
    manager = LibraryManager()
    manager.libraries, manager.primary_library = [library], library
    matches, unmatched, _ = BookMatcher(manager).match_all_books(books)

    rated = {}
    for m in matches:
        ratings = tuple(c for c in m.kobo_book.collections if c in RATINGS.values())
        if ratings:
            rated[m.calibre_book_id] = ratings
    current = {book_id: api.field_for(COLUMN, book_id) or () for book_id in rated}
    changes = {k: v for k, v in rated.items() if sorted(current[k]) != sorted(v)}

    summary = (f"{len(books)} Kobo books, {len(matches)} matched in {library.name}, {len(rated)} rated.\n"
               f"{len(changes)} to write, {len(rated) - len(changes)} already up to date. "
               f"Existing ratings are never cleared.")
    lines = [f"{api.field_for('title', k)}: {', '.join(current[k]) or '(none)'} -> {', '.join(v)}"
             for k, v in changes.items()]
    shelved = [b for b in unmatched if b.collections]
    if shelved:
        lines += ["", f"On a Kobo shelf but not in this library ({len(shelved)}):"]
        lines += [f"  {b.title} by {b.author} [{', '.join(b.collections)}]" for b in shelved]
    return changes, summary, "\n".join(lines)


def apply(api, changes, backup_dir):
    """Back up metadata.db, then write all changes in one call. Returns the backup path."""
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"metadata_{datetime.now():%Y%m%d_%H%M%S}.db"
    api.backend.backup_database(str(backup))
    api.set_field(COLUMN, changes)
    return backup
