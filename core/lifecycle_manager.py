"""
DLT Connection Lifecycle Manager
"""
import threading
import time
from utils.logger import get_logger

class DLTLifecycleManager:
    """Manages DLT connection lifecycle and reconnection"""
    
    def __init__(self, connection):
        self.connection = connection
        self.logger = get_logger()
        self.auto_reconnect = True
        self.reconnect_interval = 5  # seconds
        self.max_retries = 3
        self.retry_count = 0
        self.monitor_thread = None
        self.stop_monitor = False
        
    def start(self):
        """Start connection monitoring"""
        self.stop_monitor = False
        self.monitor_thread = threading.Thread(target=self._monitor_connection)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop(self):
        """Stop connection monitoring"""
        self.stop_monitor = True
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def _monitor_connection(self):
        """Monitor connection and handle reconnection"""
        while not self.stop_monitor:
            if not self.connection.is_connected and self.auto_reconnect:
                if self.retry_count < self.max_retries:
                    self.logger.info("Connection lost, attempting reconnect...")
                    if self.connection.connect():
                        self.logger.info("Reconnection successful")
                        self.retry_count = 0
                    else:
                        self.retry_count += 1
                        self.logger.warning(
                            f"Reconnection failed, attempt {self.retry_count}/{self.max_retries}"
                        )
                else:
                    self.logger.error("Max reconnection attempts reached")
                    self.stop_monitor = True
                    
            time.sleep(self.reconnect_interval)
            
    def reset_retries(self):
        """Reset the retry counter"""
        self.retry_count = 0