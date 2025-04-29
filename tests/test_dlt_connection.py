"""
Test DLT Connection Module
"""
import unittest
import socket
import threading
import time
from core.dlt_connection import DLTConnection

class TestDLTConnection(unittest.TestCase):
    def setUp(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 0))
        self.port = self.server_socket.getsockname()[1]
        self.server_socket.listen(1)
        
        self.connection = DLTConnection('localhost', self.port)
        
    def tearDown(self):
        if self.connection.is_connected:
            self.connection.disconnect()
        self.server_socket.close()
        
    def test_connect(self):
        """Test connection establishment"""
        # Start server thread
        server_thread = threading.Thread(target=self._accept_connection)
        server_thread.daemon = True
        server_thread.start()
        
        # Connect client
        result = self.connection.connect()
        self.assertTrue(result)
        self.assertTrue(self.connection.is_connected)
        
    def test_disconnect(self):
        """Test disconnection"""
        # Connect first
        server_thread = threading.Thread(target=self._accept_connection)
        server_thread.daemon = True
        server_thread.start()
        
        self.connection.connect()
        time.sleep(0.1)  # Allow connection to establish
        
        # Test disconnect
        self.connection.disconnect()
        self.assertFalse(self.connection.is_connected)
        
    def test_callbacks(self):
        """Test message callbacks"""
        received_messages = []
        
        def callback(message):
            received_messages.append(message)
            
        self.connection.add_callback(callback)
        
        # Verify callback is registered
        self.assertIn(callback, self.connection.callbacks)
        
        # Remove callback
        self.connection.remove_callback(callback)
        self.assertNotIn(callback, self.connection.callbacks)
        
    def _accept_connection(self):
        """Helper to accept test connections"""
        client_socket, _ = self.server_socket.accept()
        client_socket.close()

if __name__ == '__main__':
    unittest.main()