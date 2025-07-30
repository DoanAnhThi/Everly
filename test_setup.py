#!/usr/bin/env python3
"""
Test script to verify the floating AI assistant setup.
Run this before running main.py to check if everything is configured correctly.
"""

import sys
import os
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import PySide6
        print("✓ PySide6 imported successfully")
    except ImportError as e:
        print(f"✗ PySide6 import failed: {e}")
        return False
    
    try:
        import langchain
        print("✓ LangChain imported successfully")
    except ImportError as e:
        print(f"✗ LangChain import failed: {e}")
        return False
    
    try:
        import langchain_openai
        print("✓ LangChain OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ LangChain OpenAI import failed: {e}")
        return False
    
    try:
        import pyautogui
        print("✓ pyautogui imported successfully")
    except ImportError as e:
        print(f"✗ pyautogui import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Pillow import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test if environment variables are set correctly."""
    print("\nTesting environment...")
    
    # Load .env file
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ OPENAI_API_KEY not found in environment variables")
        print("  Please create a .env file with your OpenAI API key")
        return False
    elif api_key == "your_openai_api_key_here":
        print("✗ OPENAI_API_KEY is set to placeholder value")
        print("  Please replace 'your_openai_api_key_here' with your actual API key")
        return False
    else:
        print("✓ OPENAI_API_KEY is configured")
        return True

def test_modules():
    """Test if our custom modules can be imported."""
    print("\nTesting custom modules...")
    
    try:
        from agent import FloatingAppAgent
        print("✓ agent module imported successfully")
    except ImportError as e:
        print(f"✗ agent module import failed: {e}")
        return False
    
    try:
        from ui import FloatingWindow
        print("✓ ui module imported successfully")
    except ImportError as e:
        print(f"✗ ui module import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("Floating AI Assistant - Setup Test")
    print("=" * 40)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test environment
    if not test_environment():
        all_passed = False
    
    # Test modules
    if not test_modules():
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All tests passed! You can now run 'python main.py'")
    else:
        print("✗ Some tests failed. Please fix the issues above before running the app.")
        sys.exit(1)

if __name__ == "__main__":
    main() 