import time
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem
from gui.dialogs import AddSiteDialog, SettingsDialog, AboutDialog

def check_websites(self):
    """Perform the actual website checks"""
    websites = self.database.get_websites()
    total_sites = len(websites)
    
    # Initialize counters
    dns_checks = 0
    ssl_checks = 0
    http_checks = 0
    
    # Time tracking
    start_time = time.time()
    
    # Store original methods
    original_check_dns = self.checker.check_dns
    original_check_ssl = self.checker.check_ssl
    original_check_http = self.checker.check_http
    
    # Create wrapped methods that count calls
    def wrapped_check_dns(hostname):
        nonlocal dns_checks
        dns_checks += 1
        return original_check_dns(hostname)
    
    def wrapped_check_ssl(hostname):
        nonlocal ssl_checks
        ssl_checks += 1
        return original_check_ssl(hostname)
    
    def wrapped_check_http(url):
        nonlocal http_checks
        http_checks += 1
        return original_check_http(url)
    
    # Replace with instrumented methods
    self.checker.check_dns = wrapped_check_dns
    self.checker.check_ssl = wrapped_check_ssl
    self.checker.check_http = wrapped_check_http
    
    try:
        # Perform the checks
        for i, website in enumerate(websites):
            status, status_code = self.checker.check_website(website)
            self.database.update_website_status(website['id'], status, status_code)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print debug information
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n--- Website Check Report ({timestamp}) ---")
        print(f"Total websites checked: {total_sites}")
        print(f"Network requests made:")
        print(f"  - DNS checks: {dns_checks}")
        print(f"  - SSL checks: {ssl_checks}")
        print(f"  - HTTP checks: {http_checks}")
        print(f"Total network requests: {dns_checks + ssl_checks + http_checks}")
        print(f"Check completed in {duration:.2f} seconds")
        print("---------------------------------------\n")
    finally:
        # Restore original methods
        self.checker.check_dns = original_check_dns
        self.checker.check_ssl = original_check_ssl
        self.checker.check_http = original_check_http
    
    # Reload the website data from database after checks
    self.load_websites()

def refresh_websites(self):
    """Manual refresh button handler"""
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

def edit_site(self):
    selected_rows = self.table.selectedIndexes()
    if selected_rows:
        row = selected_rows[0].row()
        website_id = self.websites_cache[row]['id']
        website = self.database.get_website(website_id)
        
        dialog = AddSiteDialog(self, website)
        if dialog.exec_():
            site_data = dialog.get_values()
            if site_data['name'] and site_data['url']:
                self.database.update_website(website_id, site_data['name'], site_data['url'], site_data['check_string'])
                self.load_websites()
                self.check_websites_signal.emit()
            else:
                QMessageBox.warning(self, "Invalid Input", "Name and URL are required.")
    else:
        QMessageBox.information(self, "Selection Required", "Please select a website to edit.")

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
        # Apply theme if settings were changed
        self.apply_theme()
        
        # Update timer with new frequency
        self.check_timer.setInterval(self.config.get('check_frequency') * 1000)
        self.check_websites_signal.emit()

def show_about(self):
    dialog = AboutDialog(self)
    dialog.exec_()