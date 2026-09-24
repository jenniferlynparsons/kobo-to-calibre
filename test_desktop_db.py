"""Check: KoboReader refuses the mounted device DB and opens copies read-only."""

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))
import kobo_reader
from kobo_reader import KoboReader

try:
    KoboReader("/Volumes/KOBOeReader/.kobo/KoboReader.sqlite").connect()
    raise AssertionError("mounted DB was opened")
except ValueError:
    pass

with tempfile.TemporaryDirectory() as d:
    copy = Path(d) / "Kobo Reader.sqlite"  # space checks URI escaping
    sqlite3.connect(copy).execute("CREATE TABLE t (x)").connection.commit()

    # Stale copy: a fake device DB newer than the copy is refused
    device = Path(d) / "device.sqlite"
    device.touch()
    kobo_reader.DEVICE_DB = device
    os.utime(copy, (0, device.stat().st_mtime - 60))
    try:
        KoboReader(str(copy)).connect()
        raise AssertionError("stale copy was opened")
    except ValueError:
        pass
    os.utime(copy, None)

    conn = KoboReader(str(copy)).connect()
    try:
        conn.execute("INSERT INTO t VALUES (1)")
        raise AssertionError("copy was writable")
    except sqlite3.OperationalError:
        pass
    conn.close()

print("ok")
