from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from datetime import datetime

from gui.dialogs import AddSiteDialog, SettingsDialog, AboutDialog

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