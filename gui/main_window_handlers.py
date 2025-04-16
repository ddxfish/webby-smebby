from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QSize
from datetime import datetime, timedelta

from gui.dialogs import AddSiteDialog, SettingsDialog, AboutDialog

def format_time_since(timestamp_str):
    """Convert timestamp to human-readable time-since with max 2 significant numbers"""
    if not timestamp_str:
        return ""
    
    try:
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        delta = now - timestamp
        
        # Get total seconds
        total_seconds = delta.total_seconds()
        
        # Less than a minute
        if total_seconds < 60:
            return f"{int(total_seconds)}s"
        
        # Less than an hour
        if total_seconds < 3600:
            minutes = int(total_seconds / 60)
            seconds = int(total_seconds % 60)
            return f"{minutes}m {seconds}s"
        
        # Less than a day
        if total_seconds < 86400:
            hours = int(total_seconds / 3600)
            minutes = int((total_seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
        
        # Less than a month (30 days)
        if total_seconds < 2592000:
            days = int(total_seconds / 86400)
            hours = int((total_seconds % 86400) / 3600)
            return f"{days}d {hours}h"
        
        # Less than a year
        if total_seconds < 31536000:
            months = int(total_seconds / 2592000)
            days = int((total_seconds % 2592000) / 86400)
            return f"{months}mo {days}d"
        
        # More than a year
        years = int(total_seconds / 31536000)
        days = int((total_seconds % 31536000) / 86400)
        return f"{years}y {days}d"
    except:
        return timestamp_str

def get_short_status_code(status, status_code):
    """Convert status and status_code to a 3-character code"""
    # Handle None status
    if status is None:
        return 'UNK'  # Unknown status
    
    if status == 'OK':
        return status_code[:3] if status_code else '200'
    
    # Check that status is a string before calling string methods
    if isinstance(status, str):
        if status.startswith('DNS'):
            return 'DNS'
        
        if status.startswith('SSL'):
            return 'SSL'
        
        if status.startswith('HTTP'):
            return 'HTT'
        
        if status.startswith('String'):
            return 'STR'
        
        if status.startswith('Timeout'):
            return 'TMO'
        
        if status.startswith('Connection'):
            return 'CON'
    
    if status_code and len(status_code) <= 3:
        return status_code
    
    # Default case: take first 3 characters of status if it's a string
    if isinstance(status, str) and status:
        return status[:3].upper()
    
    return 'UNK'  # Default for any other case

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
        # More concise status line: timestamp, site name, failure type
        timestamp = datetime.strptime(last_failure['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
        failure_text = f"{timestamp} - {last_failure['name']}: {get_short_status_code(last_failure['status'], last_failure['status_code'])}"
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
    
    # Get 3-character status code
    short_status = get_short_status_code(website.get('status', ''), website.get('status_code', ''))
    
    if website.get('status') == 'OK':
        # 50% larger icon
        icon = QIcon("assets/images/green.png")
        status_item.setIcon(icon)
        status_text = short_status
    else:
        # 50% larger icon
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