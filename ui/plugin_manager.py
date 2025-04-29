"""
Plugin Manager - Support for DLT message decoder plugins
"""
import os
import sys
import importlib
import inspect

class PluginManager:
    """Manager for DLT decoder plugins"""
    
    def __init__(self, plugin_dir=None):
        if plugin_dir is None:
            plugin_dir = os.path.expanduser("~/.python_dlt_viewer/plugins")
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self.load_plugins()
        
    def load_plugins(self):
        """Load all plugins from the plugin directory"""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return
            
        # Add plugin directory to Python path
        if self.plugin_dir not in sys.path:
            sys.path.append(self.plugin_dir)
            
        # Load each .py file as a potential plugin
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py"):
                try:
                    module_name = filename[:-3]
                    module = importlib.import_module(module_name)
                    
                    # Look for plugin classes
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            hasattr(obj, "decode_message") and
                            hasattr(obj, "plugin_name")):
                            # Valid plugin found
                            plugin = obj()
                            self.plugins[plugin.plugin_name] = plugin
                except Exception as e:
                    print(f"Error loading plugin {filename}: {e}")
                    
    def decode_message(self, message):
        """Try to decode a message using available plugins"""
        for plugin in self.plugins.values():
            try:
                if plugin.can_decode(message):
                    decoded = plugin.decode_message(message)
                    if decoded:
                        message.parsed_payload = decoded
                        return True
            except Exception as e:
                print(f"Plugin {plugin.plugin_name} error: {e}")
                
        return False