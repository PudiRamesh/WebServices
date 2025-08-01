#!/usr/bin/env python3
"""
PowerPoint Audit Trail System Startup Script
Runs both the audit trail monitoring and web dashboard.
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\nShutting down PowerPoint Audit Trail System...")
    sys.exit(0)

def run_audit_trail(watch_dir=".", db_path="ppt_audit.db"):
    """Run the audit trail monitoring process."""
    try:
        cmd = [sys.executable, "ppt_audit_trail.py", "--watch-dir", watch_dir, "--db-path", db_path]
        print(f"Starting audit trail monitoring for directory: {watch_dir}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Stream output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"[AUDIT] {output.strip()}")
                
        return process.poll()
    except Exception as e:
        print(f"Error starting audit trail: {e}")
        return 1

def run_dashboard(port=5000):
    """Run the web dashboard process."""
    try:
        # Set environment variables
        env = os.environ.copy()
        env['FLASK_ENV'] = 'development'
        
        cmd = [sys.executable, "audit_dashboard.py"]
        print(f"Starting web dashboard on port: {port}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        
        # Stream output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"[DASHBOARD] {output.strip()}")
                
        return process.poll()
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        return 1

def main():
    """Main function to start both services."""
    import argparse
    
    parser = argparse.ArgumentParser(description='PowerPoint Audit Trail System Startup')
    parser.add_argument('--watch-dir', default='.', help='Directory to monitor (default: current directory)')
    parser.add_argument('--db-path', default='ppt_audit.db', help='Database file path')
    parser.add_argument('--port', type=int, default=5000, help='Dashboard port (default: 5000)')
    parser.add_argument('--audit-only', action='store_true', help='Run only audit trail monitoring')
    parser.add_argument('--dashboard-only', action='store_true', help='Run only web dashboard')
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("PowerPoint Audit Trail System")
    print("=" * 40)
    print(f"Watch Directory: {args.watch_dir}")
    print(f"Database: {args.db_path}")
    print(f"Dashboard Port: {args.port}")
    print("=" * 40)
    
    # Check if required files exist
    if not Path("ppt_audit_trail.py").exists():
        print("Error: ppt_audit_trail.py not found!")
        sys.exit(1)
    
    if not Path("audit_dashboard.py").exists():
        print("Error: audit_dashboard.py not found!")
        sys.exit(1)
    
    # Create watch directory if it doesn't exist
    watch_path = Path(args.watch_dir)
    if not watch_path.exists():
        print(f"Creating watch directory: {args.watch_dir}")
        watch_path.mkdir(parents=True, exist_ok=True)
    
    processes = []
    
    try:
        if not args.dashboard_only:
            # Start audit trail in a separate thread
            audit_thread = threading.Thread(
                target=run_audit_trail,
                args=(args.watch_dir, args.db_path),
                daemon=True
            )
            audit_thread.start()
            processes.append(audit_thread)
            print("Audit trail monitoring started")
        
        if not args.audit_only:
            # Give audit trail a moment to initialize
            time.sleep(2)
            
            # Start dashboard in a separate thread
            dashboard_thread = threading.Thread(
                target=run_dashboard,
                args=(args.port,),
                daemon=True
            )
            dashboard_thread.start()
            processes.append(dashboard_thread)
            print("Web dashboard started")
        
        print("\nSystem is running...")
        print("Press Ctrl+C to stop")
        
        if not args.audit_only:
            print(f"\nDashboard available at: http://localhost:{args.port}")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()