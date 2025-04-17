# This file adds the methods from main_window_handlers.py to the MainWindow class

from gui.main_window import MainWindow
from gui.main_window_handlers import (
    setup_timers, update_time, load_websites, update_table_row, 
    check_websites, refresh_websites, add_site, remove_site,
    import_from_csv, export_to_csv, show_settings, show_about,
    update_table_times
)

# Add all the handler methods to the MainWindow class
MainWindow.setup_timers = setup_timers
MainWindow.update_time = update_time
MainWindow.load_websites = load_websites
MainWindow.update_table_row = update_table_row
MainWindow.check_websites = check_websites
MainWindow.refresh_websites = refresh_websites
MainWindow.add_site = add_site
MainWindow.remove_site = remove_site
MainWindow.import_from_csv = import_from_csv
MainWindow.export_to_csv = export_to_csv
MainWindow.show_settings = show_settings
MainWindow.show_about = show_about
MainWindow.update_table_times = update_table_times
# The apply_theme method is already defined in main_window.py