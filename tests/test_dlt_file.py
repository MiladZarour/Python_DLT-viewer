"""
Test DLT File Module
"""
import unittest
import os
import tempfile
from core.dlt_file import DLTFile

class TestDLTFile(unittest.TestCase):
    def setUp(self):
        # Create temporary test file
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.dlt")
        
        # Create sample DLT file with valid version 1 header
        with open(self.test_file, "wb") as f:
            f.write(b"DLT\1")  # Magic bytes
            f.write(b"\x01")   # Version 1
            f.write(b"\x00" * 8)  # Timestamp
            f.write(b"ECU1")   # ECU ID
            f.write(b"\x00" * 87)  # Remaining dummy content
            
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
        
    def test_init(self):
        """Test initialization"""
        dlt_file = DLTFile(self.test_file)
        self.assertEqual(dlt_file.file_path, self.test_file)
        self.assertTrue(os.path.exists(dlt_file.file_path))
        
    def test_parse_header(self):
        """Test header parsing"""
        dlt_file = DLTFile(self.test_file)
        dlt_file.parse_header()
        
        self.assertEqual(dlt_file.header_info["version"], 1)
        self.assertEqual(dlt_file.header_info["ecu_id"], "ECU1")
        
    def test_load_messages(self):
        """Test message loading"""
        dlt_file = DLTFile(self.test_file)
        dlt_file.parse_header()
        messages = dlt_file.load_messages(limit=10)
        
        self.assertIsInstance(messages, list)
        
    def test_invalid_file(self):
        """Test handling of invalid file"""
        invalid_file = os.path.join(self.temp_dir, "invalid.dlt")
        
        with self.assertRaises(FileNotFoundError):
            DLTFile(invalid_file)

if __name__ == '__main__':
    unittest.main()