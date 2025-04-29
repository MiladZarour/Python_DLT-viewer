"""
Test DLT Message Module
"""
import unittest
import time
from core.dlt_message import DLTMessage

class TestDLTMessage(unittest.TestCase):
    def setUp(self):
        self.message = DLTMessage()
        
    def test_init_defaults(self):
        """Test default initialization"""
        self.assertEqual(self.message.ecu_id, "UNK")
        self.assertEqual(self.message.app_id, "NOID")
        self.assertEqual(self.message.ctx_id, "NOID")
        self.assertEqual(self.message.log_level, "INFO")
        self.assertEqual(self.message.msg_type, "LOG")
        
    def test_time_string_format(self):
        """Test time string formatting"""
        self.message.timestamp = 1609459200  # 2021-01-01 00:00:00
        self.message.timestamp_us = 123456
        time_str = self.message.get_time_string()
        self.assertRegex(time_str, r"\d{2}:\d{2}:\d{2}\.\d{6}")
        
    def test_parse_from_bytes(self):
        """Test parsing from binary data"""
        # Create valid DLT message with standard header
        header = (1 << 31) | (1 << 16) | 24  # Extended header, counter=1, length=24
        header_bytes = header.to_bytes(4, byteorder='little')
        
        # Extended header
        ext_header = bytes([
            0x02,           # MSIN (log level INFO)
            0x41, 0x50, 0x50, 0x31,  # APP1
            0x43, 0x54, 0x58, 0x31,  # CTX1
            0x01            # 1 argument
        ])
        
        # Payload
        payload = b"Test message"
        
        data = header_bytes + ext_header + payload
        
        bytes_used = self.message.parse_from_bytes(data)
        self.assertTrue(bytes_used > 0)
        self.assertEqual(self.message.app_id, "APP1")
        self.assertEqual(self.message.ctx_id, "CTX1")
        
    def test_to_dict(self):
        """Test conversion to dictionary"""
        self.message.ecu_id = "TEST"
        self.message.payload = "Test message"
        
        data = self.message.to_dict()
        self.assertEqual(data["ecu_id"], "TEST")
        self.assertEqual(data["payload"], "Test message")
        
    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            "ecu_id": "TEST",
            "app_id": "APP1",
            "ctx_id": "CTX1",
            "payload": "Test message"
        }
        
        message = DLTMessage.from_dict(data)
        self.assertEqual(message.ecu_id, "TEST")
        self.assertEqual(message.app_id, "APP1")
        self.assertEqual(message.payload, "Test message")

if __name__ == '__main__':
    unittest.main()