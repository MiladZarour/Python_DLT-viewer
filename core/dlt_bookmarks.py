"""
DLT Bookmark Manager
"""
import json
import os
from datetime import datetime

class DLTBookmark:
    """Class representing a DLT message bookmark"""
    
    def __init__(self, message, description=""):
        self.timestamp = message.timestamp
        self.ecu_id = message.ecu_id
        self.app_id = message.app_id
        self.ctx_id = message.ctx_id
        self.description = description
        self.created_at = datetime.now()
        
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "ecu_id": self.ecu_id,
            "app_id": self.app_id,
            "ctx_id": self.ctx_id,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        bookmark = cls.__new__(cls)
        bookmark.timestamp = data["timestamp"]
        bookmark.ecu_id = data["ecu_id"]
        bookmark.app_id = data["app_id"]
        bookmark.ctx_id = data["ctx_id"]
        bookmark.description = data["description"]
        bookmark.created_at = datetime.fromisoformat(data["created_at"])
        return bookmark

class DLTBookmarkManager:
    """Manager for DLT message bookmarks"""
    
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = os.path.expanduser("~/.python_dlt_viewer")
        self.config_dir = config_dir
        self.bookmarks_file = os.path.join(config_dir, "bookmarks.json")
        self.bookmarks = []
        self.load_bookmarks()
        
    def add_bookmark(self, message, description=""):
        """Add a new bookmark"""
        bookmark = DLTBookmark(message, description)
        self.bookmarks.append(bookmark)
        self.save_bookmarks()
        return bookmark
        
    def remove_bookmark(self, bookmark):
        """Remove a bookmark"""
        if bookmark in self.bookmarks:
            self.bookmarks.remove(bookmark)
            self.save_bookmarks()
            
    def clear_bookmarks(self):
        """Clear all bookmarks"""
        self.bookmarks.clear()
        self.save_bookmarks()
        
    def load_bookmarks(self):
        """Load bookmarks from file"""
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r') as f:
                    data = json.load(f)
                    self.bookmarks = [DLTBookmark.from_dict(b) for b in data]
            except Exception as e:
                print(f"Error loading bookmarks: {e}")
                
    def save_bookmarks(self):
        """Save bookmarks to file"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.bookmarks_file, 'w') as f:
                json.dump([b.to_dict() for b in self.bookmarks], f, indent=2)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")
            
    def get_bookmarks(self):
        """Get all bookmarks"""
        return self.bookmarks.copy()