"""
Statistics View Component
"""
import tkinter as tk
from tkinter import ttk
import time

class StatisticsView(ttk.Frame):
    """Component for displaying DLT statistics"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent)
        
        # Create main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Statistics tree
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=("value"),
            show="tree headings"
        )
        
        # Configure columns
        self.tree.heading("value", text="Value")
        self.tree.column("#0", width=200)
        self.tree.column("value", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize statistics
        self.stats = {
            "total_messages": 0,
            "start_time": time.time(),
            "bytes_received": 0,
            "msg_per_second": 0.0,
            "bytes_per_second": 0.0,
            "by_level": {},
            "by_ecu": {},
            "by_app": {},
            "by_ctx": {}
        }
        
        self._update_tree()
        
    def update_stats(self, message):
        """Update statistics with new message"""
        self.stats["total_messages"] += 1
        self.stats["bytes_received"] += len(message.raw_data) if message.raw_data else 0
        
        # Update counts by category
        self.stats["by_level"][message.log_level] = self.stats["by_level"].get(message.log_level, 0) + 1
        self.stats["by_ecu"][message.ecu_id] = self.stats["by_ecu"].get(message.ecu_id, 0) + 1
        self.stats["by_app"][message.app_id] = self.stats["by_app"].get(message.app_id, 0) + 1
        self.stats["by_ctx"][message.ctx_id] = self.stats["by_ctx"].get(message.ctx_id, 0) + 1
        
        # Calculate rates
        elapsed = time.time() - self.stats["start_time"]
        if elapsed > 0:
            self.stats["msg_per_second"] = self.stats["total_messages"] / elapsed
            self.stats["bytes_per_second"] = self.stats["bytes_received"] / elapsed
        
        self._update_tree()
        
    def _update_tree(self):
        """Update the statistics tree"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add general statistics
        general = self.tree.insert("", "end", text="General", open=True)
        self.tree.insert(general, "end", text="Total Messages", values=(self.stats["total_messages"],))
        self.tree.insert(general, "end", text="Messages/Second", values=(f"{self.stats['msg_per_second']:.1f}",))
        self.tree.insert(general, "end", text="Bytes Received", values=(self.stats["bytes_received"],))
        self.tree.insert(general, "end", text="Bytes/Second", values=(f"{self.stats['bytes_per_second']:.1f}",))
        
        # Add log level statistics
        levels = self.tree.insert("", "end", text="Log Levels", open=True)
        for level, count in sorted(self.stats["by_level"].items()):
            self.tree.insert(levels, "end", text=level, values=(count,))
            
        # Add ECU statistics
        ecus = self.tree.insert("", "end", text="ECUs", open=True)
        for ecu, count in sorted(self.stats["by_ecu"].items()):
            self.tree.insert(ecus, "end", text=ecu, values=(count,))
            
        # Add application statistics
        apps = self.tree.insert("", "end", text="Applications", open=True)
        for app, count in sorted(self.stats["by_app"].items()):
            self.tree.insert(apps, "end", text=app, values=(count,))
            
        # Add context statistics
        contexts = self.tree.insert("", "end", text="Contexts", open=True)
        for ctx, count in sorted(self.stats["by_ctx"].items()):
            self.tree.insert(contexts, "end", text=ctx, values=(count,))