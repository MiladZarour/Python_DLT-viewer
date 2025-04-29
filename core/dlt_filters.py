"""
DLT Message Filters
"""
import re
from datetime import datetime

class DLTFilter:
    """Filter for DLT messages"""
    
    def __init__(self):
        self.ecu_ids = set()
        self.app_ids = set()
        self.ctx_ids = set()
        self.log_levels = set()
        self.regex_pattern = None
        self.time_start = None
        self.time_end = None
        self.payload_text = None
        self.case_sensitive = False
        
    def set_ecu_filter(self, ecu_ids):
        """Set ECU ID filter"""
        self.ecu_ids = set(ecu_ids)
        
    def set_app_filter(self, app_ids):
        """Set Application ID filter"""
        self.app_ids = set(app_ids)
        
    def set_ctx_filter(self, ctx_ids):
        """Set Context ID filter"""
        self.ctx_ids = set(ctx_ids)
        
    def set_log_level_filter(self, levels):
        """Set log level filter"""
        self.log_levels = set(levels)
        
    def set_regex_filter(self, pattern, case_sensitive=False):
        """Set regex pattern filter"""
        if pattern:
            flags = 0 if case_sensitive else re.IGNORECASE
            self.regex_pattern = re.compile(pattern, flags)
        else:
            self.regex_pattern = None
            
    def set_time_range(self, start_time=None, end_time=None):
        """Set time range filter"""
        self.time_start = start_time
        self.time_end = end_time
        
    def set_payload_filter(self, text, case_sensitive=False):
        """Set payload text filter"""
        self.payload_text = text
        self.case_sensitive = case_sensitive
        
    def matches(self, message):
        """Check if message matches filter criteria"""
        # ECU ID filter
        if self.ecu_ids and message.ecu_id not in self.ecu_ids:
            return False
            
        # Application ID filter
        if self.app_ids and message.app_id not in self.app_ids:
            return False
            
        # Context ID filter
        if self.ctx_ids and message.ctx_id not in self.ctx_ids:
            return False
            
        # Log level filter
        if self.log_levels and message.log_level not in self.log_levels:
            return False
            
        # Time range filter
        if self.time_start and message.timestamp < self.time_start:
            return False
        if self.time_end and message.timestamp > self.time_end:
            return False
            
        # Payload text filter
        if self.payload_text:
            if self.case_sensitive:
                if self.payload_text not in message.payload:
                    return False
            else:
                if self.payload_text.lower() not in message.payload.lower():
                    return False
                    
        # Regex pattern filter
        if self.regex_pattern:
            if not self.regex_pattern.search(message.payload):
                return False
                
        return True