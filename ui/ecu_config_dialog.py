"""
ECU Configuration Dialog
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core.dlt_ecu import ECUConfig

class ECUConfigDialog:
    """Dialog for configuring ECU settings"""
    
    def __init__(self, parent, ecu=None):
        """Initialize the ECU configuration dialog"""
        self.parent = parent
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("ECU Configuration")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        window_width = 400
        window_height = 450
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ECU ID
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(id_frame, text="ECU ID:").pack(side=tk.LEFT)
        self.ecu_id_var = tk.StringVar(value=ecu.ecu_id if ecu else "")
        self.ecu_id_entry = ttk.Entry(id_frame, textvariable=self.ecu_id_var)
        self.ecu_id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Description
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(desc_frame, text="Description:").pack(side=tk.LEFT)
        self.desc_var = tk.StringVar(value=ecu.description if ecu else "")
        self.desc_entry = ttk.Entry(desc_frame, textvariable=self.desc_var)
        self.desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Network settings
        net_frame = ttk.LabelFrame(main_frame, text="Network Settings")
        net_frame.pack(fill=tk.X, pady=10)
        
        # IP Address
        ip_frame = ttk.Frame(net_frame)
        ip_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(ip_frame, text="IP Address:").pack(side=tk.LEFT)
        self.ip_var = tk.StringVar(value=ecu.ip_address if ecu else "")
        self.ip_entry = ttk.Entry(ip_frame, textvariable=self.ip_var)
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # TCP Port
        port_frame = ttk.Frame(net_frame)
        port_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(port_frame, text="TCP Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value=str(ecu.tcp_port if ecu else 3490))
        self.port_entry = ttk.Entry(port_frame, textvariable=self.port_var)
        self.port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Options frame
        opt_frame = ttk.LabelFrame(main_frame, text="Options")
        opt_frame.pack(fill=tk.X, pady=10)
        
        # Verbose mode
        self.verbose_var = tk.BooleanVar(value=ecu.verbose if ecu else True)
        ttk.Checkbutton(
            opt_frame, 
            text="Verbose Mode",
            variable=self.verbose_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Timing packets
        self.timing_var = tk.BooleanVar(value=ecu.timing if ecu else False)
        ttk.Checkbutton(
            opt_frame,
            text="Send Timing Packets",
            variable=self.timing_var
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Default log level
        level_frame = ttk.Frame(opt_frame)
        level_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(level_frame, text="Default Log Level:").pack(side=tk.LEFT)
        self.level_var = tk.StringVar(value=ecu.default_log_level if ecu else "INFO")
        level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.level_var,
            values=["FATAL", "ERROR", "WARN", "INFO", "DEBUG", "VERBOSE"],
            state="readonly"
        )
        level_combo.pack(side=tk.LEFT, padx=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="OK",
            command=self._on_ok
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.RIGHT)
        
        # Configure dialog behavior
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.dialog.bind("<Return>", lambda e: self._on_ok())
        self.dialog.bind("<Escape>", lambda e: self._on_cancel())
        
    def _validate(self):
        """Validate input values"""
        try:
            # Validate ECU ID
            ecu_id = self.ecu_id_var.get().strip()
            if not ecu_id:
                raise ValueError("ECU ID is required")
                
            # Validate port
            port = int(self.port_var.get())
            if port < 1 or port > 65535:
                raise ValueError("Port must be between 1 and 65535")
                
            return True
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return False
            
    def _on_ok(self):
        """Handle OK button"""
        if self._validate():
            # Create ECU config
            self.result = ECUConfig(
                self.ecu_id_var.get().strip(),
                description=self.desc_var.get().strip(),
                ip_address=self.ip_var.get().strip(),
                tcp_port=int(self.port_var.get()),
                verbose=self.verbose_var.get(),
                timing=self.timing_var.get(),
                default_log_level=self.level_var.get()
            )
            self.dialog.destroy()
            
    def _on_cancel(self):
        """Handle Cancel button"""
        self.dialog.destroy()
        
    @classmethod
    def show_dialog(cls, parent, ecu=None):
        """Show the ECU configuration dialog"""
        dialog = cls(parent, ecu)
        dialog.dialog.wait_window()
        return dialog.result