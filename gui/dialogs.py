from PyQt5.QtWidgets import (QDialog, QLineEdit, QFormLayout, QHBoxLayout, 
                           QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt

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
        
        # Add dark mode toggle
        self.dark_mode = QPushButton("On" if config.get('dark_mode') else "Off")
        self.dark_mode.clicked.connect(lambda: self.toggle_button(self.dark_mode))
        layout.addRow("Dark Mode:", self.dark_mode)
        
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
            self.config.set('dark_mode', self.dark_mode.text() == "On")
            
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Setting", str(e))

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setMinimumWidth(300)
        
        layout = QHBoxLayout()
        
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