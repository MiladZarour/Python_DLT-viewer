"""
Marker/Bookmark View Component
"""
import tkinter as tk
from tkinter import ttk

class MarkerView(ttk.Frame):
    """Component for managing message markers/bookmarks"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent)
        
        # Create main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Marker list
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=("time", "description"),
            show="headings"
        )
        
        # Configure columns
        self.tree.heading("time", text="Time")
        self.tree.heading("description", text="Description")
        
        self.tree.column("time", width=100)
        self.tree.column("description", width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=(5,0))
        
        ttk.Button(toolbar, text="Add Marker", command=self._add_marker).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Remove", command=self._remove_marker).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Clear All", command=self._clear_markers).pack(side=tk.LEFT, padx=5)
        
        # Bind double-click to jump to message
        self.tree.bind("<Double-1>", self._on_marker_selected)
        
    def add_marker(self, message, description=""):
        """Add a marker for a message"""
        self.tree.insert(
            "",
            "end",
            values=(message.get_time_string(), description),
            tags=(str(id(message)),)
        )
        
    def _add_marker(self):
        """Add marker dialog"""
        # This would show a dialog to add a marker
        pass
        
    def _remove_marker(self):
        """Remove selected marker"""
        selection = self.tree.selection()
        if selection:
            self.tree.delete(selection[0])
            
    def _clear_markers(self):
        """Clear all markers"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
    def _on_marker_selected(self, event):
        """Handle marker selection"""
        # This would jump to the marked message
        pass