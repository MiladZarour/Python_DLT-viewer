"""
DLT Network Connection - Module for TCP/IP connections to DLT devices
"""
import socket
import threading
import time
import os
from datetime import datetime
from .dlt_message import DLTMessage

class DLTConnection:
    """Class for handling TCP/IP connections to DLT devices"""
    
    def __init__(self, host="localhost", port=3490):
        """Initialize connection parameters"""
        self.host = host
        self.port = port
        self.socket = None
        self.is_connected = False
        self.receive_thread = None
        self.stop_thread = False
        self.callbacks = []
        self.log_file = None
        self.log_dir = os.path.expanduser("~/dlt_logs")
        
    def connect(self):
        """Establish connection to DLT device"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            
            # Start receive thread
            self.stop_thread = False
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            # Start new log file
            self._start_new_log()
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close connection to DLT device"""
        self.stop_thread = True
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.is_connected = False
        
        # Close current log file
        if self.log_file:
            self.log_file.close()
            self.log_file = None
        
    def _receive_loop(self):
        """Background thread for receiving messages"""
        buffer = bytearray()
        
        while not self.stop_thread:
            try:
                # Read data
                data = self.socket.recv(4096)
                if not data:
                    break
                    
                buffer.extend(data)
                
                # Process complete messages
                while len(buffer) >= 4:  # Minimum message size
                    # Try to parse message
                    msg = DLTMessage()
                    bytes_used = msg.parse_from_bytes(buffer)
                    
                    if bytes_used > 0:
                        # Valid message found
                        buffer = buffer[bytes_used:]
                        
                        # Save to log file
                        if self.log_file and msg.raw_data:
                            try:
                                self.log_file.write(msg.raw_data)
                                self.log_file.flush()
                            except Exception as e:
                                print(f"Error writing to log file: {e}")
                        
                        # Notify listeners
                        for callback in self.callbacks:
                            callback(msg)
                    else:
                        # Invalid or incomplete message
                        break
                        
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
        
        self.is_connected = False
        
        # Close log file on disconnect
        if self.log_file:
            self.log_file.close()
            self.log_file = None
    
    def add_callback(self, callback):
        """Add callback for received messages"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback):
        """Remove message callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            
    def clear_log(self):
        """Clear current log and start a new one"""
        if self.log_file:
            self.log_file.close()
            self.log_file = None
            
        if self.is_connected:
            self._start_new_log()
            
    def _start_new_log(self):
        """Start a new log file with timestamp"""
        try:
            # Create logs directory if needed
            os.makedirs(self.log_dir, exist_ok=True)
            
            # Create filename with timestamp including milliseconds
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"DLT_LOG_{timestamp}.dlt"
            filepath = os.path.join(self.log_dir, filename)
            
            # Open new log file
            self.log_file = open(filepath, 'wb')
            
            # Write DLT file header
            self.log_file.write(b'DLT\1')  # Magic + version
            
            print(f"Started new log file: {filepath}")
            return True
            
        except Exception as e:
            print(f"Error creating log file: {e}")
            self.log_file = None
            return False