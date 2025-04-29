"""
DLT ECU Configuration
"""
import json
import os

class ECUConfig:
    """Class for ECU configuration"""
    
    def __init__(self, ecu_id, description="", ip_address="", tcp_port=3490, 
                 verbose=True, timing=False, default_log_level="INFO"):
        self.ecu_id = ecu_id
        self.description = description
        self.ip_address = ip_address
        self.tcp_port = tcp_port
        self.verbose = verbose
        self.timing = timing
        self.default_log_level = default_log_level
        self.app_ids = {}  # Dictionary of configured application IDs
        
    def add_app(self, app_id, description="", contexts=None):
        """Add application configuration"""
        self.app_ids[app_id] = {
            "description": description,
            "contexts": contexts or {}
        }
        
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "ecu_id": self.ecu_id,
            "description": self.description,
            "ip_address": self.ip_address,
            "tcp_port": self.tcp_port,
            "verbose": self.verbose,
            "timing": self.timing,
            "default_log_level": self.default_log_level,
            "app_ids": self.app_ids
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        ecu = cls(
            data["ecu_id"],
            description=data.get("description", ""),
            ip_address=data.get("ip_address", ""),
            tcp_port=data.get("tcp_port", 3490),
            verbose=data.get("verbose", True),
            timing=data.get("timing", False),
            default_log_level=data.get("default_log_level", "INFO")
        )
        ecu.app_ids = data.get("app_ids", {})
        return ecu

class ECUManager:
    """Class for managing ECU configurations"""
    
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = os.path.expanduser("~/.python_dlt_viewer/ecus")
        self.config_dir = config_dir
        self.ecus = {}
        self.load_configs()
        
    def load_configs(self):
        """Load all ECU configurations"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            return
            
        for filename in os.listdir(self.config_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.config_dir, filename)) as f:
                        data = json.load(f)
                        ecu = ECUConfig.from_dict(data)
                        self.ecus[ecu.ecu_id] = ecu
                except Exception as e:
                    print(f"Error loading ECU config {filename}: {e}")
    
    def save_configs(self):
        """Save all ECU configurations"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        for ecu_id, ecu in self.ecus.items():
            filename = os.path.join(self.config_dir, f"{ecu_id}.json")
            try:
                with open(filename, 'w') as f:
                    json.dump(ecu.to_dict(), f, indent=2)
            except Exception as e:
                print(f"Error saving ECU config {filename}: {e}")
    
    def add_ecu(self, ecu):
        """Add or update ECU configuration"""
        self.ecus[ecu.ecu_id] = ecu
        self.save_configs()
        
    def remove_ecu(self, ecu_id):
        """Remove ECU configuration"""
        if ecu_id in self.ecus:
            del self.ecus[ecu_id]
            
            # Remove config file
            filename = os.path.join(self.config_dir, f"{ecu_id}.json")
            try:
                os.remove(filename)
            except:
                pass
                
    def get_ecu(self, ecu_id):
        """Get ECU configuration"""
        return self.ecus.get(ecu_id)