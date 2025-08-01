#!/usr/bin/env python3
"""
Simple auto-reload script for Everly development
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

class AutoReloader:
    def __init__(self):
        self.process = None
        self.last_modified = 0
        self.ui_file = Path("ui.py")
        self.start_app()
    
    def start_app(self):
        """Start the main application."""
        if self.process:
            print("🔄 Stopping previous instance...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        print("🚀 Starting Everly application...")
        self.process = subprocess.Popen([sys.executable, "main.py"])
    
    def check_for_changes(self):
        """Check if ui.py has been modified."""
        if self.ui_file.exists():
            current_modified = self.ui_file.stat().st_mtime
            if current_modified > self.last_modified:
                self.last_modified = current_modified
                print(f"📝 Detected change in ui.py")
                print("🔄 Reloading application...")
                self.start_app()
    
    def run(self):
        """Main loop to watch for changes."""
        print("🔧 Everly Auto-Reload Development Server")
        print("📁 Watching for changes in ui.py...")
        print("⏹️  Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                self.check_for_changes()
                time.sleep(1)  # Check every second
        except KeyboardInterrupt:
            print("\n⏹️  Stopping development server...")
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()

def main():
    """Main entry point."""
    reloader = AutoReloader()
    reloader.run()

if __name__ == "__main__":
    main() 