#!/usr/bin/env python3
"""
EcoScrap Cheat Sheet - HTML to PDF Converter
=============================================

This script converts the HTML cheat sheet to PDF format for easy sharing
and offline reference. It uses weasyprint for high-quality PDF generation.

Requirements:
    pip install weasyprint

Usage:
    python3 convert_to_pdf.py

Output:
    ECOSCRAP_CHEATSHEET.pdf
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import weasyprint
        return True
    except ImportError:
        print("❌ WeasyPrint not found. Installing...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
            print("✅ WeasyPrint installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install WeasyPrint")
            print("Please install manually: pip install weasyprint")
            return False

def convert_html_to_pdf():
    """Convert HTML cheat sheet to PDF"""
    try:
        import weasyprint
        
        # File paths
        html_file = "ECOSCRAP_CHEATSHEET.html"
        pdf_file = "ECOSCRAP_CHEATSHEET.pdf"
        
        # Check if HTML file exists
        if not os.path.exists(html_file):
            print(f"❌ HTML file '{html_file}' not found!")
            return False
        
        print(f"📖 Converting {html_file} to PDF...")
        
        # Convert HTML to PDF
        weasyprint.HTML(filename=html_file).write_pdf(pdf_file)
        
        # Check if PDF was created successfully
        if os.path.exists(pdf_file):
            file_size = os.path.getsize(pdf_file) / (1024 * 1024)  # Size in MB
            print(f"✅ PDF created successfully: {pdf_file}")
            print(f"📊 File size: {file_size:.2f} MB")
            print(f"📁 Location: {os.path.abspath(pdf_file)}")
            return True
        else:
            print("❌ PDF creation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        return False

def main():
    """Main function"""
    print("♻️ EcoScrap Cheat Sheet - HTML to PDF Converter")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot proceed without WeasyPrint")
        sys.exit(1)
    
    # Convert HTML to PDF
    if convert_html_to_pdf():
        print("\n🎉 Conversion completed successfully!")
        print("\n📚 The PDF cheat sheet contains:")
        print("   • Complete project overview")
        print("   • Modular architecture guide")
        print("   • Database models & relationships")
        print("   • Authentication & security system")
        print("   • API endpoints & business logic")
        print("   • Frontend architecture")
        print("   • Application workflows & algorithms")
        print("   • Deployment & configuration")
        print("   • Development workflow & best practices")
        print("   • Quick reference commands")
        print("\n💡 You can now share the PDF with your team!")
    else:
        print("\n❌ Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
