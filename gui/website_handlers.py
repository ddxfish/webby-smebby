import time
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem
from gui.dialogs import AddSiteDialog, SettingsDialog, AboutDialog

def check_websites(self):
    """Perform the actual website checks"""
    if hasattr(self, 'threaded_checker') and self.threaded_checker.is_running():
        print("Check already in progress, skipping...")
        return
    
    websites = self.database.get_websites()
    if not websites:
        return
    
    # Start a new check
    self.threaded_checker.start_check(websites)

def on_checking_started(self):
    """Handle the checking started signal"""
    self.checking_status_label.setText("Checking websites...")
    
def on_website_checked(self, website, status, status_code):
    """Handle individual website check completion"""
    # Find the row in the table for this website
    for row, cached_website in enumerate(self.websites_cache):
        if cached_website['id'] == website['id']:
            # Update the cache
            cached_website['status'] = status
            cached_website['status_code'] = status_code
            cached_website['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if status == 'OK':
                cached_website['last_seen'] = cached_website['last_check']
            else:
                cached_website['last_fail'] = cached_website['last_check']
            
            # Update the table row
            self.update_table_row(row, cached_website)
            break
    
    # Update status display
    self.update_time()

def on_website_error(self, website, error):
    """Handle website check errors"""
    # Similar to on_website_checked but for errors
    for row, cached_website in enumerate(self.websites_cache):
        if cached_website['id'] == website['id']:
            cached_website['status'] = "Error"
            cached_website['status_code'] = error
            cached_website['last_check'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cached_website['last_fail'] = cached_website['last_check']
            
            self.update_table_row(row, cached_website)
            break
    
    self.update_time()

def on_checking_complete(self, total, successful, duration):
    """Handle all checks complete signal"""
    self.checking_status_label.setText(f"Check completed: {successful}/{total} successful ({duration:.2f}s)")
    
    # Reload websites from the database to ensure consistency
    self.load_websites()

def refresh_websites(self):
    """Manual refresh button handler"""
    self.check_websites()

def add_site(self):
    dialog = AddSiteDialog(self)
    if dialog.exec_():
        site_data = dialog.get_values()
        if site_data['name'] and site_data['url']:
            self.database.add_website(site_data['name'], site_data['url'], site_data['check_string'])
            self.load_websites()
            self.check_websites()
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
                self.check_websites()
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
            self.check_websites()
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
        self.check_websites()

def show_about(self):
    dialog = AboutDialog(self)
    dialog.exec_()