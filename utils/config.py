"""
Configuration handling
"""
import os
import json

# Default configuration
DEFAULT_CONFIG = {
    "theme": "light",
    "recent_files": [],
    "bookmarks": {},
    "plugins": [],
    "column_visibility": {
        "index": True,
        "time": True,
        "ecu": True,
        "app": True,
        "ctx": True,
        "level": True,
        "payload": True
    }
}

# Configuration file path
CONFIG_FILE = os.path.expanduser("~/.python_dlt_viewer.json")

def load_config():
    """Load configuration from file or create default"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                
            # Ensure all default keys exist
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
                    
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Return default config if file doesn't exist or has errors
    return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_setting(config, key, default=None):
    """Get a specific setting with default fallback"""
    keys = key.split('.')
    
    # Navigate through nested config
    current = config
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    
    return current

def update_setting(config, key, value):
    """Update a specific setting"""
    keys = key.split('.')
    
    # Navigate to the parent object
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # Set the value
    current[keys[-1]] = value