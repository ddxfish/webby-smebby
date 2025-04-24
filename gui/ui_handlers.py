from PyQt5.QtWidgets import QTableWidgetItem, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QTimer, QSize, Qt
from datetime import datetime

from gui.utils import format_time_since, get_short_status_code
from gui.threaded_checker import ThreadedChecker

def setup_timers(self):
    # Timer for updating the time display - runs every second
    self.time_timer = QTimer(self)
    self.time_timer.timeout.connect(self.update_time)
    self.time_timer.start(1000)  # Update every second
    
    # Timer for triggering website checks - runs according to config
    self.check_timer = QTimer(self)
    self.check_timer.timeout.connect(self.check_websites)
    self.check_timer.start(self.config.get('check_frequency') * 1000)
    
    # Timer for updating the table UI with fresh time values
    self.update_ui_timer = QTimer(self)
    self.update_ui_timer.timeout.connect(self.update_table_times)
    self.update_ui_timer.start(1000)  # Every 1000ms
    
    # Initialize threaded checker
    self.threaded_checker = ThreadedChecker(self.checker, self.config, self.database)
    
    # Connect signals
    self.threaded_checker.checkingStarted.connect(self.on_checking_started)
    self.threaded_checker.websiteChecked.connect(self.on_website_checked)
    self.threaded_checker.websiteError.connect(self.on_website_error)
    self.threaded_checker.checkingComplete.connect(self.on_checking_complete)

def update_time(self):
    current_time = datetime.now().strftime('%H:%M:%S')
    self.time_label.setText(current_time)
    
    # Use the current status method instead of get_last_failure
    current_status = self.database.get_current_status()
    if current_status:
        # Show info about the currently failing website
        if current_status.get('last_fail'):
            timestamp = datetime.strptime(current_status['last_fail'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
            failure_text = f"{timestamp} - {current_status['name']}: {get_short_status_code(current_status['status'], current_status['status_code'])}"
            self.failure_label.setText(failure_text)
        else:
            # Fallback if last_fail is not available
            failure_text = f"{current_status['name']}: {get_short_status_code(current_status['status'], current_status['status_code'])}"
            self.failure_label.setText(failure_text)
        
        # Update icons to red for failures
        status_icon_pixmap = QPixmap("assets/images/red.png")
        self.status_icon.setPixmap(status_icon_pixmap.scaled(16, 16, Qt.KeepAspectRatio))
        self.header_status_icon.setPixmap(status_icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio))
    else:
        self.failure_label.setText("Status: All Online")
        
        # Update icons to green for all online
        status_icon_pixmap = QPixmap("assets/images/green.png")
        self.status_icon.setPixmap(status_icon_pixmap.scaled(16, 16, Qt.KeepAspectRatio))
        self.header_status_icon.setPixmap(status_icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio))

def update_table_times(self):
    """Update just the time columns in the table without a database query"""
    if not self.websites_cache:
        return
    
    for row, website in enumerate(self.websites_cache):
        # Update Last Seen time
        last_seen = format_time_since(website.get('last_seen', ''))
        last_seen_item = QTableWidgetItem(last_seen)
        self.table.setItem(row, 3, last_seen_item)
        
        # Update Last Fail time
        last_fail = format_time_since(website.get('last_fail', ''))
        last_fail_item = QTableWidgetItem(last_fail)
        self.table.setItem(row, 4, last_fail_item)

def load_websites(self):
    """Load websites from database and update the table and cache"""
    websites = self.database.get_websites()
    self.websites_cache = websites  # Update the cache
    self.table.setRowCount(len(websites))
    
    for i, website in enumerate(websites):
        self.update_table_row(i, website)

def update_table_row(self, row, website):
    status_item = QTableWidgetItem()
    
    # Get 3-character status code
    short_status = get_short_status_code(website.get('status', ''), website.get('status_code', ''))
    
    if website.get('status') == 'OK':
        icon = QIcon("assets/images/green.png")
        status_item.setIcon(icon)
        status_text = short_status
    else:
        icon = QIcon("assets/images/red.png")
        status_item.setIcon(icon)
        status_text = short_status
    
    # Set larger icon size (24x24 instead of 16x16)
    self.table.setIconSize(QSize(24, 24))
    
    status_item.setText(status_text)
    self.table.setItem(row, 0, status_item)
    
    name_item = QTableWidgetItem(website.get('name', ''))
    self.table.setItem(row, 1, name_item)
    
    url_item = QTableWidgetItem(website.get('url', ''))
    self.table.setItem(row, 2, url_item)
    
    # Format time-since for Last Seen
    last_seen = format_time_since(website.get('last_seen', ''))
    last_seen_item = QTableWidgetItem(last_seen)
    self.table.setItem(row, 3, last_seen_item)
    
    # Format time-since for Last Fail
    last_fail = format_time_since(website.get('last_fail', ''))
    last_fail_item = QTableWidgetItem(last_fail)
    self.table.setItem(row, 4, last_fail_item)