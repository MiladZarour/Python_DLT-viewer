"""
DLT Message Decoder Plugin Base Class
"""

class DLTDecoderPlugin:
    """Base class for DLT message decoder plugins"""
    
    def __init__(self):
        self.name = "Base Decoder"
        self.description = "Base decoder plugin"
        self.version = "1.0"
        
    def can_decode(self, message):
        """Check if this plugin can decode the message"""
        return False
        
    def decode(self, message):
        """Decode the message payload"""
        return None
        
    def get_name(self):
        """Get plugin name"""
        return self.name
        
    def get_description(self):
        """Get plugin description"""
        return self.description
        
    def get_version(self):
        """Get plugin version"""
        return self.version