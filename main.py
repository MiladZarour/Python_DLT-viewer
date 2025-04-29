#!/usr/bin/env python3
"""
Python DLT Viewer - Main Application Entry Point
"""
import sys
import os
from ui.app import DLTViewerApp
from utils.config import load_config, save_config
from utils.logger import setup_logger

def main():
    """Main entry point for the DLT Viewer application"""
    # Set up logging
    logger = setup_logger()
    logger.info("Starting Python DLT Viewer")
    
    # Load configuration
    config = load_config()
    
    # Start the application
    app = DLTViewerApp(config)
    
    # Run the main loop
    try:
        app.run()
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        raise
    finally:
        # Save configuration on exit
        save_config(config)
        logger.info("DLT Viewer shutting down")

if __name__ == "__main__":
    main()