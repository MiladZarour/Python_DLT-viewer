"""
Test UI Components
"""
import unittest
import tkinter as tk
from tkinter import ttk
from ui.filter_panel import FilterPanel
from ui.message_list import MessageListView
from ui.message_view import MessageDetailView
from ui.statistics_view import StatisticsView
from ui.marker_view import MarkerView
from core.dlt_message import DLTMessage

class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        
    def test_filter_panel(self):
        """Test filter panel creation"""
        main_window = type('MockMainWindow', (), {'update_status': lambda x: None})()
        panel = FilterPanel(self.root, main_window)
        self.assertIsInstance(panel, ttk.Frame)
        
    def test_message_list(self):
        """Test message list creation"""
        main_window = type('MockMainWindow', (), {'update_status': lambda x: None})()
        msg_list = MessageListView(self.root, main_window)
        self.assertIsInstance(msg_list, ttk.Frame)
        
    def test_message_view(self):
        """Test message detail view creation"""
        main_window = type('MockMainWindow', (), {'update_status': lambda x: None})()
        msg_view = MessageDetailView(self.root, main_window)
        self.assertIsInstance(msg_view, ttk.Frame)
        
        # Test displaying a message with valid data
        message = DLTMessage()
        message.payload = "Test message"
        message.raw_data = b"Test message"  # Add raw_data to prevent NoneType error
        msg_view.display_message(message)
        
    def test_statistics_view(self):
        """Test statistics view creation"""
        main_window = type('MockMainWindow', (), {'update_status': lambda x: None})()
        stats_view = StatisticsView(self.root, main_window)
        self.assertIsInstance(stats_view, ttk.Frame)
        
        # Test updating statistics
        message = DLTMessage()
        stats_view.update_stats(message)
        
    def test_marker_view(self):
        """Test marker view creation"""
        main_window = type('MockMainWindow', (), {'update_status': lambda x: None})()
        marker_view = MarkerView(self.root, main_window)
        self.assertIsInstance(marker_view, ttk.Frame)
        
        # Test adding a marker
        message = DLTMessage()
        marker_view.add_marker(message, "Test marker")

if __name__ == '__main__':
    unittest.main()