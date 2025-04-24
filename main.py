import sys
import os
import logging
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
    csv_file = 'websites.csv'  # Hardcode this for simplicity
    
    # Create database instance
    database = Database(db_file)
    
    # Verify database integrity first
    database_valid = database.verify_database()
    
    # Recovery path if database is invalid
    if not database_valid:
        print("Database corrupted or invalid")
        # If CSV exists, restore from it
        if os.path.exists(csv_file):
            print(f"Attempting recovery from {csv_file}")
            # Re-initialize database file (removing corrupted one)
            if os.path.exists(db_file):
                os.remove(db_file)
            database = Database(db_file)  # Create fresh database
            if database.import_from_csv(csv_file):
                print("Recovery successful")
    
    checker = WebsiteChecker(config)
    main_window = MainWindow(config, database, checker)
    
    # Initialize watchdog
    watchdog = UIWatchdog(main_window)
    main_window.ui_watchdog = watchdog
    watchdog.start_monitoring()
    
    # Create backup if database is valid and we don't have one
    websites = database.get_websites()
    if websites and not os.path.exists(csv_file):
        database.export_to_csv(csv_file)
    
    main_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()