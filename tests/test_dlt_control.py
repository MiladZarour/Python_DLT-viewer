"""
Test DLT Control Module
"""
import unittest
from core.dlt_control import DLTControlMessage, DLTControlMessageType

class TestDLTControl(unittest.TestCase):
    def setUp(self):
        self.message = DLTControlMessage(DLTControlMessageType.GET_LOG_INFO)
        
    def test_encode(self):
        """Test message encoding"""
        data = self.message.encode()
        self.assertIsInstance(data, bytes)
        self.assertEqual(len(data), 8)  # Header size
        
    def test_decode(self):
        """Test message decoding"""
        # Create sample control message
        original = DLTControlMessage(DLTControlMessageType.GET_SOFTWARE_VERSION)
        encoded = original.encode()
        
        # Decode and verify
        decoded = DLTControlMessage.decode(encoded)
        self.assertEqual(decoded.service_id, original.service_id)
        
    def test_response(self):
        """Test response message creation"""
        response = self.message.get_response()
        self.assertEqual(response.service_id, self.message.service_id | 0x1000)

if __name__ == '__main__':
    unittest.main()