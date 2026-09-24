"""Check: KoboReader refuses the mounted device DB and opens copies read-only."""

import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))
from kobo_reader import KoboReader

mounted = Path("/Volumes/KOBOeReader/.kobo/KoboReader.sqlite")
if mounted.exists():
    try:
        KoboReader(str(mounted)).connect()
        raise AssertionError("mounted DB was opened")
    except ValueError:
        pass

with tempfile.TemporaryDirectory() as d:
    copy = Path(d) / "Kobo Reader.sqlite"  # space checks URI escaping
    sqlite3.connect(copy).execute("CREATE TABLE t (x)").connection.commit()
    conn = KoboReader(str(copy)).connect()
    try:
        conn.execute("INSERT INTO t VALUES (1)")
        raise AssertionError("copy was writable")
    except sqlite3.OperationalError:
        pass
    conn.close()

print("ok")
