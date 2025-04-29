"""
DLT Control Message Support
"""
import struct
from enum import IntEnum

class DLTControlMessageType(IntEnum):
    """DLT Control Message Types"""
    GET_LOG_INFO = 0x03
    GET_DEFAULT_LOG_LEVEL = 0x04
    SET_DEFAULT_LOG_LEVEL = 0x05
    GET_SOFTWARE_VERSION = 0x13
    GET_LOCAL_TIME = 0x0F
    SET_VERBOSE_MODE = 0x09
    SET_TIMING_PACKETS = 0x0B
    GET_TRACE_STATUS = 0x0C
    SET_TRACE_STATUS = 0x0D

class DLTControlMessage:
    """Class for handling DLT Control Messages"""
    
    def __init__(self, service_id, status=0):
        self.service_id = service_id
        self.status = status
        self.payload = b""
        
    def encode(self):
        """Encode control message to bytes"""
        header = struct.pack("<II", self.service_id, self.status)
        return header + self.payload
        
    @classmethod
    def decode(cls, data):
        """Decode control message from bytes"""
        if len(data) < 8:
            return None
            
        service_id, status = struct.unpack("<II", data[:8])
        msg = cls(service_id, status)
        msg.payload = data[8:]
        return msg
        
    def get_response(self):
        """Create response message"""
        return DLTControlMessage(self.service_id | 0x1000, self.status)