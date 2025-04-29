"""
Advanced Search Dialog
"""
import tkinter as tk
from tkinter import ttk

class SearchDialog:
    """Advanced search dialog for DLT messages"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Advanced Search")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        window_width = 400
        window_height = 300
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search criteria
        criteria_frame = ttk.LabelFrame(main_frame, text="Search Criteria")
        criteria_frame.pack(fill=tk.X, pady=5)
        
        # Text search
        text_frame = ttk.Frame(criteria_frame)
        text_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(text_frame, text="Text:").pack(side=tk.LEFT)
        self.text_var = tk.StringVar()
        ttk.Entry(text_frame, textvariable=self.text_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )
        
        # Case sensitive
        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(
            criteria_frame, 
            text="Case Sensitive",
            variable=self.case_sensitive
        ).pack(anchor=tk.W, padx=5)
        
        # Regular expression
        self.use_regex = tk.BooleanVar()
        ttk.Checkbutton(
            criteria_frame,
            text="Use Regular Expression",
            variable=self.use_regex
        ).pack(anchor=tk.W, padx=5)
        
        # Search scope
        scope_frame = ttk.LabelFrame(main_frame, text="Search Scope")
        scope_frame.pack(fill=tk.X, pady=5)
        
        # Scope checkboxes
        self.search_payload = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            scope_frame,
            text="Search in Payload",
            variable=self.search_payload
        ).pack(anchor=tk.W, padx=5)
        
        self.search_headers = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            scope_frame,
            text="Search in Headers",
            variable=self.search_headers
        ).pack(anchor=tk.W, padx=5)
        
        # Direction
        direction_frame = ttk.LabelFrame(main_frame, text="Search Direction")
        direction_frame.pack(fill=tk.X, pady=5)
        
        self.direction = tk.StringVar(value="forward")
        ttk.Radiobutton(
            direction_frame,
            text="Forward",
            variable=self.direction,
            value="forward"
        ).pack(anchor=tk.W, padx=5)
        
        ttk.Radiobutton(
            direction_frame,
            text="Backward",
            variable=self.direction,
            value="backward"
        ).pack(anchor=tk.W, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Find",
            command=self._on_find
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.RIGHT)
        
    def _on_find(self):
        """Handle find button"""
        self.result = {
            "text": self.text_var.get(),
            "case_sensitive": self.case_sensitive.get(),
            "use_regex": self.use_regex.get(),
            "search_payload": self.search_payload.get(),
            "search_headers": self.search_headers.get(),
            "direction": self.direction.get()
        }
        self.dialog.destroy()
        
    def _on_cancel(self):
        """Handle cancel button"""
        self.dialog.destroy()
        
    @classmethod
    def show_dialog(cls, parent):
        """Show the search dialog"""
        dialog = cls(parent)
        dialog.dialog.wait_window()
        return dialog.result