import sys
import os
from PyQt5.QtWidgets import QApplication

from config import Config
from database import Database
from checker import WebsiteChecker
from gui import MainWindow
import gui.methods
from gui.watchdog import UIWatchdog

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Webby")
    
    config = Config()
    db_file = config.get('db_file')
    csv_file = 'websites.csv'
    
    # Simple recovery logic:
    # If database doesn't exist but CSV does, we'll import after creating database
    csv_exists = os.path.exists(csv_file)
    db_exists = os.path.exists(db_file)
    should_import = False
    
    # Create a fresh database if needed
    if not db_exists and csv_exists:
        print(f"Database not found. Will recover from {csv_file}")
        should_import = True
    
    # Create database instance
    database = Database(db_file)
    
    # Import from CSV if we need to recover
    if should_import:
        if database.import_from_csv(csv_file):
            print("Recovery successful")
        else:
            print("Recovery failed")
    
    checker = WebsiteChecker(config)
    main_window = MainWindow(config, database, checker)
    
    # Initialize watchdog
    watchdog = UIWatchdog(main_window)
    main_window.ui_watchdog = watchdog
    watchdog.start_monitoring()
    
    # Load websites and show window
    main_window.show()
    main_window.load_websites()
    
    # Create backup if database is valid and no backup exists yet
    websites = database.get_websites()
    if websites and not csv_exists:
        database.export_to_csv(csv_file)
    
    # Start checking websites
    if websites:
        main_window.check_websites()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()