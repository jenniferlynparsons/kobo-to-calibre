"""
GUI - Tkinter interface for multi-library sync operations
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
from typing import List, Dict

from config_manager import ConfigManager
from sync_engine import SyncEngine


class KoboSyncGUI:
    """Main GUI application for Kobo-to-Calibre sync."""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize the GUI application."""
        self.config_manager = config_manager
        self.sync_engine = None
        self.logger = logging.getLogger(__name__)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Kobo-to-Calibre Sync Tool")
        self.root.geometry("800x600")
        
        # Create GUI components
        self._create_widgets()
        self._setup_logging_handler()
    
    def _create_widgets(self):
        """Create and layout GUI widgets."""
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sync tab
        self.sync_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sync_frame, text="Sync")
        self._create_sync_tab()
        
        # Configuration tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        self._create_config_tab()
        
        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        self._create_logs_tab()
    
    def _create_sync_tab(self):
        """Create the main sync interface."""
        
        # Library status frame
        status_frame = ttk.LabelFrame(self.sync_frame, text="Library Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.library_status = ttk.Label(status_frame, text="Click 'Discover Libraries' to scan for Calibre libraries")
        self.library_status.pack(padx=10, pady=10)
        
        # Control buttons frame
        control_frame = ttk.Frame(self.sync_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.discover_btn = ttk.Button(control_frame, text="Discover Libraries", command=self._discover_libraries)
        self.discover_btn.pack(side=tk.LEFT, padx=5)
        
        self.sync_btn = ttk.Button(control_frame, text="🔍 START PREVIEW", command=self._start_sync, state=tk.DISABLED)
        self.sync_btn.pack(side=tk.LEFT, padx=5)
        
        # Enhanced dry run section with visual warning
        dry_run_frame = ttk.LabelFrame(control_frame, text="⚠️ SYNC MODE")
        dry_run_frame.pack(side=tk.LEFT, padx=20, pady=5)
        
        self.dry_run_var = tk.BooleanVar(value=True)
        self.dry_run_check = ttk.Checkbutton(dry_run_frame, text="🔍 DRY RUN (PREVIEW ONLY - NO CHANGES)", 
                                            variable=self.dry_run_var, command=self._on_dry_run_toggle)
        self.dry_run_check.pack(padx=10, pady=5)
        
        # Status indicator
        self.mode_status = ttk.Label(dry_run_frame, text="📋 Preview mode - no files will be modified", 
                                   foreground="orange")
        self.mode_status.pack(padx=10, pady=2)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.sync_frame, text="Progress")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(progress_frame, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_config_tab(self):
        """Create configuration interface."""
        
        # Kobo database path
        kobo_frame = ttk.LabelFrame(self.config_frame, text="Kobo Database")
        kobo_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(kobo_frame, text="Database Path:").pack(anchor=tk.W, padx=10, pady=5)
        self.kobo_path_var = tk.StringVar(value=self.config_manager.get_kobo_database_path())
        kobo_path_entry = ttk.Entry(kobo_frame, textvariable=self.kobo_path_var, width=60)
        kobo_path_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Library search paths
        paths_frame = ttk.LabelFrame(self.config_frame, text="Library Search Paths")
        paths_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.paths_listbox = tk.Listbox(paths_frame)
        self.paths_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load current search paths
        for path in self.config_manager.get_search_paths():
            self.paths_listbox.insert(tk.END, path)
    
    def _create_logs_tab(self):
        """Create logs display interface."""
        
        # Log level selection
        level_frame = ttk.Frame(self.logs_frame)
        level_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(level_frame, text="Log Level:").pack(side=tk.LEFT, padx=5)
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(level_frame, textvariable=self.log_level_var, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"])
        log_level_combo.pack(side=tk.LEFT, padx=5)
        
        # Log management buttons
        log_buttons_frame = ttk.Frame(self.logs_frame)
        log_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_buttons_frame, text="📂 Open Logs Folder", 
                  command=self._open_logs_folder).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(log_buttons_frame, text="📄 Open Unmatched Report", 
                  command=self._open_unmatched_report).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(log_buttons_frame, text="🔄 Rotate Logs", 
                  command=self._rotate_logs).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(log_buttons_frame, text="🗑️ Clear Old Logs", 
                  command=self._clear_old_logs).pack(side=tk.LEFT, padx=5)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(self.logs_frame)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _setup_logging_handler(self):
        """Setup custom logging handler to display logs in GUI."""
        
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
        
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # Add handler to root logger
        logging.getLogger().addHandler(gui_handler)
    
    def _on_dry_run_toggle(self):
        """Handle dry run checkbox toggle."""
        if self.dry_run_var.get():
            # Preview mode
            self.sync_btn.config(text="🔍 START PREVIEW")
            self.mode_status.config(text="📋 Preview mode - no files will be modified", foreground="orange")
        else:
            # Real sync mode
            self.sync_btn.config(text="⚡ START REAL SYNC")
            self.mode_status.config(text="⚠️ REAL SYNC - will modify Calibre libraries!", foreground="red")
    
    def _discover_libraries(self):
        """Discover Calibre libraries in background thread."""
        self.discover_btn.config(state=tk.DISABLED)
        self.progress_var.set("Discovering libraries...")
        self.progress_bar.start()
        
        def discovery_task():
            try:
                self.sync_engine = SyncEngine(self.config_manager)
                libraries = self.sync_engine.discover_libraries()
                
                # Update GUI in main thread
                self.root.after(0, self._on_discovery_complete, libraries)
                
            except Exception as e:
                self.root.after(0, self._on_discovery_error, str(e))
        
        threading.Thread(target=discovery_task, daemon=True).start()
    
    def _on_discovery_complete(self, libraries: List):
        """Handle library discovery completion."""
        self.progress_bar.stop()
        self.discover_btn.config(state=tk.NORMAL)
        
        if libraries:
            status_text = f"Found {len(libraries)} libraries:\n"
            for lib in libraries:
                primary_indicator = " (PRIMARY)" if lib.is_primary else ""
                status_text += f"  • {lib.name}{primary_indicator}\n"
            
            self.library_status.config(text=status_text)
            self.sync_btn.config(state=tk.NORMAL)
            self.progress_var.set("Ready to sync")
        else:
            self.library_status.config(text="No Calibre libraries found. Check search paths in Configuration tab.")
            self.progress_var.set("No libraries found")
    
    def _on_discovery_error(self, error_msg: str):
        """Handle library discovery error."""
        self.progress_bar.stop()
        self.discover_btn.config(state=tk.NORMAL)
        self.progress_var.set("Discovery failed")
        messagebox.showerror("Discovery Error", f"Failed to discover libraries:\n{error_msg}")
    
    def _start_sync(self):
        """Start sync process in background thread."""
        if not self.sync_engine:
            messagebox.showerror("Error", "Please discover libraries first")
            return
        
        dry_run = self.dry_run_var.get()
        
        # Enhanced confirmation for real sync
        if not dry_run:
            response = messagebox.askyesno(
                "⚠️ CONFIRM REAL SYNC",
                "This will make ACTUAL CHANGES to your Calibre libraries!\n\n"
                "✅ Backup files will be created automatically\n"
                "✅ Collection data will be written to custom columns\n\n"
                "Are you absolutely sure you want to proceed?",
                icon='warning'
            )
            if not response:
                return
        
        self.sync_btn.config(state=tk.DISABLED)
        
        if dry_run:
            self.progress_var.set("🔍 Running preview - no changes will be made")
        else:
            self.progress_var.set("⚡ Running REAL SYNC - making changes to Calibre")
        
        self.progress_bar.start()
        self.results_text.delete(1.0, tk.END)
        
        def sync_task():
            try:
                results = self.sync_engine.run_sync(dry_run=dry_run)
                self.root.after(0, self._on_sync_complete, results)
            except Exception as e:
                self.root.after(0, self._on_sync_error, str(e))
        
        threading.Thread(target=sync_task, daemon=True).start()
    
    
    def _on_sync_complete(self, results: Dict):
        """Handle sync completion."""
        self.progress_bar.stop()
        self.sync_btn.config(state=tk.NORMAL)
        
        is_dry_run = results.get('dry_run', False)
        conflicts_count = results.get('conflicts_count', 0)
        
        # Check if conflicts need resolution
        if conflicts_count > 0 and self.sync_engine:
            self.logger.info(f"Handling {conflicts_count} conflicts")
            conflicts = self.sync_engine.conflicts
            resolved_matches = self._resolve_conflicts(conflicts)
            
            if resolved_matches:
                # Apply resolved matches and update results
                self.sync_engine.apply_conflict_resolutions(resolved_matches)
                
                # Update results to reflect resolved conflicts
                results['total'] = results.get('total', 0) + len(resolved_matches)
                results['conflicts_count'] = len(conflicts) - len(resolved_matches)
                
                self.logger.info(f"Resolved {len(resolved_matches)} conflicts")
        
        if is_dry_run:
            self.progress_var.set("🔍 Preview completed - no changes made")
            header = "🔍 PREVIEW RESULTS (NO CHANGES MADE)\n"
            self.results_text.config(bg="lightyellow")
        else:
            self.progress_var.set("⚡ Real sync completed - changes made to Calibre!")
            header = "⚡ REAL SYNC RESULTS (CHANGES MADE TO CALIBRE)\n"
            self.results_text.config(bg="lightgreen")
        
        # Display results with clear formatting
        self.results_text.insert(tk.END, header)
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Show key metrics
        total = results.get('total', 0)
        successful = results.get('successful', 0) 
        failed = results.get('failed', 0)
        
        self.results_text.insert(tk.END, f"Books processed: {total}\n")
        if is_dry_run:
            self.results_text.insert(tk.END, f"Books ready to update: {successful}\n")
        else:
            self.results_text.insert(tk.END, f"Successfully updated: {successful}\n")
        self.results_text.insert(tk.END, f"Failed: {failed}\n")
        self.results_text.insert(tk.END, f"Libraries affected: {len(results.get('libraries_updated', []))}\n")
        self.results_text.insert(tk.END, f"Unmatched books: {results.get('unmatched_count', 0)}\n")
        
        if conflicts_count > 0:
            remaining_conflicts = results.get('conflicts_count', conflicts_count)
            self.results_text.insert(tk.END, f"Conflicts resolved: {conflicts_count - remaining_conflicts}\n")
            if remaining_conflicts > 0:
                self.results_text.insert(tk.END, f"Conflicts remaining: {remaining_conflicts}\n")
        self.results_text.insert(tk.END, "\n")
        
        # Show unmatched books info
        if 'reports' in results and 'unmatched_file' in results['reports']:
            unmatched_file = results['reports']['unmatched_file']
            if unmatched_file:
                self.results_text.insert(tk.END, f"Unmatched books report saved to:\n{unmatched_file}\n\n")
        
        # Show unmatched summary
        if 'reports' in results and 'unmatched' in results['reports']:
            self.results_text.insert(tk.END, results['reports']['unmatched'])
        
        # Show completion message
        if is_dry_run:
            if total > 0:
                conflict_msg = ""
                if conflicts_count > 0:
                    resolved_count = conflicts_count - results.get('conflicts_count', 0)
                    conflict_msg = f"\nConflicts resolved: {resolved_count}"
                    if results.get('conflicts_count', 0) > 0:
                        conflict_msg += f"\nConflicts remaining: {results.get('conflicts_count', 0)}"
                
                messagebox.showinfo(
                    "🔍 Preview Complete", 
                    f"Preview completed successfully!\n\n"
                    f"Found {total} books ready to update.\n"
                    f"Unmatched: {results.get('unmatched_count', 0)} books{conflict_msg}\n\n"
                    f"Uncheck 'DRY RUN' and click sync button to make actual changes."
                )
            else:
                messagebox.showinfo("🔍 Preview Complete", "No books found to update.")
        else:
            if successful > 0:
                messagebox.showinfo(
                    "⚡ Sync Complete!", 
                    f"Successfully updated {successful} books!\n\n"
                    f"Failed: {failed}\n"
                    f"Total processed: {total}\n\n"
                    f"Your Calibre libraries have been updated."
                )
            else:
                messagebox.showwarning(
                    "⚠️ Sync Issues", 
                    f"No books were successfully updated.\n\n"
                    f"Check the logs for details."
                )
    
    
    def _on_sync_error(self, error_msg: str):
        """Handle sync error."""
        self.progress_bar.stop()
        self.sync_btn.config(state=tk.NORMAL)
        self.progress_var.set("Sync failed")
        messagebox.showerror("Sync Error", f"Sync failed:\n{error_msg}")
    
    def _resolve_conflicts(self, conflicts: List) -> List:
        """Resolve conflicts through user dialog."""
        if not conflicts:
            return []
        
        resolved_matches = []
        
        for conflict in conflicts:
            # Create conflict resolution dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Resolve Conflict")
            dialog.geometry("600x400")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
            y = (dialog.winfo_screenheight() // 2) - (400 // 2)
            dialog.geometry(f"600x400+{x}+{y}")
            
            # Book info
            book_frame = ttk.LabelFrame(dialog, text="Book Information")
            book_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(book_frame, text=f"Title: {conflict.kobo_book.title}", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(book_frame, text=f"Author: {conflict.kobo_book.author}").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(book_frame, text=f"Collections: {', '.join(conflict.kobo_book.collections[:5])}").pack(anchor=tk.W, padx=10, pady=2)
            
            # Conflict info
            conflict_frame = ttk.LabelFrame(dialog, text="Found in Multiple Libraries")
            conflict_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            ttk.Label(conflict_frame, text="This book was found in the following libraries:").pack(anchor=tk.W, padx=10, pady=5)
            
            # Resolution options
            resolution_var = tk.StringVar(value="")
            
            for i, match in enumerate(conflict.matches):
                frame = ttk.Frame(conflict_frame)
                frame.pack(fill=tk.X, padx=10, pady=2)
                
                ttk.Radiobutton(
                    frame, 
                    text=f"Update in {match.library.name} library",
                    variable=resolution_var,
                    value=f"library_{i}"
                ).pack(anchor=tk.W)
            
            # All libraries option
            ttk.Radiobutton(
                conflict_frame,
                text="Update in ALL libraries",
                variable=resolution_var,
                value="all"
            ).pack(anchor=tk.W, padx=10, pady=2)
            
            # Skip option
            ttk.Radiobutton(
                conflict_frame,
                text="Skip this book (don't update anywhere)",
                variable=resolution_var,
                value="skip"
            ).pack(anchor=tk.W, padx=10, pady=2)
            
            # Dialog result
            result = {"action": None}
            
            def on_ok():
                result["action"] = resolution_var.get()
                dialog.destroy()
            
            def on_skip_all():
                result["action"] = "skip_all"
                dialog.destroy()
            
            # Buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=5)
            ttk.Button(button_frame, text="Skip All Conflicts", command=on_skip_all).pack(side=tk.RIGHT, padx=5)
            
            # Wait for user response
            dialog.wait_window()
            
            # Process result
            action = result["action"]
            
            if action == "skip_all":
                break
            elif action == "skip" or not action:
                continue
            elif action == "all":
                resolved_matches.extend(conflict.matches)
            elif action.startswith("library_"):
                library_index = int(action.split("_")[1])
                resolved_matches.append(conflict.matches[library_index])
        
        return resolved_matches
    
    def _clear_logs(self):
        """Clear the log display."""
        self.log_text.delete(1.0, tk.END)
    
    def run(self):
        """Start the GUI application."""
        self.logger.info("Starting Kobo-to-Calibre Sync GUI")
        self.root.mainloop()
    
    def _open_logs_folder(self):
        """Open the logs folder in file manager."""
        import subprocess
        import os
        from pathlib import Path
        
        logs_path = Path("logs")
        if logs_path.exists():
            try:
                # macOS
                subprocess.run(["open", str(logs_path)])
                self.logger.info(f"📂 Opened logs folder: {logs_path.absolute()}")
            except Exception as e:
                self.logger.error(f"Failed to open logs folder: {e}")
        else:
            messagebox.showwarning("Logs Folder", "Logs folder does not exist yet.")
    
    def _open_unmatched_report(self):
        """Open the most recent unmatched books report."""
        import subprocess
        from pathlib import Path
        import glob
        
        logs_path = Path("logs")
        if not logs_path.exists():
            messagebox.showwarning("No Reports", "No logs folder found.")
            return
        
        # Find most recent unmatched books report
        pattern = str(logs_path / "unmatched_books_*.txt")
        reports = glob.glob(pattern)
        
        if not reports:
            messagebox.showinfo("No Reports", "No unmatched books reports found.")
            return
        
        # Get most recent report
        latest_report = max(reports, key=os.path.getctime)
        
        try:
            # Open with default text editor
            subprocess.run(["open", latest_report])
            self.logger.info(f"📄 Opened unmatched report: {latest_report}")
        except Exception as e:
            self.logger.error(f"Failed to open unmatched report: {e}")
            messagebox.showerror("Error", f"Failed to open report: {e}")
    
    def _rotate_logs(self):
        """Rotate current logs (archive old ones)."""
        try:
            from pathlib import Path
            import shutil
            from datetime import datetime
            
            logs_path = Path("logs")
            if not logs_path.exists():
                messagebox.showinfo("No Logs", "No logs to rotate.")
                return
            
            # Create archive name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"kobo_sync_archived_{timestamp}.log"
            archive_path = logs_path / archive_name
            
            # Archive main log file
            main_log = logs_path / "kobo_sync.log"
            if main_log.exists():
                shutil.move(str(main_log), str(archive_path))
                self.logger.info(f"📦 Archived log to: {archive_name}")
                messagebox.showinfo("Logs Rotated", f"Archived current log to: {archive_name}")
            else:
                messagebox.showinfo("No Active Log", "No active log file to rotate.")
                
        except Exception as e:
            self.logger.error(f"Failed to rotate logs: {e}")
            messagebox.showerror("Error", f"Failed to rotate logs: {e}")
    
    def _clear_old_logs(self):
        """Clear old log files (keep recent ones)."""
        try:
            from pathlib import Path
            import glob
            import os
            
            logs_path = Path("logs")
            if not logs_path.exists():
                messagebox.showinfo("No Logs", "No logs folder found.")
                return
            
            # Get all log files
            log_files = []
            for pattern in ["*.log", "unmatched_books_*.txt"]:
                log_files.extend(glob.glob(str(logs_path / pattern)))
            
            if len(log_files) <= 5:  # Keep at least 5 recent files
                messagebox.showinfo("Keep Logs", f"Only {len(log_files)} log files found. Keeping all recent logs.")
                return
            
            # Sort by modification time, keep newest 5
            log_files.sort(key=os.path.getmtime, reverse=True)
            files_to_delete = log_files[5:]  # Delete older files
            
            # Confirm deletion
            response = messagebox.askyesno(
                "Confirm Cleanup",
                f"Delete {len(files_to_delete)} old log files?\\n\\n"
                f"This will keep the 5 most recent logs."
            )
            
            if response:
                deleted_count = 0
                for file_path in files_to_delete:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        self.logger.warning(f"Could not delete {file_path}: {e}")
                
                self.logger.info(f"🗑️ Deleted {deleted_count} old log files")
                messagebox.showinfo("Cleanup Complete", f"Deleted {deleted_count} old log files.")
                
        except Exception as e:
            self.logger.error(f"Failed to clear old logs: {e}")
            messagebox.showerror("Error", f"Failed to clear logs: {e}")