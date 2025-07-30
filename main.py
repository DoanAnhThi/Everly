#!/usr/bin/env python3
"""
Floating AI Assistant - A desktop app that analyzes screenshots using GPT-4o Vision

This app provides a small, frameless, always-on-top floating window where users can
type questions and get AI analysis of their current screen using LangChain and GPT-4o.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from ui import FloatingWindow

def check_environment():
    """Check if required environment variables are set."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    return True

def main():
    """Main application entry point."""
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Floating AI Assistant")
    app.setApplicationVersion("1.0.0")
    
    # Create and show the floating window
    window = FloatingWindow()
    window.show()
    
    # Set focus to input field
    window.input_field.setFocus()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 