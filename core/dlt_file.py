"""
DLT File Parser - Core module for handling DLT files
"""
import os
import struct
import time
from .dlt_message import DLTMessage

class DLTFile:
    """
    Class for parsing and handling DLT (Diagnostic Log and Trace) files
    """
    
    # DLT file header magic number (DLT\1)
    HEADER_MAGIC = b'DLT\1'
    
    def __init__(self, file_path):
        """Initialize with the file path"""
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.messages = []
        self.header_info = {}
        self.cached_indices = {}
        self.current_position = 0
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"DLT file not found: {file_path}")
    
    def parse_header(self):
        """Parse the DLT file header"""
        with open(self.file_path, 'rb') as f:
            # Read magic bytes
            magic = f.read(4)
            
            if magic == self.HEADER_MAGIC:
                # Standard DLT file with header
                version = struct.unpack("<B", f.read(1))[0]
                
                if version == 1:
                    # Parse version 1 header
                    self.header_info["version"] = version
                    self.header_info["timestamp"] = struct.unpack("<Q", f.read(8))[0]
                    self.header_info["ecu_id"] = f.read(4).decode('ascii').strip('\0')
                    
                    # Read other header information as needed
                    # ...
                    
                    # Set starting position for messages
                    self.current_position = f.tell()
                else:
                    # Unsupported version
                    raise ValueError(f"Unsupported DLT file version: {version}")
            else:
                # No header, assume raw DLT messages
                self.header_info["version"] = 0
                self.header_info["timestamp"] = int(time.time())
                self.header_info["ecu_id"] = "UNK"
                
                # Start from beginning
                self.current_position = 0
    
    def load_messages(self, offset=None, limit=None):
        """
        Load DLT messages from the file
        
        Args:
            offset: Starting index (or None for current position)
            limit: Maximum number of messages to load (or None for all)
        
        Returns:
            List of loaded DLT messages
        """
        if offset is not None:
            self.current_position = offset
        
        loaded_messages = []
        message_count = 0
        
        with open(self.file_path, 'rb') as f:
            f.seek(self.current_position)
            
            while f.tell() < self.file_size:
                # Check if we've loaded enough messages
                if limit is not None and message_count >= limit:
                    break
                
                # Remember position before reading message
                msg_start = f.tell()
                
                try:
                    # Parse a single DLT message
                    message = self._parse_message(f)
                    
                    if message:
                        # Store message position for later random access
                        self.cached_indices[len(self.messages) + len(loaded_messages)] = msg_start
                        
                        # Add to loaded messages
                        loaded_messages.append(message)
                        message_count += 1
                except Exception as e:
                    # Error parsing message, skip to next
                    # In a real implementation, we'd try to resync to the next valid message
                    print(f"Error parsing message at position {msg_start}: {str(e)}")
                    f.seek(msg_start + 1)  # Skip one byte and try again
            
            # Update current position
            self.current_position = f.tell()
        
        # Add loaded messages to the message list
        self.messages.extend(loaded_messages)
        
        return loaded_messages
    
    def _parse_message(self, file_handle):
        """
        Parse a single DLT message from the file
        
        Args:
            file_handle: Open file handle positioned at message start
        
        Returns:
            DLTMessage object or None if end of file
        """
        # Remember position
        start_pos = file_handle.tell()
        
        # Read standard header (4 bytes)
        header_bytes = file_handle.read(4)
        if len(header_bytes) < 4:
            return None  # End of file
        
        # Parse header fields
        header = struct.unpack("<I", header_bytes)[0]
        
        # Extract header information
        use_extended_header = (header >> 31) & 0x01
        message_counter = (header >> 16) & 0xFF
        length = header & 0xFFFF
        
        # Sanity check for message length
        if length < 4 or length > 65535:
            # Invalid length, try to resync
            raise ValueError(f"Invalid message length: {length}")
        
        # Read the rest of the message
        # Total length - 4 bytes we already read
        message_data = file_handle.read(length - 4)
        
        if len(message_data) < length - 4:
            # Incomplete message
            return None
        
        # Create basic message
        message = DLTMessage()
        message.length = length
        message.counter = message_counter
        
        # If using extended header, parse it
        if use_extended_header:
            if len(message_data) < 10:
                # Not enough data for extended header
                raise ValueError("Message too short for extended header")
            
            ext_header = struct.unpack("<BBBBHI", message_data[:10])
            
            # MSIN byte contains verbose/non-verbose and log level
            msin = ext_header[0]
            message.log_level = self._get_log_level(msin & 0x07)
            
            # ECU, app and context IDs
            message.ecu_id = self._get_id_string(message_data[1:5])
            message.app_id = self._get_id_string(message_data[5:9])
            message.ctx_id = self._get_id_string(message_data[9:13])
            
            # Session ID if available
            if len(message_data) >= 14:
                message.session_id = f"{message_data[13]:02x}"
            
            # Timestamp (from extended header or file time)
            if "timestamp" in self.header_info:
                message.timestamp = self.header_info["timestamp"]
            else:
                message.timestamp = time.time()
            
            # Extract payload
            payload_data = message_data[10:]
            message.payload = self._decode_payload(payload_data)
        else:
            # Standard header only
            message.log_level = "INFO"  # Default level
            message.ecu_id = self.header_info.get("ecu_id", "UNK")
            message.app_id = "NOID"
            message.ctx_id = "NOID"
            message.timestamp = time.time()
            
            # Extract payload
            message.payload = self._decode_payload(message_data)
        
        # Store raw data for hex view
        message.raw_data = header_bytes + message_data
        
        return message
    
    def _get_log_level(self, level_code):
        """Convert log level code to string"""
        log_levels = {
            0: "FATAL",
            1: "ERROR",
            2: "WARN",
            3: "INFO",
            4: "DEBUG",
            5: "VERBOSE",
            6: "VERBOSE2",
            7: "VERBOSE3"
        }
        return log_levels.get(level_code, "UNKNOWN")
    
    def _get_id_string(self, id_bytes):
        """Convert ID bytes to string, handling different formats"""
        # Try as ASCII string
        try:
            id_str = id_bytes.decode('ascii').strip('\0')
            if id_str:
                return id_str
        except:
            pass
        
        # Return as hex
        return "".join([f"{b:02x}" for b in id_bytes])
    
    def _decode_payload(self, payload_data):
        """Decode payload data to string representation"""
        # This is a simplified decoder
        # A real implementation would handle DLT message types and arguments
        
        # Try to decode as ASCII first
        try:
            payload = payload_data.decode('ascii', errors='replace')
            return payload
        except:
            pass
        
        # Fall back to hex representation
        return "".join([f"{b:02x}" for b in payload_data])
    
    def get_message(self, index):
        """Get message at specific index, loading if necessary"""
        if index < 0 or index >= len(self.messages):
            return None
        
        return self.messages[index]
    
    def get_message_range(self, start, end):
        """Get a range of messages, loading if necessary"""
        # Make sure indices are valid
        start = max(0, start)
        end = min(end, len(self.messages))
        
        return self.messages[start:end]