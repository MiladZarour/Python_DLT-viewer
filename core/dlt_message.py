"""
DLT Message Model - Data structure for DLT messages
"""
import time
import struct

class DLTMessage:
    """Class representing a single DLT (Diagnostic Log and Trace) message"""
    
    # DLT message types
    MSG_TYPE_LOG = 0
    MSG_TYPE_APP_TRACE = 1
    MSG_TYPE_NW_TRACE = 2
    MSG_TYPE_CONTROL = 3
    
    # Log levels
    LOG_FATAL = 1
    LOG_ERROR = 2
    LOG_WARN = 3
    LOG_INFO = 4
    LOG_DEBUG = 5
    LOG_VERBOSE = 6
    
    def __init__(self):
        """Initialize a new DLT message with default values"""
        # Standard DLT fields
        self.timestamp = time.time()  # Default to current time
        self.timestamp_us = 0         # Microseconds part of timestamp
        self.ecu_id = "UNK"           # ECU identifier
        self.app_id = "NOID"          # Application identifier
        self.ctx_id = "NOID"          # Context identifier
        self.session_id = None        # Session identifier (optional)
        self.log_level = "INFO"       # Log level
        self.msg_type = "LOG"         # Message type 
        self.msg_id = 0               # Message ID
        self.counter = 0              # Message counter
        self.length = 0               # Message length
        self.arg_count = 0            # Number of arguments
        
        # Payload
        self.payload = ""             # Text representation of payload
        self.raw_data = None          # Raw binary data
        self.parsed_payload = None    # Structured representation
        self.arguments = []           # List of parsed arguments
        
        # Additional fields for filtering and display
        self.is_visible = True        # Used for filtering in UI
        self.is_bookmarked = False    # Used for bookmarks feature
        
    def parse_from_bytes(self, data):
        """Parse message from binary data
        
        Args:
            data: Bytes object containing DLT message
            
        Returns:
            Number of bytes consumed, or 0 if parsing failed
        """
        if len(data) < 4:
            return 0
            
        try:
            # Parse standard header
            header = struct.unpack("<I", data[0:4])[0]
            
            # Extract header fields
            self.length = header & 0xFFFF
            self.msg_counter = (header >> 16) & 0xFF
            use_extended_header = (header >> 31) & 0x01
            
            if len(data) < self.length:
                return 0  # Not enough data
                
            # Parse extended header if present
            pos = 4
            if use_extended_header:
                if len(data) < pos + 10:
                    return 0  # Not enough data
                    
                # Parse MSIN (Message Info)
                msin = data[pos]
                self.msg_type = self._get_msg_type((msin >> 4) & 0x0F)
                self.log_level = self._get_log_level(msin & 0x0F)
                pos += 1
                
                # Parse app/context IDs
                self.app_id = data[pos:pos+4].decode('ascii', 'replace').strip('\0')
                pos += 4
                self.ctx_id = data[pos:pos+4].decode('ascii', 'replace').strip('\0')
                pos += 4
                
                # Parse argument count
                self.arg_count = data[pos]
                pos += 1
            
            # Store raw payload
            self.raw_data = data[0:self.length]
            payload_data = data[pos:self.length]
            
            # Parse payload based on type
            if self.msg_type == "LOG":
                self._parse_log_payload(payload_data)
            elif self.msg_type == "APP_TRACE":
                self._parse_trace_payload(payload_data)
            else:
                # Default to raw hex for unknown types
                self.payload = " ".join([f"{b:02x}" for b in payload_data])
            
            return self.length
            
        except Exception as e:
            print(f"Error parsing message: {e}")
            return 0
    
    def _parse_log_payload(self, data):
        """Parse LOG type payload"""
        try:
            # Try to decode as UTF-8 text
            self.payload = data.decode('utf-8', 'replace')
            self.arguments = [self.payload]
        except:
            # Fall back to hex representation
            self.payload = " ".join([f"{b:02x}" for b in data])
            self.arguments = [self.payload]
    
    def _parse_trace_payload(self, data):
        """Parse APP_TRACE type payload"""
        self.arguments = []
        pos = 0
        
        while pos < len(data) and len(self.arguments) < self.arg_count:
            if pos + 2 > len(data):
                break
                
            # Get type info
            type_info = struct.unpack("<H", data[pos:pos+2])[0]
            pos += 2
            
            # Parse based on type
            arg_type = type_info & 0x0F
            if arg_type == 1:  # String
                str_len = struct.unpack("<H", data[pos:pos+2])[0]
                pos += 2
                if pos + str_len <= len(data):
                    arg_val = data[pos:pos+str_len].decode('utf-8', 'replace')
                    self.arguments.append(arg_val)
                    pos += str_len
            elif arg_type == 2:  # Integer
                if pos + 4 <= len(data):
                    arg_val = struct.unpack("<i", data[pos:pos+4])[0]
                    self.arguments.append(str(arg_val))
                    pos += 4
            else:
                # Skip unknown types
                break
        
        # Combine arguments into payload string
        self.payload = " ".join(self.arguments)
    
    def _get_msg_type(self, type_code):
        """Convert message type code to string"""
        types = {
            self.MSG_TYPE_LOG: "LOG",
            self.MSG_TYPE_APP_TRACE: "APP_TRACE",
            self.MSG_TYPE_NW_TRACE: "NW_TRACE",
            self.MSG_TYPE_CONTROL: "CONTROL"
        }
        return types.get(type_code, "UNKNOWN")
    
    def _get_log_level(self, level_code):
        """Convert log level code to string"""
        levels = {
            self.LOG_FATAL: "FATAL",
            self.LOG_ERROR: "ERROR",
            self.LOG_WARN: "WARN",
            self.LOG_INFO: "INFO",
            self.LOG_DEBUG: "DEBUG",
            self.LOG_VERBOSE: "VERBOSE"
        }
        return levels.get(level_code, "UNKNOWN")
    
    def get_time_string(self):
        """Get formatted time string"""
        time_str = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        if self.timestamp_us:
            time_str += f".{self.timestamp_us:06d}"
        return time_str
    
    def get_summary(self):
        """Get a one-line summary of the message"""
        payload_preview = self.payload[:50]
        if len(self.payload) > 50:
            payload_preview += "..."
            
        return (f"[{self.get_time_string()}] {self.ecu_id}.{self.app_id}.{self.ctx_id} "
                f"[{self.log_level}]: {payload_preview}")
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp,
            "timestamp_us": self.timestamp_us,
            "ecu_id": self.ecu_id,
            "app_id": self.app_id,
            "ctx_id": self.ctx_id,
            "session_id": self.session_id,
            "log_level": self.log_level,
            "msg_type": self.msg_type,
            "msg_id": self.msg_id,
            "counter": self.counter,
            "length": self.length,
            "payload": self.payload,
            "is_bookmarked": self.is_bookmarked,
            "arguments": self.arguments
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create message from dictionary"""
        msg = cls()
        
        for key, value in data.items():
            if hasattr(msg, key):
                setattr(msg, key, value)
        
        return msg
    
    def __str__(self):
        """String representation of the message"""
        return self.get_summary()