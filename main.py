import sys
import os
import logging
from PyQt5.QtWidgets import QApplication

from config import Config
from database import Database
from checker import WebsiteChecker
from gui import MainWindow  # Import from the gui module
import gui.methods  # Import to add methods to MainWindow class
from gui.watchdog import UIWatchdog  # Import our new watchdog

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Webby")
    
    config = Config()
    database = Database(config.get('db_file'))
    checker = WebsiteChecker(config)
    
    main_window = MainWindow(config, database, checker)
    
    # Initialize and start the UI watchdog
    watchdog = UIWatchdog(main_window)
    main_window.ui_watchdog = watchdog  # Store reference in main window
    watchdog.start_monitoring()
    
    main_window.show()
    
    if os.path.exists(config.get('csv_file')) and not database.get_websites():
        database.import_from_csv(config.get('csv_file'))
        main_window.load_websites()
        main_window.check_websites()
    
    sys.exit(app.exec_())
    
    database = Database(config.get('db_file'))
    
    # Add database recovery mechanism
    if os.path.exists('websites.csv'):
        websites = database.get_websites()
        if not websites or os.path.getsize(config.get('db_file')) == 0:
            print("Database empty or corrupted, restoring from backup...")
            database.import_from_csv('websites.csv')
            print("Restore complete")

if __name__ == "__main__":
    main()