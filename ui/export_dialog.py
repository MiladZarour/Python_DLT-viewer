"""
Export Dialog
"""
import tkinter as tk
from tkinter import ttk, filedialog
from core.export_manager import DLTExportManager

class ExportDialog:
    """Dialog for exporting DLT messages"""
    
    def __init__(self, parent, messages):
        self.parent = parent
        self.messages = messages
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export Messages")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        window_width = 400
        window_height = 200
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Export format
        format_frame = ttk.LabelFrame(main_frame, text="Export Format")
        format_frame.pack(fill=tk.X, pady=5)
        
        self.format_var = tk.StringVar(value="dlt")
        
        ttk.Radiobutton(
            format_frame,
            text="DLT File",
            variable=self.format_var,
            value="dlt"
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(
            format_frame,
            text="CSV File",
            variable=self.format_var,
            value="csv"
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(
            format_frame,
            text="JSON File",
            variable=self.format_var,
            value="json"
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Export range
        range_frame = ttk.LabelFrame(main_frame, text="Export Range")
        range_frame.pack(fill=tk.X, pady=5)
        
        self.range_var = tk.StringVar(value="all")
        
        ttk.Radiobutton(
            range_frame,
            text="All Messages",
            variable=self.range_var,
            value="all"
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(
            range_frame,
            text="Filtered Messages Only",
            variable=self.range_var,
            value="filtered"
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Export",
            command=self._on_export
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.RIGHT)
        
    def _on_export(self):
        """Handle export button"""
        export_format = self.format_var.get()
        
        # Get file extension and type
        if export_format == "dlt":
            file_types = [("DLT Files", "*.dlt")]
            default_ext = ".dlt"
        elif export_format == "csv":
            file_types = [("CSV Files", "*.csv")]
            default_ext = ".csv"
        else:
            file_types = [("JSON Files", "*.json")]
            default_ext = ".json"
            
        # Get save location
        filepath = filedialog.asksaveasfilename(
            parent=self.dialog,
            defaultextension=default_ext,
            filetypes=file_types
        )
        
        if not filepath:
            return
            
        # Export based on format
        try:
            if export_format == "dlt":
                DLTExportManager.export_to_dlt(self.messages, filepath)
            elif export_format == "csv":
                DLTExportManager.export_to_csv(self.messages, filepath)
            else:
                DLTExportManager.export_to_json(self.messages, filepath)
                
            self.result = filepath
            self.dialog.destroy()
            
        except Exception as e:
            tk.messagebox.showerror(
                "Export Error",
                f"Failed to export messages: {str(e)}"
            )
        
    def _on_cancel(self):
        """Handle cancel button"""
        self.dialog.destroy()
        
    @classmethod
    def show_dialog(cls, parent, messages):
        """Show the export dialog"""
        dialog = cls(parent, messages)
        dialog.dialog.wait_window()
        return dialog.result