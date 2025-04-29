"""
Test DLT ECU Module
"""
import unittest
import os
import tempfile
import json
from core.dlt_ecu import ECUConfig, ECUManager

class TestECUConfig(unittest.TestCase):
    def setUp(self):
        self.ecu = ECUConfig("TEST_ECU", description="Test ECU")
        
    def test_init(self):
        """Test initialization"""
        self.assertEqual(self.ecu.ecu_id, "TEST_ECU")
        self.assertEqual(self.ecu.description, "Test ECU")
        self.assertEqual(self.ecu.tcp_port, 3490)
        
    def test_add_app(self):
        """Test adding application"""
        self.ecu.add_app("APP1", "Test App")
        self.assertIn("APP1", self.ecu.app_ids)
        
    def test_to_dict(self):
        """Test conversion to dictionary"""
        data = self.ecu.to_dict()
        self.assertEqual(data["ecu_id"], "TEST_ECU")
        self.assertEqual(data["description"], "Test ECU")
        
    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {
            "ecu_id": "ECU1",
            "description": "Test ECU",
            "tcp_port": 3491
        }
        
        ecu = ECUConfig.from_dict(data)
        self.assertEqual(ecu.ecu_id, "ECU1")
        self.assertEqual(ecu.tcp_port, 3491)

class TestECUManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ECUManager(self.temp_dir)
        
    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)
        
    def test_add_ecu(self):
        """Test adding ECU configuration"""
        ecu = ECUConfig("ECU1")
        self.manager.add_ecu(ecu)
        
        self.assertIn("ECU1", self.manager.ecus)
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "ECU1.json")))
        
    def test_remove_ecu(self):
        """Test removing ECU configuration"""
        ecu = ECUConfig("ECU1")
        self.manager.add_ecu(ecu)
        self.manager.remove_ecu("ECU1")
        
        self.assertNotIn("ECU1", self.manager.ecus)
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, "ECU1.json")))

if __name__ == '__main__':
    unittest.main()