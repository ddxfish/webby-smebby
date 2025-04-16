import sys
import os
from PyQt5.QtWidgets import QApplication

from config import Config
from database import Database
from checker import WebsiteChecker
from gui import MainWindow  # Import from the gui module
import gui.methods  # Import to add methods to MainWindow class

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Webby")
    
    config = Config()
    database = Database(config.get('db_file'))
    checker = WebsiteChecker(config)
    
    main_window = MainWindow(config, database, checker)
    main_window.show()
    
    if os.path.exists(config.get('csv_file')) and not database.get_websites():
        database.import_from_csv(config.get('csv_file'))
        main_window.load_websites()
        main_window.check_websites()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()