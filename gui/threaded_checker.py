import time
import threading
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class CheckerWorker(QObject):
    checkComplete = pyqtSignal(dict, str, str)  # website, status, status_code
    checkError = pyqtSignal(dict, str)  # website, error_message
    allChecksComplete = pyqtSignal(int, int, float)  # total_checks, successful_checks, duration
    
    def __init__(self, checker, config):
        super().__init__()
        self.checker = checker
        self.config = config
        self.is_running = False
        self.should_stop = False
    
    def check_website(self, website):
        if self.should_stop:
            return
        
        try:
            # Add a timeout mechanism
            status, status_code = "Error", "Timeout"
            
            # Create a separate thread for the actual check
            check_thread = threading.Thread(
                target=self._do_check, 
                args=(website,),
                daemon=True
            )
            check_thread.start()
            
            # Wait for the check thread to complete with timeout
            timeout = min(30, self.config.get('check_frequency') / 2)
            check_thread.join(timeout)
            
            if check_thread.is_alive():
                # Check timed out
                self.checkError.emit(website, "Checker timeout")
            elif hasattr(self, 'last_status') and hasattr(self, 'last_status_code'):
                # Check completed successfully
                self.checkComplete.emit(website, self.last_status, self.last_status_code)
        except Exception as e:
            # Handle any other errors
            self.checkError.emit(website, f"Error checking website: {str(e)}")
    
    def _do_check(self, website):
        try:
            status, status_code = self.checker.check_website(website)
            # Store the result to be picked up by the main method
            self.last_status = status
            self.last_status_code = status_code
        except Exception as e:
            # If any exception occurs, set error status
            self.last_status = "Error"
            self.last_status_code = str(e)
    
    def check_all_websites(self, websites):
        start_time = time.time()
        self.is_running = True
        self.should_stop = False
        
        total_checks = len(websites)
        successful_checks = 0
        
        for website in websites:
            if self.should_stop:
                break
                
            try:
                self.check_website(website)
                successful_checks += 1
            except Exception as e:
                print(f"Error checking website {website.get('name')}: {str(e)}")
        
        duration = time.time() - start_time
        self.is_running = False
        self.allChecksComplete.emit(total_checks, successful_checks, duration)
    
    def stop(self):
        self.should_stop = True

class ThreadedChecker(QObject):
    checkingStarted = pyqtSignal()
    checkingComplete = pyqtSignal(int, int, float)  # total, successful, duration
    websiteChecked = pyqtSignal(dict, str, str)  # website, status, status_code
    websiteError = pyqtSignal(dict, str)  # website, error
    
    def __init__(self, checker, config, database):
        super().__init__()
        self.checker = checker
        self.config = config
        self.database = database
        self.is_checking = False
        self.worker = None
        self.thread = None
    
    def start_check(self, websites=None):
        if self.is_checking:
            print("Check already in progress, skipping...")
            return False
        
        if websites is None:
            websites = self.database.get_websites()
        
        if not websites:
            return False
        
        self.is_checking = True
        self.checkingStarted.emit()
        
        # Create worker and thread
        self.worker = CheckerWorker(self.checker, self.config)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.worker.checkComplete.connect(self._on_website_checked)
        self.worker.checkError.connect(self._on_website_error)
        self.worker.allChecksComplete.connect(self._on_all_checks_complete)
        self.thread.started.connect(lambda: self.worker.check_all_websites(websites))
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start thread
        self.thread.start()
        return True
    
    def stop_check(self):
        if not self.is_checking or not self.worker:
            return
        
        self.worker.stop()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(5000)  # Wait up to 5 seconds
            if self.thread.isRunning():
                self.thread.terminate()
        
        self.is_checking = False
    
    def _on_website_checked(self, website, status, status_code):
        try:
            self.database.update_website_status(website['id'], status, status_code)
            self.websiteChecked.emit(website, status, status_code)
        except Exception as e:
            print(f"Error updating website status: {str(e)}")
    
    def _on_website_error(self, website, error):
        try:
            self.database.update_website_status(website['id'], "Error", error)
            self.websiteError.emit(website, error)
        except Exception as e:
            print(f"Error updating website error: {str(e)}")
    
    def _on_all_checks_complete(self, total, successful, duration):
        self.is_checking = False
        
        if self.thread:
            self.thread.quit()
            self.thread.wait(2000)
        
        self.checkingComplete.emit(total, successful, duration)
    
    def is_running(self):
        return self.is_checking