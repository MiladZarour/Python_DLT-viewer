"""
DLT Statistics Manager
"""
from datetime import datetime, timedelta
from collections import defaultdict

class DLTStatistics:
    """Class for collecting and analyzing DLT message statistics"""
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        """Reset all statistics"""
        self.total_messages = 0
        self.start_time = datetime.now()
        self.bytes_received = 0
        self.msg_per_second = 0.0
        self.bytes_per_second = 0.0
        
        # Counters
        self.ecu_counts = defaultdict(int)
        self.app_counts = defaultdict(int)
        self.ctx_counts = defaultdict(int)
        self.level_counts = defaultdict(int)
        
        # Time-based stats
        self.messages_by_hour = defaultdict(int)
        self.bytes_by_hour = defaultdict(int)
        
        # Performance metrics
        self.min_processing_time = float('inf')
        self.max_processing_time = 0
        self.total_processing_time = 0
        
    def update(self, message, processing_time=None):
        """Update statistics with new message"""
        self.total_messages += 1
        self.bytes_received += len(message.raw_data) if message.raw_data else 0
        
        # Update counters
        self.ecu_counts[message.ecu_id] += 1
        self.app_counts[message.app_id] += 1
        self.ctx_counts[message.ctx_id] += 1
        self.level_counts[message.log_level] += 1
        
        # Update time-based stats
        hour = datetime.fromtimestamp(message.timestamp).strftime('%Y-%m-%d %H:00')
        self.messages_by_hour[hour] += 1
        self.bytes_by_hour[hour] += len(message.raw_data) if message.raw_data else 0
        
        # Update performance metrics
        if processing_time is not None:
            self.min_processing_time = min(self.min_processing_time, processing_time)
            self.max_processing_time = max(self.max_processing_time, processing_time)
            self.total_processing_time += processing_time
            
        # Calculate rates
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed > 0:
            self.msg_per_second = self.total_messages / elapsed
            self.bytes_per_second = self.bytes_received / elapsed
            
    def get_summary(self):
        """Get statistics summary"""
        return {
            "total_messages": self.total_messages,
            "bytes_received": self.bytes_received,
            "duration": str(datetime.now() - self.start_time),
            "msg_per_second": round(self.msg_per_second, 2),
            "bytes_per_second": round(self.bytes_per_second, 2),
            "ecu_distribution": dict(self.ecu_counts),
            "app_distribution": dict(self.app_counts),
            "level_distribution": dict(self.level_counts),
            "performance": {
                "min_processing_time": round(self.min_processing_time, 6),
                "max_processing_time": round(self.max_processing_time, 6),
                "avg_processing_time": round(self.total_processing_time / self.total_messages, 6)
                if self.total_messages > 0 else 0
            }
        }