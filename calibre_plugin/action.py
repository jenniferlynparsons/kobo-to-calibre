from pathlib import Path

from calibre.gui2.actions import InterfaceAction
from calibre.gui2.dialogs.message_box import MessageBox
from calibre.utils.config import config_dir
from qt.core import QDialog, QTimer

from calibre_plugins.kobo_ratings.core import apply, preview

BACKUP_DIR = Path(config_dir) / "plugins" / "kobo_ratings_backups"


class KoboRatingsAction(InterfaceAction):
    name = 'Kobo Ratings'
    action_spec = ('Kobo Ratings', 'rating.png', 'Copy Kobo rating shelves into #myratings', None)

    def genesis(self):
        self.qaction.triggered.connect(self.run)

    def _dialog(self, kind, msg, details=''):
        """Show a message box; True if accepted (Yes/OK)."""
        d = MessageBox(kind, 'Kobo Ratings', msg, det_msg=details, show_copy_button=False,
                       parent=self.gui, default_yes=False)
        # Calibre's MessageBox does not grow for wrapped text, so it clips; resize once laid out
        QTimer.singleShot(0, d.adjustSize)
        return d.exec() == QDialog.DialogCode.Accepted

    def run(self):
        db = self.gui.current_db
        # ponytail: runs on the GUI thread (about 1-2s for one library); move to a ThreadedJob if it grows
        try:
            changes, summary, details = preview(db.new_api, db.library_path)
        except Exception as e:
            return self._dialog(MessageBox.ERROR, str(e))
        if not changes:
            return self._dialog(MessageBox.INFO, summary, details)
        if not self._dialog(MessageBox.QUESTION, f"{summary}\n\nWrite these ratings?", details):
            return
        backup = apply(db.new_api, changes, BACKUP_DIR / Path(db.library_path).name)
        self.gui.library_view.model().refresh_ids(list(changes))
        self._dialog(MessageBox.INFO, f"Wrote ratings for {len(changes)} books.\nBackup: {backup}")
