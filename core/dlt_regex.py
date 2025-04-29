"""
DLT Regular Expression Support
"""
import re
from datetime import datetime

class DLTRegexMatcher:
    """Regular expression matching for DLT messages"""
    
    def __init__(self):
        self.patterns = {}
        
    def add_pattern(self, name, pattern, flags=0):
        """Add a regex pattern"""
        try:
            self.patterns[name] = re.compile(pattern, flags)
            return True
        except re.error:
            return False
            
    def remove_pattern(self, name):
        """Remove a regex pattern"""
        if name in self.patterns:
            del self.patterns[name]
            
    def match_message(self, message):
        """Match message against all patterns"""
        results = {}
        for name, pattern in self.patterns.items():
            match = pattern.search(message.payload)
            if match:
                results[name] = match.groups()
        return results
        
    def find_all(self, message):
        """Find all matches in message"""
        results = {}
        for name, pattern in self.patterns.items():
            results[name] = pattern.findall(message.payload)
        return results