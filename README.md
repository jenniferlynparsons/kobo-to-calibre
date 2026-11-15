# Kobo-to-Calibre Sync

This project copies Kobo rating shelves into a Calibre custom column, `#myratings`. It has two
tools that use the same matching code:

- **Calibre plugin (recommended).** It works from inside Calibre on the open library. It reads
  the Kobo directly, and Calibre can stay open. It writes ratings only.
- **Standalone script.** It is a separate app that scans all your Calibre libraries at once. It
  reads a copy of the Kobo database on your Desktop. Calibre must be closed when it writes. It
  writes ratings, and it also writes genres to libraries that have a `#my_genres` column.

Both tools run on macOS only.

## Set up your Kobo and Calibre

Both tools use the same rating shelves and the same column.

1. On the Kobo, make these shelves and put each rated book on one of them:

   | Kobo shelf | Value in `#myratings` |
   | --- | --- |
   | `\| evergreen` | Evergreen |
   | `\| absolute favorite` | Absolute Favorite |
   | `\| favorite` | Favorites |
   | `\| good` | Great |

2. In each Calibre library that you sync, add a custom column. Use the lookup name `myratings`,
   the type "Comma separated text, like tags", and any heading.

The tools add ratings and change ratings. They never remove a rating from a book.

A Kobo book matches a Calibre book when the titles match and one author matches. The match ignores
case, punctuation, and a leading "The", "A", or "An". "Last, First" and "First Last" also match.

## Calibre plugin

### Install the plugin

1. Install [Calibre](https://calibre-ebook.com) (version 9 or later).
2. Clone this repo:

   ```sh
   git clone https://github.com/jenniferlynparsons/kobo-to-calibre.git
   cd kobo-to-calibre
   ```

3. Quit Calibre, then install the plugin:

   ```sh
   /Applications/calibre.app/Contents/MacOS/calibre-customize -b calibre_plugin
   ```

4. Start Calibre.
5. Go to **Preferences → Toolbars & menus**. Select **The main toolbar**.
6. Move **Kobo Ratings** from the left list to the right list, then click **Apply**.

To install from a zip file instead, make the zip, then use **Preferences → Plugins → Load plugin
from file**:

```sh
cd calibre_plugin && zip -r ../kobo_ratings.zip . -x '.*' && cd ..
```

### Use the plugin

1. Connect the Kobo with USB. Make sure that it shows in Finder as `KOBOeReader`.
2. In Calibre, open the library that you want to update.
3. Click **Kobo Ratings** (the star button).
4. Read the preview. Click **Show details** to see each change and the books that did not match.
5. Click **Yes** to write the ratings, or **No** to stop.

The plugin does not open the database on the Kobo. It copies the file to a temporary folder,
checks the copy, and reads only the copy.

Before each write, the plugin backs up `metadata.db` to
`~/Library/Preferences/calibre/plugins/kobo_ratings_backups/<library>/`.

The first time, macOS can ask if Calibre can get access to removable volumes. Click **Allow**.

### Update the plugin

After you change the code, quit Calibre and run step 3 of "Install the plugin" again.

`kobo_reader.py`, `book_matcher.py`, and `library_manager.py` in `calibre_plugin/` are symlinks to
the files in `src/`. A change in `src/` also changes the plugin.

## Standalone script

### Install the script

1. Install [Calibre](https://calibre-ebook.com). The script uses its `calibredb` command.
2. Install Python 3 with Tk. The script uses only the standard library, so you do not need pip.
   If you use Homebrew Python, also install Tk:

   ```sh
   brew install python-tk
   ```

   To make sure that Tk works, run `python3 -c "import tkinter"`. It must show no error.

3. Clone this repo (see "Install the plugin", step 2).
4. Edit `config/library_mappings.json`:
   - `search_paths`: the folders that contain your Calibre libraries. The script finds each
     folder below them that has a `metadata.db` file.
   - `kobo_database_path`: the path of the Kobo database copy on your Desktop.

### Use the script

1. Connect the Kobo with USB.
2. Copy the Kobo database to your Desktop:

   ```sh
   cp /Volumes/KOBOeReader/.kobo/KoboReader.sqlite ~/Desktop/
   ```

   If `cp` shows "Operation not permitted", drag the file in Finder. Press **Cmd+Shift+.** to
   show the hidden `.kobo` folder.

3. Quit Calibre.
4. Double-click `launch_kobo_sync.command`, or run `python3 main.py`.
5. Click **Discover Libraries**.
6. Keep **DRY RUN** selected and click **START PREVIEW**. Read the results.
7. To write, clear **DRY RUN** and click **START REAL SYNC**.

The script stops if the Desktop copy is older than the database on the Kobo. Copy the file again
to continue.

Before it writes, the script backs up each `metadata.db` to `backups/`. Logs and the report of
books that did not match go to `logs/`.

If a library name contains `mcr`, the script searches that library first. If a book is in two or
more other libraries, the script asks which library to update.

Genres: each Kobo shelf that is not a rating shelf goes to `#my_genres`. The script writes genres
only to libraries that already have that column. It does not make the column.

## Checks

```sh
python3 test_desktop_db.py
python3 test_author_match.py
/Applications/calibre.app/Contents/MacOS/calibre-debug -e test_plugin_core.py
```

`test_plugin_core.py` needs the Kobo connected. It writes only to a temporary copy of the library.
To test a different library, add its path at the end of the command.
