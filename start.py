#!/usr/bin/env python3
"""
EcoScrap Application - Startup Script
=====================================

This script provides an easy way to start the EcoScrap application
from the root directory. It automatically navigates to the correct
backend directory and starts the application.

Usage:
    python3 start.py                    # Start modular version (recommended)
    python3 start.py --original         # Start original monolithic version
    python3 start.py --help             # Show help information
"""

import os
import sys
import subprocess
import argparse

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description='Start EcoScrap Application')
    parser.add_argument('--original', action='store_true', 
                       help='Start original monolithic version instead of modular')
    
    args = parser.parse_args()
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, 'ecoscrap')
    
    # Check if backend directory exists
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        print(f"Expected: {backend_dir}")
        sys.exit(1)
    
    # Change to backend directory
    os.chdir(backend_dir)
    print(f"📁 Changed to backend directory: {backend_dir}")
    
    # Determine which application to run
    if args.original:
        app_file = "app.py"
        print("🚀 Starting original monolithic application...")
    else:
        app_file = "app_modular.py"
        print("🚀 Starting modular application (recommended)...")
    
    # Check if the application file exists
    if not os.path.exists(app_file):
        print(f"❌ Application file not found: {app_file}")
        sys.exit(1)
    
    # Start the application
    try:
        print(f"🎯 Running: python3 {app_file}")
        print("📍 Application will be available at: http://localhost:5001")
        print("🛑 Press Ctrl+C to stop the application")
        print("-" * 50)
        
        # Run the application
        subprocess.run([sys.executable, app_file])
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
