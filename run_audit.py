#!/usr/bin/env python3
"""
PowerPoint Audit Trail System Launcher
Simple launcher script with menu options.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print the system banner."""
    print("=" * 60)
    print("           PowerPoint Audit Trail System")
    print("=" * 60)
    print("A comprehensive system for tracking PowerPoint file changes")
    print("with detailed audit logging, automatic backups, and reporting.")
    print("=" * 60)

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pptx
        import watchdog
        print("✓ Dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def start_monitoring():
    """Start the monitoring system."""
    print("\nStarting PowerPoint Audit Trail Monitoring...")
    print("Press Ctrl+C to stop monitoring and generate report.")
    print("-" * 50)
    
    try:
        # Get monitoring directory
        directory = input("Enter directory to monitor (or press Enter for current directory): ").strip()
        if not directory:
            directory = "."
        
        # Validate directory
        if not os.path.exists(directory):
            print(f"Error: Directory '{directory}' does not exist.")
            return
        
        # Start monitoring
        cmd = [sys.executable, "ppt_audit_trail.py", "--watch", directory]
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except Exception as e:
        print(f"Error starting monitoring: {e}")

def query_audit_data():
    """Query audit data."""
    print("\nPowerPoint Audit Trail Query")
    print("-" * 30)
    
    if not os.path.exists("audit_trail.db"):
        print("No audit database found. Please run monitoring first.")
        return
    
    print("Available queries:")
    print("1. Show recent changes")
    print("2. List all tracked files")
    print("3. Show file history")
    print("4. Show statistics")
    print("5. Export to CSV")
    print("6. Back to main menu")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == "1":
        limit = input("Number of recent changes to show (default 20): ").strip()
        limit = limit if limit else "20"
        subprocess.run([sys.executable, "audit_query.py", "--recent", limit])
    elif choice == "2":
        subprocess.run([sys.executable, "audit_query.py", "--list-files"])
    elif choice == "3":
        file_name = input("Enter file name: ").strip()
        if file_name:
            subprocess.run([sys.executable, "audit_query.py", "--file-history", file_name])
    elif choice == "4":
        subprocess.run([sys.executable, "audit_query.py", "--stats"])
    elif choice == "5":
        output_file = input("Enter output file name (default: audit_export.csv): ").strip()
        output_file = output_file if output_file else "audit_export.csv"
        subprocess.run([sys.executable, "audit_query.py", "--export", output_file])
    elif choice == "6":
        return
    else:
        print("Invalid option.")

def run_tests():
    """Run the test suite."""
    print("\nRunning PowerPoint Audit Trail System Tests...")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "test_audit_system.py"])
    except Exception as e:
        print(f"Error running tests: {e}")

def show_help():
    """Show help information."""
    print("\nPowerPoint Audit Trail System Help")
    print("-" * 40)
    print("This system monitors PowerPoint files (.pptx, .ppt) and tracks:")
    print("• File creation, modification, deletion, and movement")
    print("• Automatic backups before changes")
    print("• Content extraction and slide-level tracking")
    print("• Detailed audit logs in SQLite database")
    print("• HTML reports and CSV exports")
    print()
    print("Files created by the system:")
    print("• audit_trail.db - SQLite database with audit data")
    print("• audit_trail.log - Application log file")
    print("• audit_backups/ - Directory containing file backups")
    print("• audit_report.html - Generated HTML audit report")
    print()
    print("For more information, see README.md")

def main_menu():
    """Display the main menu."""
    while True:
        print("\n" + "=" * 60)
        print("Main Menu")
        print("=" * 60)
        print("1. Start Monitoring")
        print("2. Query Audit Data")
        print("3. Run Tests")
        print("4. Help")
        print("5. Exit")
        print("=" * 60)
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            start_monitoring()
        elif choice == "2":
            query_audit_data()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            show_help()
        elif choice == "5":
            print("\nThank you for using PowerPoint Audit Trail System!")
            break
        else:
            print("Invalid option. Please select 1-5.")

def main():
    """Main function."""
    print_banner()
    
    if not check_dependencies():
        return
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()