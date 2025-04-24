import time
import logging
import sys
import os
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication
from datetime import datetime

class UIWatchdog(QObject):
    ui_frozen_signal = pyqtSignal()
    ping_signal = pyqtSignal()  # New signal for ping
    
    def __init__(self, main_window, threshold=10, check_interval=5000, ping_interval=2000):
        super().__init__()
        self.main_window = main_window
        self.threshold = threshold
        self.check_interval = check_interval
        self.ping_interval = ping_interval
        self.last_response_time = time.time()
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        
        # Connect signals
        self.ui_frozen_signal.connect(self.handle_frozen_ui)
        
        # Setup logging with rotation
        from logging.handlers import RotatingFileHandler
        log_handler = RotatingFileHandler(
            'webby_watchdog.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5  # Keep 5 backup files
        )
        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_formatter)
        
        logger = logging.getLogger('webby_watchdog')
        logger.setLevel(logging.INFO)
        logger.addHandler(log_handler)
        self.logger = logger
        
    def start_monitoring(self):
        """Start the UI monitoring process."""
        # Connect ping signal to pong response method
        self.ping_signal.connect(self.main_window.pong_response)
        
        # Set up timer to check UI responsiveness
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_ui_responsive)
        self.check_timer.start(self.check_interval)
        
        # Set up ping-pong mechanism
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self.ping_main_thread)
        self.ping_timer.start(self.ping_interval)
        
        logging.info("UI Watchdog started")
        
    def ping_main_thread(self):
        """Send a ping to the main thread."""
        # Emit the ping signal instead of invoking the method directly
        self.ping_signal.emit()
    
    def record_pong(self):
        """Record that a pong response was received."""
        self.last_response_time = time.time()
        self.recovery_attempts = 0  # Reset recovery attempts on successful pong
    
    def check_ui_responsive(self):
        """Check if the UI is responsive."""
        current_time = time.time()
        if current_time - self.last_response_time > self.threshold:
            # UI is potentially frozen
            logging.warning(f"UI appears to be frozen for {current_time - self.last_response_time:.2f} seconds")
            self.ui_frozen_signal.emit()
    
    def handle_frozen_ui(self):
        """Handle a frozen UI situation."""
        self.recovery_attempts += 1
        logging.warning(f"Attempting to recover UI (attempt {self.recovery_attempts}/{self.max_recovery_attempts})")
        
        try:
            # Try to process events to unstick the UI
            QApplication.processEvents()
            
            # Check if this helped
            if time.time() - self.last_response_time <= self.threshold:
                logging.info("UI recovered after processing events")
                return
                
            # If we're here, processing events didn't help
            if self.recovery_attempts >= self.max_recovery_attempts:
                logging.critical("UI failed to recover after maximum attempts, terminating application")
                # Save any necessary state before exit
                self.emergency_shutdown()
            else:
                # Wait for next check cycle
                logging.warning("Recovery attempt unsuccessful, will try again")
        except Exception as e:
            logging.error(f"Error during UI recovery attempt: {str(e)}")
            self.emergency_shutdown()
    
    def emergency_shutdown(self):
        """Perform emergency shutdown when UI cannot be recovered."""
        try:
            # Try to save state if possible
            if hasattr(self.main_window, "emergency_save"):
                self.main_window.emergency_save()
                
            # Log shutdown
            logging.critical("Performing emergency shutdown due to unrecoverable UI freeze")
            
            # Exit forcefully
            sys.exit(1)
        except Exception as e:
            logging.critical(f"Failed even during emergency shutdown: {str(e)}")
            # Force exit no matter what
            os._exit(1)