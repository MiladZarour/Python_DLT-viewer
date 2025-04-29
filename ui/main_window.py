"""
Main Window UI for the DLT Viewer
"""
import tkinter as tk
from tkinter import ttk
import time

from ui.message_list import MessageListView
from ui.filter_panel import FilterPanel
from ui.message_view import MessageDetailView
from ui.statistics_view import StatisticsView
from ui.marker_view import MarkerView

class MainWindow:
    """Main application window interface"""
    
    def __init__(self, app):
        """Initialize the main window UI components"""
        self.app = app
        self.root = app.root
        
        # Create notebook for main views
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Main view
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Messages")
        
        # Statistics view
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        # Markers view
        self.markers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.markers_frame, text="Markers")
        
        # Initialize views
        self._init_main_view()
        self._init_stats_view()
        self._init_markers_view()
        
        # Create status bar
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.message_count_label = ttk.Label(self.status_bar, text="")
        self.message_count_label.pack(side=tk.RIGHT)
        
    def _init_main_view(self):
        """Initialize the main message view"""
        # Create the main layout using PanedWindow
        self.h_paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.h_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Filter panel
        self.filter_frame = ttk.Frame(self.h_paned)
        self.filter_panel = FilterPanel(self.filter_frame, self)  # Fixed: Added self as main_window parameter
        self.filter_panel.pack(fill=tk.BOTH, expand=True)
        self.h_paned.add(self.filter_frame, weight=1)
        
        # Right side
        self.v_paned = ttk.PanedWindow(self.h_paned, orient=tk.VERTICAL)
        self.h_paned.add(self.v_paned, weight=3)
        
        # Message list (top of right panel)
        self.message_list_frame = ttk.Frame(self.v_paned)
        self.message_list = MessageListView(self.message_list_frame, self)
        self.message_list.pack(fill=tk.BOTH, expand=True)
        self.v_paned.add(self.message_list_frame, weight=2)
        
        # Message details (bottom of right panel)
        self.detail_frame = ttk.Frame(self.v_paned)
        self.message_detail = MessageDetailView(self.detail_frame, self)
        self.message_detail.pack(fill=tk.BOTH, expand=True)
        self.v_paned.add(self.detail_frame, weight=1)
        
    def _init_stats_view(self):
        """Initialize the statistics view"""
        self.stats_view = StatisticsView(self.stats_frame, self)
        self.stats_view.pack(fill=tk.BOTH, expand=True)
        
    def _init_markers_view(self):
        """Initialize the markers view"""
        self.markers_view = MarkerView(self.markers_frame, self)
        self.markers_view.pack(fill=tk.BOTH, expand=True)
        
    def update_file_view(self, dlt_file):
        """Update the UI with the loaded file data"""
        # Update the message list
        self.message_list.load_messages(dlt_file.messages)
        
        # Update filter panel
        self.filter_panel.update_filters(dlt_file)
        
        # Update statistics
        for message in dlt_file.messages:
            self.stats_view.update_stats(message)
        
        # Update status bar
        self.update_status(f"Loaded {len(dlt_file.messages)} messages")
        self.update_message_count(len(dlt_file.messages))
        
    def update_status(self, message):
        """Update the status bar message"""
        self.status_label.config(text=message)
        
    def update_message_count(self, count, filtered=None):
        """Update the message count display"""
        if filtered is not None and filtered != count:
            self.message_count_label.config(
                text=f"Showing {filtered} of {count} messages"
            )
        else:
            self.message_count_label.config(text=f"{count} messages")