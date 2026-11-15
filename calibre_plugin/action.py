from pathlib import Path

from calibre.gui2 import error_dialog, info_dialog, question_dialog
from calibre.gui2.actions import InterfaceAction
from calibre.utils.config import config_dir

from calibre_plugins.kobo_ratings.core import apply, preview

BACKUP_DIR = Path(config_dir) / "plugins" / "kobo_ratings_backups"


class KoboRatingsAction(InterfaceAction):
    name = 'Kobo Ratings'
    action_spec = ('Kobo Ratings', None, 'Copy Kobo rating shelves into #myratings', None)

    def genesis(self):
        self.qaction.triggered.connect(self.run)

    def run(self):
        db = self.gui.current_db
        # ponytail: runs on the GUI thread (about 1-2s for one library); move to a ThreadedJob if it grows
        try:
            changes, summary, details = preview(db.new_api, db.library_path)
        except Exception as e:
            return error_dialog(self.gui, 'Kobo Ratings', str(e), show=True)
        if not changes:
            return info_dialog(self.gui, 'Kobo Ratings', summary, det_msg=details, show=True)
        if not question_dialog(self.gui, 'Kobo Ratings', f"{summary}\n\nWrite these ratings?",
                               det_msg=details, default_yes=False):
            return
        backup = apply(db.new_api, changes, BACKUP_DIR / Path(db.library_path).name)
        self.gui.library_view.model().refresh_ids(list(changes))
        info_dialog(self.gui, 'Kobo Ratings', f"Wrote ratings for {len(changes)} books.\nBackup: {backup}",
                    show=True)
