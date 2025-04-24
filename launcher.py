#!/usr/bin/env python3
# launcher.py
import os
import sys
import time
import subprocess
import logging
import signal
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='launcher.log',
    filemode='a'
)

class AppLauncher:
    def __init__(self, script_path="main.py"):
        self.script_path = script_path
        self.process = None
        self.restart_count = 0
        self.max_restarts = 5  # Maximum number of restarts in short succession
        self.restart_window = 300  # Time window in seconds for counting restarts
        self.restart_times = []
        self.running = True
        
    def start_app(self):
        """Start the application process."""
        try:
            logging.info(f"Starting application: {self.script_path}")
            # Use Python executable from current environment
            python_exec = sys.executable
            self.process = subprocess.Popen([python_exec, self.script_path])
            return True
        except Exception as e:
            logging.error(f"Failed to start application: {str(e)}")
            return False
    
    def monitor(self):
        """Monitor the application and restart if needed."""
        if not self.start_app():
            logging.critical("Could not start application, exiting launcher")
            return
        
        try:
            logging.info("Launcher monitoring started")
            
            while self.running:
                # Check if process is still running
                if self.process.poll() is not None:
                    exit_code = self.process.returncode
                    logging.warning(f"Application exited with code {exit_code}")
                    
                    # Record restart time
                    current_time = time.time()
                    self.restart_times.append(current_time)
                    
                    # Clean up old restart times outside the window
                    self.restart_times = [t for t in self.restart_times 
                                         if current_time - t <= self.restart_window]
                    
                    # Check if we're restarting too frequently
                    if len(self.restart_times) > self.max_restarts:
                        logging.critical(f"Too many restarts ({len(self.restart_times)}) "
                                       f"within {self.restart_window} seconds. Giving up.")
                        break
                    
                    # Wait before restart
                    restart_delay = min(30, 5 * len(self.restart_times))
                    logging.info(f"Waiting {restart_delay} seconds before restart")
                    time.sleep(restart_delay)
                    
                    # Restart application
                    if not self.start_app():
                        logging.critical("Failed to restart application, exiting launcher")
                        break
                    
                time.sleep(1)  # Sleep to prevent high CPU usage
                
        except KeyboardInterrupt:
            logging.info("Launcher received keyboard interrupt")
            self.cleanup()
        except Exception as e:
            logging.critical(f"Launcher error: {str(e)}")
            logging.critical(traceback.format_exc())
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources before exiting."""
        self.running = False
        if self.process and self.process.poll() is None:
            logging.info("Terminating application process")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logging.warning("Process did not terminate, forcing kill")
                self.process.kill()

def handle_signal(sig, frame):
    """Handle signals to gracefully shut down."""
    logging.info(f"Received signal {sig}")
    if launcher:
        launcher.cleanup()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    launcher = AppLauncher()
    launcher.monitor()