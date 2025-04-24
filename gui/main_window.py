import sys
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QLabel, QAction, QStatusBar)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from gui.dialogs import AddSiteDialog, SettingsDialog, AboutDialog
from gui.styles import LIGHT_STYLE, DARK_STYLE

class MainWindow(QMainWindow):
    check_websites_signal = pyqtSignal()
    
    def __init__(self, config, database, checker):
        super().__init__()
        self.config = config
        self.database = database
        self.checker = checker
        
        # Add cache for website data
        self.websites_cache = []
        
        self.setWindowTitle("Webby - Website Uptime Checker")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.apply_theme()  # Apply theme based on config
        self.setup_timers()
        self.load_websites()
    
    def apply_theme(self):
        """Apply light or dark theme based on config setting"""
        if self.config.get('dark_mode'):
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        header_layout = QHBoxLayout()
        
        # Status icon on far left - matches status bar icon
        self.header_status_icon = QLabel()
        status_icon_pixmap = QPixmap("assets/images/green.png")
        self.header_status_icon.setPixmap(status_icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio))
        header_layout.addWidget(self.header_status_icon)
        
        # Add small spacing between status icon and logo
        header_layout.addSpacing(5)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/images/webby.png")
        logo_label.setPixmap(logo_pixmap.scaled(48, 48, Qt.KeepAspectRatio))
        
        # App name to right of logo
        app_title = QLabel("Webby")
        app_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(app_title)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Status", "Name", "URL", "Last Seen", "Last Fail"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Add padding to Name column cells
        self.table.setStyleSheet("QTableView::item { padding-right: 15px; }")
        
        # Hide row numbers
        self.table.verticalHeader().setVisible(False)
        
        # Enable alternating row colors for better readability
        self.table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.table)
        
        self.status_bar = QStatusBar()
        
        # Add spacing before status icon
        spacer_label = QLabel()
        spacer_label.setFixedWidth(5)
        self.status_bar.addWidget(spacer_label)
        
        # Add status icon to status bar
        self.status_icon = QLabel()
        status_icon_pixmap = QPixmap("assets/images/green.png")
        self.status_icon.setPixmap(status_icon_pixmap.scaled(16, 16, Qt.KeepAspectRatio))
        self.status_bar.addWidget(self.status_icon)
        
        self.failure_label = QLabel("Status: All Online")
        self.time_label = QLabel()
        
        # Add checking status label
        self.checking_status_label = QLabel("")
        
        self.status_bar.addWidget(self.failure_label, 1)
        self.status_bar.addWidget(self.checking_status_label)
        self.status_bar.addPermanentWidget(self.time_label)
        
        self.setStatusBar(self.status_bar)
        
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu with Import/Export CSV and Exit
        file_menu = menu_bar.addMenu("File")
        
        import_csv_action = QAction("Import from CSV", self)
        import_csv_action.triggered.connect(self.import_from_csv)
        file_menu.addAction(import_csv_action)
        
        export_csv_action = QAction("Export to CSV", self)
        export_csv_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_csv_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(sys.exit)
        file_menu.addAction(exit_action)
        
        # Edit menu with Add/Remove/Edit Site
        edit_menu = menu_bar.addMenu("Edit")
        add_site_action = QAction("Add Site", self)
        add_site_action.triggered.connect(self.add_site)
        edit_menu.addAction(add_site_action)
        
        edit_site_action = QAction("Edit Site", self)
        edit_site_action.triggered.connect(self.edit_site)
        edit_menu.addAction(edit_site_action)
        
        remove_site_action = QAction("Remove Site", self)
        remove_site_action.triggered.connect(self.remove_site)
        edit_menu.addAction(remove_site_action)
        
        view_menu = menu_bar.addMenu("View")
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_websites)
        view_menu.addAction(refresh_action)
        
        settings_menu = menu_bar.addMenu("Settings")
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)
        
        about_menu = menu_bar.addMenu("About")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)