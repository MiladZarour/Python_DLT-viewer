"""
Test Utility Modules
"""
import unittest
import os
import tempfile
from utils.config import load_config, save_config, get_setting, update_setting
from utils.logger import setup_logger, get_logger

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
    def tearDown(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
        
    def test_load_save_config(self):
        """Test loading and saving configuration"""
        # Test loading default config
        config = load_config()
        self.assertIsInstance(config, dict)
        self.assertIn("theme", config)
        
        # Test saving and reloading
        config["test_setting"] = "test_value"
        save_config(config)
        
        reloaded = load_config()
        self.assertEqual(reloaded["test_setting"], "test_value")
        
    def test_get_setting(self):
        """Test getting settings"""
        config = {
            "section1": {
                "key1": "value1"
            }
        }
        
        value = get_setting(config, "section1.key1")
        self.assertEqual(value, "value1")
        
        # Test default value
        value = get_setting(config, "invalid.key", "default")
        self.assertEqual(value, "default")
        
    def test_update_setting(self):
        """Test updating settings"""
        config = {}
        update_setting(config, "section1.key1", "value1")
        
        self.assertEqual(config["section1"]["key1"], "value1")

class TestLogger(unittest.TestCase):
    def test_logger_setup(self):
        """Test logger setup"""
        logger = setup_logger()
        self.assertIsNotNone(logger)
        
        # Test singleton behavior
        logger2 = get_logger()
        self.assertEqual(logger, logger2)
        
    def test_logger_levels(self):
        """Test logger levels"""
        logger = get_logger()
        
        # Test different log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

if __name__ == '__main__':
    unittest.main()