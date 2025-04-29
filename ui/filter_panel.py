"""
Filter Panel Component
"""
import tkinter as tk
from tkinter import ttk
import time

class FilterPanel(ttk.Frame):
    """Panel for filtering DLT messages"""
    
    def __init__(self, parent, main_window):
        """Initialize the filter panel"""
        super().__init__(parent)  # Initialize parent class
        
        self.parent = parent
        self.main_window = main_window
        self.current_filter = {}
        
        # Main container
        self.main_frame = ttk.Frame(self)  # Use self instead of parent
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Message Filters", font=('Arial', 11, 'bold'))
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create notebook for filter categories
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic filters tab
        self.basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.basic_frame, text="Basic")
        
        # Advanced filters tab
        self.advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_frame, text="Advanced")
        
        # ECU filter section in basic tab
        self.ecu_frame = ttk.LabelFrame(self.basic_frame, text="ECU IDs")
        self.ecu_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.ecu_vars = {}
        self.ecu_checkboxes = ttk.Frame(self.ecu_frame)
        self.ecu_checkboxes.pack(fill=tk.X, pady=5)
        
        # App ID filter section in basic tab
        self.app_frame = ttk.LabelFrame(self.basic_frame, text="Application IDs")
        self.app_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.app_vars = {}
        self.app_checkboxes = ttk.Frame(self.app_frame)
        self.app_checkboxes.pack(fill=tk.X, pady=5)
        
        # Context ID filter section in basic tab
        self.ctx_frame = ttk.LabelFrame(self.basic_frame, text="Context IDs")
        self.ctx_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.ctx_vars = {}
        self.ctx_checkboxes = ttk.Frame(self.ctx_frame)
        self.ctx_checkboxes.pack(fill=tk.X, pady=5)
        
        # Log level filter in basic tab
        self.level_frame = ttk.LabelFrame(self.basic_frame, text="Log Levels")
        self.level_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.level_vars = {}
        self.level_checkboxes = ttk.Frame(self.level_frame)
        self.level_checkboxes.pack(fill=tk.X, pady=5)
        
        # Time range filter in advanced tab
        self.time_frame = ttk.LabelFrame(self.advanced_frame, text="Time Range")
        self.time_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Start time
        start_frame = ttk.Frame(self.time_frame)
        start_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(start_frame, text="Start:").pack(side=tk.LEFT, padx=(0, 5))
        self.time_start_var = tk.StringVar()
        self.time_start_entry = ttk.Entry(start_frame, textvariable=self.time_start_var)
        self.time_start_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # End time
        end_frame = ttk.Frame(self.time_frame)
        end_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(end_frame, text="End:  ").pack(side=tk.LEFT, padx=(0, 5))
        self.time_end_var = tk.StringVar()
        self.time_end_entry = ttk.Entry(end_frame, textvariable=self.time_end_var)
        self.time_end_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Payload text filter in advanced tab
        self.payload_frame = ttk.LabelFrame(self.advanced_frame, text="Payload Content")
        self.payload_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.payload_var = tk.StringVar()
        self.payload_entry = ttk.Entry(self.payload_frame, textvariable=self.payload_var)
        self.payload_entry.pack(fill=tk.X, pady=5, padx=5)
        
        # Filter control buttons at the bottom
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.apply_button = ttk.Button(
            self.button_frame, 
            text="Apply Filters",
            command=self._apply_filters
        )
        self.apply_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(
            self.button_frame, 
            text="Reset Filters",
            command=self._reset_filters
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Set up auto-update of filters
        self.payload_var.trace_add("write", lambda *args: self._auto_apply_filters())
        self.time_start_var.trace_add("write", lambda *args: self._auto_apply_filters())
        self.time_end_var.trace_add("write", lambda *args: self._auto_apply_filters())
    
    def update_filters(self, dlt_file):
        """Update available filters based on the DLT file"""
        # Clear existing checkboxes
        for widget in self.ecu_checkboxes.winfo_children():
            widget.destroy()
        
        for widget in self.app_checkboxes.winfo_children():
            widget.destroy()
            
        for widget in self.ctx_checkboxes.winfo_children():
            widget.destroy()
            
        for widget in self.level_checkboxes.winfo_children():
            widget.destroy()
        
        # Reset filter variables
        self.ecu_vars = {}
        self.app_vars = {}
        self.ctx_vars = {}
        self.level_vars = {}
        
        # Extract unique values from messages
        ecu_ids = set()
        app_ids = set()
        ctx_ids = set()
        log_levels = set()
        
        for msg in dlt_file.messages:
            ecu_ids.add(msg.ecu_id)
            app_ids.add(msg.app_id)
            ctx_ids.add(msg.ctx_id)
            log_levels.add(msg.log_level)
        
        # Create ECU ID checkboxes
        for ecu_id in sorted(ecu_ids):
            var = tk.BooleanVar(value=True)
            self.ecu_vars[ecu_id] = var
            cb = ttk.Checkbutton(
                self.ecu_checkboxes, 
                text=ecu_id,
                variable=var,
                command=self._checkbox_change
            )
            cb.pack(anchor=tk.W)
        
        # Create App ID checkboxes
        for app_id in sorted(app_ids):
            var = tk.BooleanVar(value=True)
            self.app_vars[app_id] = var
            cb = ttk.Checkbutton(
                self.app_checkboxes, 
                text=app_id,
                variable=var,
                command=self._checkbox_change
            )
            cb.pack(anchor=tk.W)
        
        # Create Context ID checkboxes
        for ctx_id in sorted(ctx_ids):
            var = tk.BooleanVar(value=True)
            self.ctx_vars[ctx_id] = var
            cb = ttk.Checkbutton(
                self.ctx_checkboxes, 
                text=ctx_id,
                variable=var,
                command=self._checkbox_change
            )
            cb.pack(anchor=tk.W)
        
        # Create Log Level checkboxes
        for level in sorted(log_levels):
            var = tk.BooleanVar(value=True)
            self.level_vars[level] = var
            cb = ttk.Checkbutton(
                self.level_checkboxes, 
                text=level,
                variable=var,
                command=self._checkbox_change
            )
            cb.pack(anchor=tk.W)
        
        # Reset other filter inputs
        self.time_start_var.set("")
        self.time_end_var.set("")
        self.payload_var.set("")
    
    def get_current_filter(self):
        """Get the current filter configuration"""
        return self.current_filter.copy()
    
    def _apply_filters(self):
        """Apply the current filter settings"""
        self.current_filter = self._build_filter_config()
        self.main_window.apply_filter(self.current_filter)
    
    def _reset_filters(self):
        """Reset all filters to default state"""
        # Reset checkboxes
        for var in self.ecu_vars.values():
            var.set(True)
        
        for var in self.app_vars.values():
            var.set(True)
            
        for var in self.ctx_vars.values():
            var.set(True)
            
        for var in self.level_vars.values():
            var.set(True)
        
        # Reset other inputs
        self.time_start_var.set("")
        self.time_end_var.set("")
        self.payload_var.set("")
        
        # Apply the reset
        self.current_filter = {}
        self.main_window.apply_filter(self.current_filter)
    
    def _checkbox_change(self):
        """Handle checkbox changes"""
        self._auto_apply_filters()
    
    def _auto_apply_filters(self):
        """Automatically apply filters after delay"""
        # This could be enhanced with a delay timer to avoid too frequent updates
        self._apply_filters()
    
    def _build_filter_config(self):
        """Build filter configuration from UI controls"""
        filter_config = {}
        
        # ECU IDs
        selected_ecus = [ecu for ecu, var in self.ecu_vars.items() if var.get()]
        if len(selected_ecus) < len(self.ecu_vars):
            filter_config["ecu"] = selected_ecus
        
        # App IDs
        selected_apps = [app for app, var in self.app_vars.items() if var.get()]
        if len(selected_apps) < len(self.app_vars):
            filter_config["app_id"] = selected_apps
        
        # Context IDs
        selected_ctxs = [ctx for ctx, var in self.ctx_vars.items() if var.get()]
        if len(selected_ctxs) < len(self.ctx_vars):
            filter_config["ctx_id"] = selected_ctxs
        
        # Log levels
        selected_levels = [level for level, var in self.level_vars.items() if var.get()]
        if len(selected_levels) < len(self.level_vars):
            filter_config["log_level"] = selected_levels
        
        # Time range
        start_time = self.time_start_var.get().strip()
        if start_time:
            try:
                # Parse time format HH:MM:SS.mmm
                filter_config["time_start"] = self._parse_time(start_time)
            except ValueError:
                # Invalid format, ignore
                pass
        
        end_time = self.time_end_var.get().strip()
        if end_time:
            try:
                filter_config["time_end"] = self._parse_time(end_time)
            except ValueError:
                # Invalid format, ignore
                pass
        
        # Payload text
        payload_text = self.payload_var.get().strip()
        if payload_text:
            filter_config["payload_text"] = payload_text
        
        return filter_config
    
    def _parse_time(self, time_str):
        """Parse time string to timestamp"""
        # This is a simplified version - could be enhanced to handle various formats
        parts = time_str.split(':')
        if len(parts) != 3:
            raise ValueError("Invalid time format")
            
        seconds_parts = parts[2].split('.')
        seconds = float(seconds_parts[0])
        if len(seconds_parts) > 1:
            seconds += float('0.' + seconds_parts[1])
            
        hours = int(parts[0])
        minutes = int(parts[1])
        
        # Get current day's timestamp at midnight
        t = time.localtime()
        base_time = time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, 0))
        
        # Add the specified time
        return base_time + hours * 3600 + minutes * 60 + seconds