"""Check the plugin core on a temp copy of a library. Run: calibre-debug -e test_plugin_core.py [library]"""

import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "calibre_plugin"))
from calibre.library import db as open_db
from core import COLUMN, DEVICE_DB, apply, preview, read_device

library = Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/jenniferparsons/Books/Heated Rivalry")

with tempfile.TemporaryDirectory() as d:
    d = Path(d)

    # Unreadable or missing device DB is refused
    (d / "bad.sqlite").write_bytes(b"not a database")
    for path, err in ((d / "bad.sqlite", ValueError), (d / "missing.sqlite", FileNotFoundError)):
        try:
            read_device(path)
            raise AssertionError(f"{path.name} was read")
        except err:
            pass

    # Library without the column is refused before the Kobo is read
    try:
        preview(open_db(str(d / "empty")).new_api, d / "empty", d / "missing.sqlite")
        raise AssertionError("library without #myratings was accepted")
    except ValueError:
        pass

    # Real device DB, temp copy of the library
    (d / "lib").mkdir()
    shutil.copy2(library / "metadata.db", d / "lib" / "metadata.db")
    api = open_db(str(d / "lib")).new_api
    device_before = DEVICE_DB.stat()
    before = {i: api.field_for(COLUMN, i) for i in api.all_book_ids()}

    changes, summary, details = preview(api, d / "lib")
    print(summary, "\n" + details)
    assert {i: api.field_for(COLUMN, i) for i in api.all_book_ids()} == before, "preview wrote"

    backup = apply(api, changes, d / "backups")
    after = {i: api.field_for(COLUMN, i) for i in api.all_book_ids()}
    for i in after:
        if i in changes:
            assert sorted(after[i]) == sorted(changes[i]), (i, after[i], changes[i])
        else:
            assert after[i] == before[i], f"book {i} changed without being planned"
    assert preview(api, d / "lib")[0] == {}, "second preview still has changes"
    assert sqlite3.connect(backup).execute("SELECT COUNT(*) FROM books").fetchone()[0] == len(before)

    device_after = DEVICE_DB.stat()
    assert (device_after.st_size, device_after.st_mtime) == (device_before.st_size, device_before.st_mtime)

print("ok")
