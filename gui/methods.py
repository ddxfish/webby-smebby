# Updated methods.py file importing from the refactored modules
from gui.main_window import MainWindow

# Import modules from refactored files
from gui.utils import format_time_since, get_short_status_code
from gui.ui_handlers import (
    setup_timers, update_time, update_table_times, 
    load_websites, update_table_row
)
from gui.website_handlers import (
    check_websites, refresh_websites, add_site, edit_site, 
    remove_site, import_from_csv, export_to_csv, 
    show_settings, show_about,
    on_checking_started, on_website_checked, on_website_error, on_checking_complete
)

# Add all the handler methods to the MainWindow class
MainWindow.setup_timers = setup_timers
MainWindow.update_time = update_time
MainWindow.load_websites = load_websites
MainWindow.update_table_row = update_table_row
MainWindow.check_websites = check_websites
MainWindow.refresh_websites = refresh_websites
MainWindow.add_site = add_site
MainWindow.edit_site = edit_site
MainWindow.remove_site = remove_site
MainWindow.import_from_csv = import_from_csv
MainWindow.export_to_csv = export_to_csv
MainWindow.show_settings = show_settings
MainWindow.show_about = show_about
MainWindow.update_table_times = update_table_times
MainWindow.on_checking_started = on_checking_started
MainWindow.on_website_checked = on_website_checked
MainWindow.on_website_error = on_website_error
MainWindow.on_checking_complete = on_checking_complete
# The apply_theme method is already defined in main_window.py

def emergency_save(self):
    """Save critical state during emergency shutdown."""
    try:
        from datetime import datetime
        
        # Try to gracefully terminate any running checks
        if hasattr(self, 'threaded_checker') and self.threaded_checker.is_running():
            self.threaded_checker.stop_check()
        
        # Export websites list if possible
        emergency_csv = "emergency_backup.csv"
        self.database.export_to_csv(emergency_csv)
        
        # Write a status file
        with open("webby_emergency.log", "w") as f:
            f.write(f"Emergency shutdown occurred at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Last status: {self.failure_label.text()}\n")
    except Exception as e:
        import logging
        logging.critical(f"Failed during emergency save: {str(e)}")