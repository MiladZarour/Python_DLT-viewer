"""
DLT Viewer Application - Main UI Application
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import datetime

from ui.main_window import MainWindow
from ui.connection_dialog import ConnectionDialog
from ui.export_dialog import ExportDialog
from core.dlt_file import DLTFile
from core.dlt_connection import DLTConnection
from utils.logger import get_logger

class DLTViewerApp:
    """Main DLT Viewer Application Class"""
    
    def __init__(self, config):
        """Initialize the DLT Viewer application"""
        self.logger = get_logger()
        self.config = config
        self.current_file = None
        self.is_loading = False
        self.connection = None
        self.log_file = None
        
        # Create the main tkinter root window
        self.root = tk.Tk()
        self.root.title("Python DLT Viewer")
        self.root.geometry("1280x800")
        
        # Set theme
        self.theme = config.get("theme", "light")
        self._apply_theme()
        
        # Create the main window interface
        self.main_window = MainWindow(self)
        
        # Set up menu
        self._setup_menu()
        
        # Register event handlers
        self._register_events()
        
        # Apply saved window size and position if available
        if "window" in self.config:
            win_cfg = self.config["window"]
            if "width" in win_cfg and "height" in win_cfg:
                self.root.geometry(f"{win_cfg['width']}x{win_cfg['height']}")
            if "x" in win_cfg and "y" in win_cfg:
                self.root.geometry(f"+{win_cfg['x']}+{win_cfg['y']}")
    
    def run(self):
        """Run the application main loop"""
        self.root.mainloop()
    
    def exit(self):
        """Exit the application"""
        if self.connection and self.connection.is_connected:
            self.connection.disconnect()
            
        # Save window size and position
        self.config["window"] = {
            "width": self.root.winfo_width(),
            "height": self.root.winfo_height(),
            "x": self.root.winfo_x(),
            "y": self.root.winfo_y()
        }
        self.root.destroy()
    
    def save_log(self):
        """Save current messages to a DLT file"""
        if not self.current_file or not self.current_file.messages:
            messagebox.showwarning("No Data", "No messages to save.")
            return
            
        # Show export dialog
        result = ExportDialog.show_dialog(self.root, self.current_file.messages)
        if result:
            self.main_window.update_status(f"Log saved to {result}")
    
    def clear_log(self):
        """Clear current log and start a new one"""
        if self.connection:
            self.connection.clear_log()
            
        # Clear message list
        if self.current_file:
            self.current_file.messages.clear()
            self.main_window.message_list.clear()
            self.main_window.update_status("Log cleared")
    
    def _on_message_received(self, message):
        """Handle received DLT message"""
        # Add to message list
        if hasattr(self, 'main_window'):
            self.main_window.message_list.add_message(message)
    
    def connect_to_device(self):
        """Open connection dialog and connect to DLT device"""
        result = ConnectionDialog.show_dialog(self.root)
        if not result:
            return
            
        host, port = result
        
        # Disconnect existing connection if any
        if self.connection and self.connection.is_connected:
            self.connection.disconnect()
        
        # Create new connection
        self.connection = DLTConnection(host, port)
        
        # Try to connect
        if self.connection.connect():
            self.main_window.update_status(f"Connected to {host}:{port}")
            
            # Set up message callback
            self.connection.add_callback(self._on_message_received)
        else:
            messagebox.showerror("Connection Failed", 
                               f"Could not connect to {host}:{port}")
    
    def disconnect_from_device(self):
        """Disconnect from DLT device"""
        if self.connection and self.connection.is_connected:
            self.connection.disconnect()
            self.main_window.update_status("Disconnected from device")
    
    def _setup_menu(self):
        """Set up the application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", 
                            command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S",
                            command=self.save_log)
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        self._update_recent_menu()
        file_menu.add_cascade(label="Open Recent", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Alt+F4", 
                            command=self.exit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Connection menu
        conn_menu = tk.Menu(menubar, tearoff=0)
        conn_menu.add_command(label="Connect...", command=self.connect_to_device)
        conn_menu.add_command(label="Disconnect", command=self.disconnect_from_device)
        conn_menu.add_separator()
        conn_menu.add_command(label="Clear Log", command=self.clear_log)
        menubar.add_cascade(label="Connection", menu=conn_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _register_events(self):
        """Register keyboard shortcuts and events"""
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_log())
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        
    def _update_recent_files(self, file_path):
        """Update the list of recently opened files"""
        recent_files = self.config.get("recent_files", [])
        
        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)
            
        # Add to the beginning
        recent_files.insert(0, file_path)
        
        # Keep only the 10 most recent
        self.config["recent_files"] = recent_files[:10]
        
        # Update the menu
        self._update_recent_menu()
        
    def _update_recent_menu(self):
        """Update the recent files menu"""
        # Clear the menu
        self.recent_menu.delete(0, tk.END)
        
        recent_files = self.config.get("recent_files", [])
        
        if not recent_files:
            self.recent_menu.add_command(label="No recent files", state=tk.DISABLED)
            return
            
        # Add each recent file
        for file_path in recent_files:
            if os.path.exists(file_path):
                # Use lambda with default argument to avoid late binding issues
                self.recent_menu.add_command(
                    label=os.path.basename(file_path),
                    command=lambda fp=file_path: self.open_file(fp)
                )
    
    def _show_about(self):
        """Show the about dialog"""
        messagebox.showinfo(
            "About Python DLT Viewer",
            "Python DLT Viewer 1.0\n\n"
            "A pure Python application for viewing and analyzing "
            "DLT (Diagnostic Log and Trace) files.\n\n"
            "© 2025 All Rights Reserved."
        )

    def open_file(self, file_path=None):
        """Open a DLT file"""
        if self.is_loading:
            messagebox.showwarning("Operation in Progress", 
                                 "Please wait until the current file is loaded.")
            return
            
        if not file_path:
            initial_dir = self.config.get("last_dir", os.path.expanduser("~"))
            file_path = filedialog.askopenfilename(
                title="Open DLT File",
                initialdir=initial_dir,
                filetypes=[("DLT Files", "*.dlt"), ("All Files", "*.*")]
            )
        
        if not file_path:
            return  # User cancelled
            
        # Save the directory for next time
        self.config["last_dir"] = os.path.dirname(file_path)
        
        # Update recent files list
        self._update_recent_files(file_path)
        
        # Start loading in a background thread to prevent UI freezing
        self.is_loading = True
        self.main_window.show_loading(f"Loading {os.path.basename(file_path)}...")
        
        thread = threading.Thread(target=self._load_file_thread, args=(file_path,))
        thread.daemon = True
        thread.start()

    def _load_file_thread(self, file_path):
        """Background thread for loading DLT files"""
        try:
            dlt_file = DLTFile(file_path)
            dlt_file.parse_header()
            # Initially load just enough messages to display
            initial_messages = dlt_file.load_messages(limit=1000)
            
            # Update UI in the main thread
            self.root.after(0, lambda: self._file_loaded(dlt_file))
        except Exception as e:
            self.logger.error(f"Error loading file: {e}", exc_info=True)
            self.root.after(0, lambda: self._show_load_error(str(e)))
    
    def _file_loaded(self, dlt_file):
        """Called when file is loaded successfully"""
        self.current_file = dlt_file
        self.main_window.hide_loading()
        self.main_window.update_file_view(dlt_file)
        self.root.title(f"Python DLT Viewer - {os.path.basename(dlt_file.file_path)}")
        self.is_loading = False
    
    def _show_load_error(self, error_msg):
        """Show error message when file loading fails"""
        self.main_window.hide_loading()
        self.is_loading = False
        messagebox.showerror("Error Loading File", 
                           f"Failed to load DLT file: {error_msg}")
    
    def _apply_theme(self):
        """Apply the selected theme to the application"""
        style = ttk.Style()
        
        if self.theme == "dark":
            # Dark theme settings
            self.root.configure(background='#2e2e2e')
            style.configure('TFrame', background='#2e2e2e')
            style.configure('TLabel', background='#2e2e2e', foreground='#e0e0e0')
            style.configure('TButton', background='#3d3d3d', foreground='#e0e0e0')
            style.map('TButton', 
                    background=[('active', '#4d4d4d')],
                    foreground=[('active', '#ffffff')])
            style.configure('Treeview', 
                          background='#3d3d3d', 
                          foreground='#e0e0e0',
                          fieldbackground='#3d3d3d')
            style.map('Treeview', 
                    background=[('selected', '#0078d7')],
                    foreground=[('selected', '#ffffff')])
        else:
            # Light theme (default)
            self.root.configure(background='#f0f0f0')
            style.configure('TFrame', background='#f0f0f0')
            style.configure('TLabel', background='#f0f0f0', foreground='#000000')
            style.configure('TButton', background='#e1e1e1', foreground='#000000')
            style.map('TButton', 
                    background=[('active', '#d1d1d1')],
                    foreground=[('active', '#000000')])
            style.configure('Treeview', 
                          background='#ffffff', 
                          foreground='#000000',
                          fieldbackground='#ffffff')
            style.map('Treeview', 
                    background=[('selected', '#0078d7')],
                    foreground=[('selected', '#ffffff')])
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.theme = "dark" if self.theme == "light" else "light"
        self.config["theme"] = self.theme
        self._apply_theme()