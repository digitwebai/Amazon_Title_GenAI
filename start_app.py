#!/usr/bin/env python3
"""
Simple script to start the Amazon Title Generator Streamlit app
"""

import subprocess
import sys
import os

def start_app():
    """Start the Streamlit app"""
    print("🚀 Starting Amazon Title Generator...")
    print("📝 The app will open in your browser automatically")
    print("🌐 If it doesn't open, go to: http://localhost:8503")
    print("⏹️  Press Ctrl+C to stop the app")
    print("-" * 50)
    
    try:
        # Start Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8503",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error starting app: {e}")

if __name__ == "__main__":
    start_app() 
