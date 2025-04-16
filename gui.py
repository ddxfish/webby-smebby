import sys
from datetime import datetime
import csv
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QLabel, QAction, 
                            QPushButton, QDialog, QLineEdit, QFormLayout, QStatusBar,
                            QMessageBox, QFileDialog)
from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

class AddSiteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Website")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.url_input = QLineEdit()
        self.string_input = QLineEdit()
        
        layout.addRow("Friendly Name:", self.name_input)
        layout.addRow("URL:", self.url_input)
        layout.addRow("String to Check:", self.string_input)
        
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addRow("", buttons_layout)
        self.setLayout(layout)
    
    def get_values(self):
        return {
            'name': self.name_input.text(),
            'url': self.url_input.text(),
            'check_string': self.string_input.text()
        }

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.frequency_input = QLineEdit(str(config.get('check_frequency')))
        layout.addRow("Check Frequency (seconds):", self.frequency_input)
        
        self.dns_check = QPushButton("On" if config.get('check_dns') else "Off")
        self.dns_check.clicked.connect(lambda: self.toggle_button(self.dns_check))
        layout.addRow("Check DNS:", self.dns_check)
        
        self.ssl_check = QPushButton("On" if config.get('check_ssl') else "Off")
        self.ssl_check.clicked.connect(lambda: self.toggle_button(self.ssl_check))
        layout.addRow("Check SSL:", self.ssl_check)
        
        self.http_check = QPushButton("On" if config.get('check_http') else "Off")
        self.http_check.clicked.connect(lambda: self.toggle_button(self.http_check))
        layout.addRow("Check HTTP:", self.http_check)
        
        self.string_check = QPushButton("On" if config.get('check_string') else "Off")
        self.string_check.clicked.connect(lambda: self.toggle_button(self.string_check))
        layout.addRow("Check String:", self.string_check)
        
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addRow("", buttons_layout)
        self.setLayout(layout)
    
    def toggle_button(self, button):
        if button.text() == "On":
            button.setText("Off")
        else:
            button.setText("On")
    
    def save_settings(self):
        try:
            frequency = int(self.frequency_input.text())
            if frequency < 1:
                raise ValueError("Frequency must be positive")
            
            self.config.set('check_frequency', frequency)
            self.config.set('check_dns', self.dns_check.text() == "On")
            self.config.set('check_ssl', self.ssl_check.text() == "On")
            self.config.set('check_http', self.http_check.text() == "On")
            self.config.set('check_string', self.string_check.text() == "On")
            
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Setting", str(e))

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        title = QLabel("Website Uptime Checker")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        description = QLabel("A simple application to monitor website uptime.")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    check_websites_signal = pyqtSignal()
    
    def __init__(self, config, database, checker):
        super().__init__()
        self.config = config
        self.database = database
        self.checker = checker
        
        self.setWindowTitle("Webby - Website Uptime Checker")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.setup_timers()
        self.load_websites()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        header_layout = QHBoxLayout()
        
        # Logo on left side
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/images/webby.png")
        logo_label.setPixmap(logo_pixmap.scaled(32, 32, Qt.KeepAspectRatio))
        
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
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        main_layout.addWidget(self.table)
        
        self.status_bar = QStatusBar()
        self.failure_label = QLabel("Status: All Online")
        self.time_label = QLabel()
        
        self.status_bar.addWidget(self.failure_label, 1)
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
        
        # Edit menu with Add/Remove Site
        edit_menu = menu_bar.addMenu("Edit")
        add_site_action = QAction("Add Site", self)
        add_site_action.triggered.connect(self.add_site)
        edit_menu.addAction(add_site_action)
        
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
    
    def setup_timers(self):
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # Update every second
        
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_websites_signal.emit)
        self.check_timer.start(self.config.get('check_frequency') * 1000)
        
        self.check_websites_signal.connect(self.check_websites)
    
    def update_time(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_label.setText(current_time)
        
        last_failure = self.database.get_last_failure()
        if last_failure:
            failure_text = f"{last_failure['name']} - {last_failure['status']}: {last_failure['status_code']} at {last_failure['timestamp']}"
            self.failure_label.setText(failure_text)
        else:
            self.failure_label.setText("Status: All Online")
    
    def load_websites(self):
        websites = self.database.get_websites()
        self.table.setRowCount(len(websites))
        
        for i, website in enumerate(websites):
            self.update_table_row(i, website)
    
    def update_table_row(self, row, website):
        status_item = QTableWidgetItem()
        
        if website.get('status') == 'OK':
            icon = QIcon("assets/images/green.png")
            status_text = f"{website.get('status_code', '')}"
        else:
            icon = QIcon("assets/images/red.png")
            status_text = f"{website.get('status', '')} {website.get('status_code', '')}"
        
        status_item.setIcon(icon)
        status_item.setText(status_text)
        self.table.setItem(row, 0, status_item)
        
        name_item = QTableWidgetItem(website.get('name', ''))
        self.table.setItem(row, 1, name_item)
        
        url_item = QTableWidgetItem(website.get('url', ''))
        self.table.setItem(row, 2, url_item)
        
        last_seen = website.get('last_seen', '')
        last_seen_item = QTableWidgetItem(last_seen)
        self.table.setItem(row, 3, last_seen_item)
        
        last_fail = website.get('last_fail', '')
        last_fail_item = QTableWidgetItem(last_fail)
        self.table.setItem(row, 4, last_fail_item)
    
    def check_websites(self):
        websites = self.database.get_websites()
        for i, website in enumerate(websites):
            status, status_code = self.checker.check_website(website)
            self.database.update_website_status(website['id'], status, status_code)
        
        self.load_websites()
    
    def refresh_websites(self):
        self.check_websites_signal.emit()
    
    def add_site(self):
        dialog = AddSiteDialog(self)
        if dialog.exec_():
            site_data = dialog.get_values()
            if site_data['name'] and site_data['url']:
                self.database.add_website(site_data['name'], site_data['url'], site_data['check_string'])
                self.load_websites()
                self.check_websites_signal.emit()
            else:
                QMessageBox.warning(self, "Invalid Input", "Name and URL are required.")
    
    def remove_site(self):
        selected_rows = self.table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            website_id = self.database.get_websites()[row]['id']
            
            reply = QMessageBox.question(self, "Confirm Removal", 
                                       "Are you sure you want to remove this website?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.database.remove_website(website_id)
                self.load_websites()
        else:
            QMessageBox.information(self, "Selection Required", "Please select a website to remove.")
    
    def import_from_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        
        if file_path:
            if self.database.import_from_csv(file_path):
                self.load_websites()
                self.check_websites_signal.emit()
                QMessageBox.information(self, "Import Successful", "Websites imported successfully.")
            else:
                QMessageBox.warning(self, "Import Failed", "Failed to import websites from CSV.")
    
    def export_to_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        
        if file_path:
            if self.database.export_to_csv(file_path):
                QMessageBox.information(self, "Export Successful", "Websites exported successfully.")
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to export websites to CSV.")
    
    def show_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_():
            self.check_timer.setInterval(self.config.get('check_frequency') * 1000)
            self.check_websites_signal.emit()
    
    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()