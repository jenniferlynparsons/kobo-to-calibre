"""Check: Kobo author strings match Calibre's stored author names."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))
from book_matcher import BookMatcher

m = BookMatcher(None)
match = lambda kobo, calibre: m._check_author_match(m.normalize_author(kobo), calibre)

assert match("409_conflict, ritualist", "409_conflict| ritualist")  # Calibre stores ',' as '|'
assert match("akamine_chan", "jiksa & akamine_chan")                # one of several authors
assert match("Scalzi, John", "John Scalzi")                         # Last, First
assert not match("ritualist", "someone_else")
assert not match("", "John Scalzi")
print("ok")
