"""
DLT Export Manager
"""
import os
import json
import csv
from datetime import datetime

class DLTExportManager:
    """Handles exporting DLT messages in various formats"""
    
    @staticmethod
    def export_to_dlt(messages, filepath):
        """Export messages to DLT format"""
        with open(filepath, 'wb') as f:
            # Write DLT header
            f.write(b'DLT\1')  # Magic + version
            
            # Write each message's raw data
            for msg in messages:
                if msg.raw_data:
                    f.write(msg.raw_data)
                    
    @staticmethod
    def export_to_csv(messages, filepath):
        """Export messages to CSV format"""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "Timestamp", "ECU", "Application", 
                "Context", "Level", "Payload"
            ])
            
            # Write messages
            for msg in messages:
                writer.writerow([
                    msg.get_time_string(),
                    msg.ecu_id,
                    msg.app_id,
                    msg.ctx_id,
                    msg.log_level,
                    msg.payload
                ])
                
    @staticmethod
    def export_to_json(messages, filepath):
        """Export messages to JSON format"""
        data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "message_count": len(messages)
            },
            "messages": [msg.to_dict() for msg in messages]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)