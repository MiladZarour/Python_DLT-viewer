"""
Connection Dialog - UI for TCP/IP connection settings
"""
import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import queue

class ConnectionDialog:
    """Dialog for configuring DLT network connection"""
    
    def __init__(self, parent):
        """Initialize the connection dialog"""
        self.parent = parent
        self.result = None
        self.scan_thread = None
        self.devices = queue.Queue()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Connect to DLT Device")
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
        
        # Device list
        list_frame = ttk.LabelFrame(main_frame, text="Available Devices")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for devices
        self.device_tree = ttk.Treeview(
            list_frame,
            columns=("host", "port", "status"),
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.device_tree.heading("host", text="Host")
        self.device_tree.heading("port", text="Port")
        self.device_tree.heading("status", text="Status")
        
        self.device_tree.column("host", width=150)
        self.device_tree.column("port", width=80)
        self.device_tree.column("status", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack list and scrollbar
        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Manual connection frame
        manual_frame = ttk.LabelFrame(main_frame, text="Manual Connection")
        manual_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Host entry
        host_frame = ttk.Frame(manual_frame)
        host_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(host_frame, text="Host:").pack(side=tk.LEFT)
        self.host_var = tk.StringVar(value="localhost")
        self.host_entry = ttk.Entry(host_frame, textvariable=self.host_var)
        self.host_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Port entry
        port_frame = ttk.Frame(manual_frame)
        port_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="3490")
        self.port_entry = ttk.Entry(port_frame, textvariable=self.port_var)
        self.port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Scan button
        self.scan_button = ttk.Button(
            button_frame, 
            text="Scan Network",
            command=self._start_scan
        )
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        # Connect/Cancel buttons
        ttk.Button(
            button_frame,
            text="Connect",
            command=self._on_connect
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X, pady=(5, 0))
        
        # Configure dialog behavior
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.dialog.bind("<Return>", lambda e: self._on_connect())
        self.dialog.bind("<Escape>", lambda e: self._on_cancel())
        
        # Double-click to connect
        self.device_tree.bind("<Double-1>", lambda e: self._on_connect())
        self.device_tree.bind("<<TreeviewSelect>>", self._on_device_select)
        
        # Start initial scan
        self._start_scan()
    
    def _start_scan(self):
        """Start network scan"""
        # Clear existing items
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        
        self.scan_button.configure(state=tk.DISABLED)
        self.status_var.set("Scanning network...")
        
        # Start scan in background thread
        self.scan_thread = threading.Thread(target=self._scan_network)
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
        # Start checking for results
        self.dialog.after(100, self._check_scan_results)
    
    def _scan_network(self):
        """Scan network for DLT devices"""
        try:
            # Scan local network
            for port in [3490, 3491]:  # Common DLT ports
                # Try localhost first
                self._check_host("localhost", port)
                
                # Try common IP patterns
                for i in range(1, 255):
                    host = f"192.168.1.{i}"
                    self._check_host(host, port)
        except Exception as e:
            print(f"Scan error: {e}")
        finally:
            # Signal scan complete
            self.devices.put(None)
    
    def _check_host(self, host, port):
        """Check if host:port has a DLT service"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Short timeout for quick scanning
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                # Connection successful, likely a DLT service
                self.devices.put((host, port, "Available"))
        except:
            pass
    
    def _check_scan_results(self):
        """Check for scan results and update UI"""
        try:
            while True:
                device = self.devices.get_nowait()
                if device is None:
                    # Scan complete
                    self.scan_button.configure(state=tk.NORMAL)
                    self.status_var.set("Scan complete")
                    return
                    
                # Add device to tree
                host, port, status = device
                self.device_tree.insert(
                    "",
                    "end",
                    values=(host, port, status)
                )
        except queue.Empty:
            # No more results yet, check again later
            self.dialog.after(100, self._check_scan_results)
    
    def _on_device_select(self, event):
        """Handle device selection"""
        selection = self.device_tree.selection()
        if selection:
            values = self.device_tree.item(selection[0], "values")
            self.host_var.set(values[0])
            self.port_var.set(values[1])
    
    def _validate_input(self):
        """Validate connection parameters"""
        try:
            # Validate host
            host = self.host_var.get().strip()
            if not host:
                raise ValueError("Host cannot be empty")
                
            # Validate port
            port = int(self.port_var.get())
            if port < 1 or port > 65535:
                raise ValueError("Port must be between 1 and 65535")
                
            return host, port
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return None
    
    def _on_connect(self):
        """Handle connect button"""
        result = self._validate_input()
        if result:
            self.result = result
            self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel button"""
        self.dialog.destroy()
    
    @classmethod
    def show_dialog(cls, parent):
        """Show the connection dialog"""
        dialog = cls(parent)
        dialog.dialog.wait_window()
        return dialog.result