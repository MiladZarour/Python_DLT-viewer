"""
Message List View Component
"""
import tkinter as tk
from tkinter import ttk
import time

class MessageListView(ttk.Frame):
    """
    Component for displaying the list of DLT messages
    with virtual scrolling for performance
    """
    
    def __init__(self, parent, main_window):
        """Initialize the message list view"""
        super().__init__(parent)  # Initialize parent class
        
        self.parent = parent
        self.main_window = main_window
        self.messages = []
        self.filtered_indices = []
        self.virtual_event_callbacks = []
        
        # Create toolbar
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Search frame
        self.search_frame = ttk.Frame(self.toolbar)
        self.search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        
        search_label = ttk.Label(self.search_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Column visibility toggles
        self.column_frame = ttk.Frame(self.toolbar)
        self.column_frame.pack(side=tk.RIGHT)
        
        self.column_vars = {}
        columns = [("Index", "index"), ("Time", "time"), 
                  ("ECU", "ecu"), ("App", "app"), 
                  ("Context", "ctx"), ("Level", "level")]
        
        for label, col_id in columns:
            var = tk.BooleanVar(value=True)
            var.trace_add("write", lambda *args, c=col_id: self._toggle_column(c))
            self.column_vars[col_id] = var
            cb = ttk.Checkbutton(self.column_frame, text=label, variable=var)
            cb.pack(side=tk.LEFT, padx=5)
        
        # Create container frame with scrollbars
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for messages
        self.tree = ttk.Treeview(
            self.container,
            columns=("index", "time", "ecu", "app", "ctx", "level", "payload"),
            show="headings",
            selectmode="browse"
        )
        
        # Configure scrollbars
        vsb = ttk.Scrollbar(self.container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack widgets
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns
        self.tree.heading("index", text="#", command=lambda: self._sort_by("index", False))
        self.tree.heading("time", text="Time", command=lambda: self._sort_by("time", False))
        self.tree.heading("ecu", text="ECU", command=lambda: self._sort_by("ecu", False))
        self.tree.heading("app", text="App", command=lambda: self._sort_by("app", False))
        self.tree.heading("ctx", text="Context", command=lambda: self._sort_by("ctx", False))
        self.tree.heading("level", text="Level", command=lambda: self._sort_by("level", False))
        self.tree.heading("payload", text="Payload", command=lambda: self._sort_by("payload", False))
        
        self.tree.column("index", width=60, stretch=False)
        self.tree.column("time", width=150, stretch=False)
        self.tree.column("ecu", width=80, stretch=False)
        self.tree.column("app", width=80, stretch=False)
        self.tree.column("ctx", width=80, stretch=False)
        self.tree.column("level", width=80, stretch=False)
        self.tree.column("payload", width=500)
        
        # Configure selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        
        # Configure colors for different log levels
        self.level_colors = {
            "FATAL": "#FF0000",  # Red
            "ERROR": "#FF5555",  # Light red
            "WARN": "#FFAA00",   # Orange
            "INFO": "#000000",   # Default (black in light mode, white in dark)
            "DEBUG": "#555555",  # Gray
            "VERBOSE": "#AAAAAA" # Light gray
        }
        
        # Sorting state
        self.sort_column = "index"
        self.sort_reverse = False
    
    def bind_selection(self, callback):
        """Bind to message selection events"""
        self.virtual_event_callbacks.append(callback)
    
    def load_messages(self, messages):
        """Load messages into the view"""
        self.messages = messages
        self.filtered_indices = list(range(len(messages)))
        self._populate_tree()
    
    def apply_filter(self, filter_config):
        """Apply filters to the message view"""
        if not self.messages:
            return
            
        # Reset to show all messages
        if not filter_config:
            self.filtered_indices = list(range(len(self.messages)))
            self._populate_tree()
            return
            
        # Apply filters
        self.filtered_indices = []
        
        for i, msg in enumerate(self.messages):
            # Check if message passes all filters
            if self._message_matches_filter(msg, filter_config):
                self.filtered_indices.append(i)
        
        # Re-populate the tree with filtered messages
        self._populate_tree()
    
    def _message_matches_filter(self, msg, filter_config):
        """Check if a message matches the filter criteria"""
        # ECU ID filter
        if filter_config.get("ecu") and msg.ecu_id not in filter_config["ecu"]:
            return False
            
        # Application ID filter
        if filter_config.get("app_id") and msg.app_id not in filter_config["app_id"]:
            return False
            
        # Context ID filter
        if filter_config.get("ctx_id") and msg.ctx_id not in filter_config["ctx_id"]:
            return False
            
        # Log level filter
        if filter_config.get("log_level"):
            log_levels = filter_config["log_level"]
            if msg.log_level not in log_levels:
                return False
        
        # Time range filter
        if filter_config.get("time_start") and msg.timestamp < filter_config["time_start"]:
            return False
            
        if filter_config.get("time_end") and msg.timestamp > filter_config["time_end"]:
            return False
            
        # Payload content filter
        if filter_config.get("payload_text"):
            search_text = filter_config["payload_text"].lower()
            if search_text not in msg.payload.lower():
                return False
                
        return True
    
    def _populate_tree(self):
        """Populate the tree with messages"""
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Sort messages if needed
        if self.sort_column != "index" or self.sort_reverse:
            self._apply_sort()
            
        # Add filtered messages to the tree
        for i, idx in enumerate(self.filtered_indices):
            msg = self.messages[idx]
            
            # Format timestamp
            time_str = time.strftime("%H:%M:%S", time.localtime(msg.timestamp))
            if hasattr(msg, 'timestamp_us') and msg.timestamp_us:
                time_str += f".{msg.timestamp_us:06d}"
                
            # Format columns
            values = (
                idx,                # Original index
                time_str,           # Formatted time
                msg.ecu_id,         # ECU ID
                msg.app_id,         # Application ID
                msg.ctx_id,         # Context ID
                msg.log_level,      # Log level
                msg.payload[:100]   # First 100 chars of payload
            )
            
            # Insert with appropriate tag for coloring
            item_id = self.tree.insert("", "end", values=values, tags=(msg.log_level,))
            
            # Apply color based on log level
            if msg.log_level in self.level_colors:
                self.tree.tag_configure(msg.log_level, foreground=self.level_colors[msg.log_level])
    
    def get_visible_count(self):
        """Get the number of currently visible messages"""
        return len(self.filtered_indices)
    
    def _on_select(self, event):
        """Handle message selection in the tree"""
        selection = self.tree.selection()
        if not selection:
            return
            
        # Get the original message index from the tree item
        item = selection[0]
        values = self.tree.item(item, "values")
        msg_idx = int(values[0])
        
        # Get the selected message
        msg = self.messages[msg_idx]
        
        # Notify listeners
        for callback in self.virtual_event_callbacks:
            callback(msg)
    
    def _on_search_changed(self, *args):
        """Handle changes to the search text"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            # If search is cleared, restore previous filter state
            self.apply_filter(self.main_window.filter_panel.get_current_filter())
            return
            
        # Apply search filter
        visible_indices = []
        for idx in self.filtered_indices:
            msg = self.messages[idx]
            if search_text in msg.payload.lower() or search_text in msg.app_id.lower() or search_text in msg.ctx_id.lower():
                visible_indices.append(idx)
        
        # Update the filtered indices
        self.filtered_indices = visible_indices
        self._populate_tree()
        
        # Update message count
        self.main_window.update_message_count(
            len(self.messages), 
            self.get_visible_count()
        )
    
    def _toggle_column(self, column_id):
        """Toggle column visibility"""
        is_visible = self.column_vars[column_id].get()
        if is_visible:
            # Restore the column width
            if column_id == "index":
                self.tree.column(column_id, width=60, stretch=False)
            elif column_id == "time":
                self.tree.column(column_id, width=150, stretch=False)
            elif column_id in ["ecu", "app", "ctx", "level"]:
                self.tree.column(column_id, width=80, stretch=False)
            else:
                self.tree.column(column_id, width=500)
        else:
            # Hide the column by setting width to 0
            self.tree.column(column_id, width=0, stretch=False)
    
    def _sort_by(self, column, keep_reverse=True):
        """Sort the message list by the specified column"""
        # If clicking the same column, toggle sort direction
        if column == self.sort_column and keep_reverse:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            
        self.sort_column = column
        self._apply_sort()
        self._populate_tree()
    
    def _apply_sort(self):
        """Apply the current sort to the filtered indices"""
        if self.sort_column == "index":
            # Default order, no need to sort
            if not self.sort_reverse:
                self.filtered_indices.sort()
            else:
                self.filtered_indices.sort(reverse=True)
            return
        
        # Get the column index for sorting
        column_map = {
            "time": lambda idx: self.messages[idx].timestamp,
            "ecu": lambda idx: self.messages[idx].ecu_id,
            "app": lambda idx: self.messages[idx].app_id,
            "ctx": lambda idx: self.messages[idx].ctx_id,
            "level": lambda idx: self.messages[idx].log_level,
            "payload": lambda idx: self.messages[idx].payload
        }
        
        if self.sort_column in column_map:
            key_func = column_map[self.sort_column]
            self.filtered_indices.sort(key=key_func, reverse=self.sort_reverse)