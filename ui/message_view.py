"""
Message Detail View Component
"""
import tkinter as tk
from tkinter import ttk
import json

class MessageDetailView(ttk.Frame):
    """Component for displaying detailed information about a DLT message"""
    
    def __init__(self, parent, main_window):
        """Initialize the message detail view"""
        super().__init__(parent)  # Initialize parent class
        
        self.parent = parent
        self.main_window = main_window
        
        # Create main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for message details
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic info tab
        self.basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.basic_frame, text="Basic Info")
        
        # Create a frame for header information
        self.header_frame = ttk.LabelFrame(self.basic_frame, text="Message Header")
        self.header_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Create grid layout for header info
        header_grid = ttk.Frame(self.header_frame)
        header_grid.pack(fill=tk.X, padx=5, pady=5)
        
        # Header fields
        self.header_fields = [
            ("Time", "time"),
            ("ECU ID", "ecu_id"),
            ("Application ID", "app_id"),
            ("Context ID", "ctx_id"),
            ("Session ID", "session_id"),
            ("Log Level", "log_level"),
            ("Message Type", "msg_type"),
            ("Message ID", "msg_id")
        ]
        
        # Create labels and values
        self.header_values = {}
        
        for i, (label, field) in enumerate(self.header_fields):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(header_grid, text=f"{label}:", width=15, anchor=tk.E).grid(
                row=row, column=col, sticky=tk.E, padx=(5, 2), pady=2
            )
            
            val_var = tk.StringVar()
            self.header_values[field] = val_var
            
            ttk.Label(header_grid, textvariable=val_var, width=20, anchor=tk.W).grid(
                row=row, column=col+1, sticky=tk.W, padx=(0, 15), pady=2
            )
        
        # Configure the grid
        for i in range(4):
            header_grid.columnconfigure(i, weight=1)
        
        # Create a frame for payload
        self.payload_frame = ttk.LabelFrame(self.basic_frame, text="Payload")
        self.payload_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Text widget for payload with scrollbar
        payload_container = ttk.Frame(self.payload_frame)
        payload_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.payload_text = tk.Text(payload_container, wrap=tk.WORD, height=10)
        payload_scroll = ttk.Scrollbar(payload_container, command=self.payload_text.yview)
        self.payload_text.configure(yscrollcommand=payload_scroll.set)
        
        payload_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.payload_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Make text widget read-only
        self.payload_text.config(state=tk.DISABLED)
        
        # Hex view tab
        self.hex_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hex_frame, text="Hex View")
        
        # Text widget for hex view with scrollbar
        hex_container = ttk.Frame(self.hex_frame)
        hex_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.hex_text = tk.Text(hex_container, wrap=tk.NONE, height=15, font=("Courier", 10))
        
        hex_vscroll = ttk.Scrollbar(hex_container, command=self.hex_text.yview)
        hex_hscroll = ttk.Scrollbar(hex_container, orient=tk.HORIZONTAL, command=self.hex_text.xview)
        
        self.hex_text.configure(yscrollcommand=hex_vscroll.set, xscrollcommand=hex_hscroll.set)
        
        hex_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        hex_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.hex_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Make hex view read-only
        self.hex_text.config(state=tk.DISABLED)
        
        # Parsed data tab
        self.parsed_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.parsed_frame, text="Parsed Data")
        
        # Treeview for structured data
        self.parsed_container = ttk.Frame(self.parsed_frame)
        self.parsed_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.parsed_tree = ttk.Treeview(
            self.parsed_container,
            columns=("value", "type", "description"),
            show="tree headings"
        )
        
        # Configure columns
        self.parsed_tree.heading("value", text="Value")
        self.parsed_tree.heading("type", text="Type")
        self.parsed_tree.heading("description", text="Description")
        
        self.parsed_tree.column("#0", width=200)
        self.parsed_tree.column("value", width=150)
        self.parsed_tree.column("type", width=100)
        self.parsed_tree.column("description", width=300)
        
        # Add scrollbars
        parsed_vscroll = ttk.Scrollbar(
            self.parsed_container, 
            command=self.parsed_tree.yview
        )
        parsed_hscroll = ttk.Scrollbar(
            self.parsed_container, 
            orient=tk.HORIZONTAL, 
            command=self.parsed_tree.xview
        )
        
        self.parsed_tree.configure(
            yscrollcommand=parsed_vscroll.set,
            xscrollcommand=parsed_hscroll.set
        )
        
        parsed_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        parsed_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.parsed_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Button toolbar
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(5, 0))
        
        self.bookmark_button = ttk.Button(
            self.toolbar,
            text="Add Bookmark",
            command=self._add_bookmark
        )
        self.bookmark_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(
            self.toolbar,
            text="Export Message",
            command=self._export_message
        )
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        self.copy_button = ttk.Button(
            self.toolbar,
            text="Copy to Clipboard",
            command=self._copy_to_clipboard
        )
        self.copy_button.pack(side=tk.RIGHT, padx=5)
        
        # Current message reference
        self.current_message = None
    
    def display_message(self, message):
        """Display message details"""
        self.current_message = message
        
        # Update header values
        self._update_header_info(message)
        
        # Update payload text
        self._update_payload_text(message)
        
        # Update hex view
        self._update_hex_view(message)
        
        # Update parsed data view
        self._update_parsed_view(message)
    
    def clear(self):
        """Clear all message information"""
        self.current_message = None
        
        # Clear header values
        for var in self.header_values.values():
            var.set("")
        
        # Clear payload text
        self.payload_text.config(state=tk.NORMAL)
        self.payload_text.delete("1.0", tk.END)
        self.payload_text.config(state=tk.DISABLED)
        
        # Clear hex view
        self.hex_text.config(state=tk.NORMAL)
        self.hex_text.delete("1.0", tk.END)
        self.hex_text.config(state=tk.DISABLED)
        
        # Clear parsed tree
        for item in self.parsed_tree.get_children():
            self.parsed_tree.delete(item)
    
    def _update_header_info(self, message):
        """Update the header information"""
        # Set timestamp
        import time
        time_str = time.strftime("%H:%M:%S", time.localtime(message.timestamp))
        if hasattr(message, 'timestamp_us') and message.timestamp_us:
            time_str += f".{message.timestamp_us:06d}"
        
        self.header_values["time"].set(time_str)
        
        # Set other fields
        self.header_values["ecu_id"].set(message.ecu_id)
        self.header_values["app_id"].set(message.app_id)
        self.header_values["ctx_id"].set(message.ctx_id)
        
        # Optional fields
        session_id = getattr(message, "session_id", "N/A")
        self.header_values["session_id"].set(session_id)
        
        self.header_values["log_level"].set(message.log_level)
        
        msg_type = getattr(message, "msg_type", "N/A")
        self.header_values["msg_type"].set(msg_type)
        
        msg_id = getattr(message, "msg_id", "N/A")
        self.header_values["msg_id"].set(str(msg_id))
    
    def _update_payload_text(self, message):
        """Update the payload text view"""
        self.payload_text.config(state=tk.NORMAL)
        self.payload_text.delete("1.0", tk.END)
        
        # Insert the payload text
        self.payload_text.insert(tk.END, message.payload)
        
        # Apply syntax highlighting if possible based on content type
        if message.payload.startswith('{') and message.payload.endswith('}'):
            try:
                # Try to format as JSON
                data = json.loads(message.payload)
                formatted_json = json.dumps(data, indent=2)
                
                self.payload_text.delete("1.0", tk.END)
                self.payload_text.insert(tk.END, formatted_json)
                
                # Could add syntax highlighting here
            except json.JSONDecodeError:
                # Not valid JSON, no formatting needed
                pass
        
        self.payload_text.config(state=tk.DISABLED)
    
    def _update_hex_view(self, message):
        """Update the hex view"""
        self.hex_text.config(state=tk.NORMAL)
        self.hex_text.delete("1.0", tk.END)
        
        # Get raw bytes (if available)
        raw_data = getattr(message, "raw_data", message.payload.encode('utf-8'))
        
        # Format as hex dump with offset, hex, and ASCII representation
        offset = 0
        hex_lines = []
        
        while offset < len(raw_data):
            # Get chunk of 16 bytes
            chunk = raw_data[offset:offset+16]
            
            # Format offset
            hex_line = f"{offset:08x}  "
            
            # Format hex values
            hex_values = []
            for i, byte in enumerate(chunk):
                if isinstance(byte, int):
                    hex_values.append(f"{byte:02x}")
                else:
                    hex_values.append(f"{ord(byte):02x}")
                    
                # Add extra space in middle
                if i == 7:
                    hex_values.append(" ")
            
            # Pad if needed
            while len(hex_values) < 17:  # 16 bytes + 1 space
                hex_values.append("  ")
                if len(hex_values) == 8:
                    hex_values.append(" ")
            
            hex_line += " ".join(hex_values)
            
            # Add ASCII representation
            ascii_repr = "  |"
            for byte in chunk:
                # Get integer value
                if isinstance(byte, int):
                    val = byte
                else:
                    val = ord(byte)
                    
                # Replace non-printable chars with dots
                if 32 <= val <= 126:
                    ascii_repr += chr(val)
                else:
                    ascii_repr += "."
            
            ascii_repr += "|"
            
            # Complete the line
            hex_line += ascii_repr
            hex_lines.append(hex_line)
            
            # Move to next chunk
            offset += 16
        
        # Insert the formatted hex dump
        self.hex_text.insert(tk.END, "\n".join(hex_lines))
        self.hex_text.config(state=tk.DISABLED)
    
    def _update_parsed_view(self, message):
        """Update the parsed data view"""
        # Clear existing items
        for item in self.parsed_tree.get_children():
            self.parsed_tree.delete(item)
        
        # Add header information
        headers_node = self.parsed_tree.insert("", "end", text="Headers", open=True)
        
        for field_name, field_var in self.header_values.items():
            value = field_var.get()
            self.parsed_tree.insert(
                headers_node, 
                "end", 
                text=field_name,
                values=(value, self._get_field_type(field_name), self._get_field_desc(field_name))
            )
        
        # Try to parse structured payload if available
        payload_node = self.parsed_tree.insert("", "end", text="Payload", open=True)
        
        if hasattr(message, "parsed_payload") and message.parsed_payload:
            # If message has pre-parsed payload, use it
            self._add_parsed_fields(payload_node, message.parsed_payload)
        else:
            # Try to parse JSON payload
            if message.payload.startswith('{') and message.payload.endswith('}'):
                try:
                    data = json.loads(message.payload)
                    self._add_parsed_fields(payload_node, data)
                except json.JSONDecodeError:
                    # Not valid JSON, add as plain text
                    self.parsed_tree.insert(
                        payload_node,
                        "end",
                        text="content",
                        values=(message.payload, "text", "Message content")
                    )
            else:
                # Add as plain text
                self.parsed_tree.insert(
                    payload_node,
                    "end",
                    text="content",
                    values=(message.payload, "text", "Message content")
                )
    
    def _add_parsed_fields(self, parent_node, data, prefix=""):
        """Recursively add parsed fields to the tree"""
        if isinstance(data, dict):
            for key, value in data.items():
                node_text = f"{prefix}{key}" if prefix else key
                
                if isinstance(value, (dict, list)):
                    # Create a node for this container
                    new_node = self.parsed_tree.insert(
                        parent_node,
                        "end",
                        text=node_text,
                        values=("", self._get_type_name(value), "")
                    )
                    # Recursively add children
                    new_prefix = f"{prefix}{key}." if prefix else f"{key}."
                    self._add_parsed_fields(new_node, value, new_prefix)
                else:
                    # Add leaf node
                    self.parsed_tree.insert(
                        parent_node,
                        "end",
                        text=node_text,
                        values=(str(value), self._get_type_name(value), "")
                    )
        elif isinstance(data, list):
            for i, value in enumerate(data):
                node_text = f"{prefix}[{i}]" if prefix else f"[{i}]"
                
                if isinstance(value, (dict, list)):
                    # Create a node for this container
                    new_node = self.parsed_tree.insert(
                        parent_node,
                        "end",
                        text=node_text,
                        values=("", self._get_type_name(value), "")
                    )
                    # Recursively add children
                    new_prefix = f"{prefix}[{i}]." if prefix else f"[{i}]."
                    self._add_parsed_fields(new_node, value, new_prefix)
                else:
                    # Add leaf node
                    self.parsed_tree.insert(
                        parent_node,
                        "end",
                        text=node_text,
                        values=(str(value), self._get_type_name(value), "")
                    )
        else:
            # Just add the value directly
            self.parsed_tree.insert(
                parent_node,
                "end",
                text=prefix,
                values=(str(data), self._get_type_name(data), "")
            )
    
    def _get_type_name(self, value):
        """Get the type name of a value"""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        elif value is None:
            return "null"
        else:
            return type(value).__name__
    
    def _get_field_type(self, field_name):
        """Get the data type for a header field"""
        if field_name in ["time"]:
            return "timestamp"
        elif field_name in ["ecu_id", "app_id", "ctx_id", "session_id", "log_level", "msg_type"]:
            return "string"
        elif field_name in ["msg_id"]:
            return "integer"
        else:
            return "string"
    
    def _get_field_desc(self, field_name):
        """Get a description for a header field"""
        descriptions = {
            "time": "Timestamp when the message was logged",
            "ecu_id": "Electronic Control Unit identifier",
            "app_id": "Application identifier",
            "ctx_id": "Context identifier within the application",
            "session_id": "Session identifier for grouped messages",
            "log_level": "Severity level of the message",
            "msg_type": "Type of DLT message",
            "msg_id": "Unique message identifier"
        }
        return descriptions.get(field_name, "")
    
    def _add_bookmark(self):
        """Add the current message to bookmarks"""
        if not self.current_message:
            return
            
        # This would be implemented to save bookmarks
        self.main_window.update_status("Bookmark feature not implemented yet")
    
    def _export_message(self):
        """Export the current message to a file"""
        if not self.current_message:
            return
            
        # This would be implemented to export the message
        self.main_window.update_status("Export feature not implemented yet")
    
    def _copy_to_clipboard(self):
        """Copy message details to clipboard"""
        if not self.current_message:
            return
            
        # Get the message as formatted text
        msg = self.current_message
        
        clipboard_text = f"DLT Message Details\n\n"
        clipboard_text += f"Time: {self.header_values['time'].get()}\n"
        clipboard_text += f"ECU ID: {msg.ecu_id}\n"
        clipboard_text += f"App ID: {msg.app_id}\n"
        clipboard_text += f"Context ID: {msg.ctx_id}\n"
        clipboard_text += f"Log Level: {msg.log_level}\n"
        clipboard_text += f"\nPayload:\n{msg.payload}\n"
        
        # Copy to clipboard using tkinter
        self.parent.clipboard_clear()
        self.parent.clipboard_append(clipboard_text)
        
        self.main_window.update_status("Message copied to clipboard")