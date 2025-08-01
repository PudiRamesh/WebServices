#!/usr/bin/env python3
"""
PowerPoint Audit Trail System
Tracks changes to PowerPoint files and maintains a detailed audit log.
"""

import os
import sqlite3
import hashlib
import json
import logging
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pptx import Presentation
from pptx.exc import PackageNotFoundError

class PowerPointAuditTrail:
    def __init__(self, watch_directory=".", db_path="audit_trail.db"):
        """
        Initialize the PowerPoint audit trail system.
        
        Args:
            watch_directory (str): Directory to monitor for PowerPoint files
            db_path (str): Path to SQLite database for storing audit logs
        """
        self.watch_directory = Path(watch_directory).resolve()
        self.db_path = db_path
        self.backup_directory = self.watch_directory / "audit_backups"
        self.backup_directory.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize database
        self.init_database()
        
        # File monitoring
        self.observer = Observer()
        self.event_handler = PowerPointEventHandler(self)
        
    def setup_logging(self):
        """Configure logging for the audit system."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('audit_trail.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def init_database(self):
        """Initialize SQLite database with audit tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                file_hash TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create changes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                change_type TEXT NOT NULL,
                change_description TEXT,
                old_hash TEXT,
                new_hash TEXT,
                backup_path TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_info TEXT,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        ''')
        
        # Create slides table for detailed slide tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS slides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                slide_number INTEGER,
                slide_hash TEXT,
                slide_content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("Database initialized successfully")
        
    def calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return None
            
    def extract_presentation_info(self, file_path):
        """Extract detailed information from PowerPoint file."""
        try:
            prs = Presentation(file_path)
            info = {
                'slide_count': len(prs.slides),
                'slides': []
            }
            
            for i, slide in enumerate(prs.slides):
                slide_content = []
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        slide_content.append(shape.text)
                
                slide_info = {
                    'slide_number': i + 1,
                    'content': ' '.join(slide_content),
                    'shape_count': len(slide.shapes)
                }
                info['slides'].append(slide_info)
                
            return info
        except PackageNotFoundError:
            self.logger.warning(f"Invalid PowerPoint file: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting presentation info from {file_path}: {e}")
            return None
            
    def backup_file(self, file_path):
        """Create a backup of the PowerPoint file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = Path(file_path).name
            backup_name = f"{timestamp}_{file_name}"
            backup_path = self.backup_directory / backup_name
            
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            self.logger.error(f"Error creating backup for {file_path}: {e}")
            return None
            
    def log_file_change(self, file_path, change_type, change_description=""):
        """Log a file change to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            file_hash = self.calculate_file_hash(file_path)
            file_size = os.path.getsize(file_path)
            file_name = Path(file_path).name
            
            # Check if file exists in database
            cursor.execute("SELECT id FROM files WHERE file_path = ?", (str(file_path),))
            file_record = cursor.fetchone()
            
            if file_record:
                file_id = file_record[0]
                # Update file record
                cursor.execute('''
                    UPDATE files 
                    SET file_size = ?, file_hash = ?, last_modified = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (file_size, file_hash, file_id))
            else:
                # Insert new file record
                cursor.execute('''
                    INSERT INTO files (file_path, file_name, file_size, file_hash)
                    VALUES (?, ?, ?, ?)
                ''', (str(file_path), file_name, file_size, file_hash))
                file_id = cursor.lastrowid
                
            # Create backup
            backup_path = self.backup_file(file_path)
            
            # Log the change
            cursor.execute('''
                INSERT INTO changes (file_id, change_type, change_description, new_hash, backup_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (file_id, change_type, change_description, file_hash, backup_path))
            
            # Extract and log slide information
            presentation_info = self.extract_presentation_info(file_path)
            if presentation_info:
                for slide_info in presentation_info['slides']:
                    slide_hash = hashlib.sha256(slide_info['content'].encode()).hexdigest()
                    cursor.execute('''
                        INSERT INTO slides (file_id, slide_number, slide_hash, slide_content)
                        VALUES (?, ?, ?, ?)
                    ''', (file_id, slide_info['slide_number'], slide_hash, slide_info['content']))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Logged {change_type} for {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error logging file change: {e}")
            
    def start_monitoring(self):
        """Start monitoring the directory for PowerPoint files."""
        self.observer.schedule(self.event_handler, str(self.watch_directory), recursive=True)
        self.observer.start()
        self.logger.info(f"Started monitoring directory: {self.watch_directory}")
        
        # Initial scan of existing files
        self.scan_existing_files()
        
    def stop_monitoring(self):
        """Stop monitoring the directory."""
        self.observer.stop()
        self.observer.join()
        self.logger.info("Stopped monitoring")
        
    def scan_existing_files(self):
        """Scan for existing PowerPoint files in the directory."""
        ppt_extensions = ['.pptx', '.ppt']
        
        for file_path in self.watch_directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ppt_extensions:
                self.logger.info(f"Found existing PowerPoint file: {file_path}")
                self.log_file_change(file_path, "INITIAL_SCAN", "File discovered during initial scan")
                
    def generate_audit_report(self, output_file="audit_report.html"):
        """Generate a comprehensive HTML audit report."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all files and their changes
        cursor.execute('''
            SELECT f.file_name, f.file_path, f.first_seen, f.last_modified, f.file_size,
                   COUNT(c.id) as change_count
            FROM files f
            LEFT JOIN changes c ON f.id = c.file_id
            GROUP BY f.id
            ORDER BY f.last_modified DESC
        ''')
        files = cursor.fetchall()
        
        # Get recent changes
        cursor.execute('''
            SELECT f.file_name, c.change_type, c.change_description, c.timestamp
            FROM changes c
            JOIN files f ON c.file_id = f.id
            ORDER BY c.timestamp DESC
            LIMIT 50
        ''')
        recent_changes = cursor.fetchall()
        
        conn.close()
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PowerPoint Audit Trail Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .change-type {{ font-weight: bold; }}
                .created {{ color: green; }}
                .modified {{ color: orange; }}
                .deleted {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PowerPoint Audit Trail Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Monitoring Directory: {self.watch_directory}</p>
            </div>
            
            <div class="section">
                <h2>Tracked Files ({len(files)})</h2>
                <table>
                    <tr>
                        <th>File Name</th>
                        <th>Path</th>
                        <th>First Seen</th>
                        <th>Last Modified</th>
                        <th>Size (bytes)</th>
                        <th>Change Count</th>
                    </tr>
        """
        
        for file_info in files:
            html_content += f"""
                    <tr>
                        <td>{file_info[0]}</td>
                        <td>{file_info[1]}</td>
                        <td>{file_info[2]}</td>
                        <td>{file_info[3]}</td>
                        <td>{file_info[4]}</td>
                        <td>{file_info[5]}</td>
                    </tr>
            """
            
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Recent Changes</h2>
                <table>
                    <tr>
                        <th>File Name</th>
                        <th>Change Type</th>
                        <th>Description</th>
                        <th>Timestamp</th>
                    </tr>
        """
        
        for change in recent_changes:
            change_class = change[1].lower().replace('_', '-')
            html_content += f"""
                    <tr>
                        <td>{change[0]}</td>
                        <td class="change-type {change_class}">{change[1]}</td>
                        <td>{change[2] or ''}</td>
                        <td>{change[3]}</td>
                    </tr>
            """
            
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
            
        self.logger.info(f"Audit report generated: {output_file}")


class PowerPointEventHandler(FileSystemEventHandler):
    def __init__(self, audit_system):
        self.audit_system = audit_system
        
    def on_created(self, event):
        if not event.is_directory and self._is_powerpoint_file(event.src_path):
            self.audit_system.log_file_change(event.src_path, "FILE_CREATED", "New PowerPoint file created")
            
    def on_modified(self, event):
        if not event.is_directory and self._is_powerpoint_file(event.src_path):
            self.audit_system.log_file_change(event.src_path, "FILE_MODIFIED", "PowerPoint file modified")
            
    def on_deleted(self, event):
        if not event.is_directory and self._is_powerpoint_file(event.src_path):
            self.audit_system.log_file_change(event.src_path, "FILE_DELETED", "PowerPoint file deleted")
            
    def on_moved(self, event):
        if not event.is_directory and self._is_powerpoint_file(event.src_path):
            self.audit_system.log_file_change(event.src_path, "FILE_MOVED", f"PowerPoint file moved to {event.src_path}")
            
    def _is_powerpoint_file(self, file_path):
        """Check if the file is a PowerPoint file."""
        return Path(file_path).suffix.lower() in ['.pptx', '.ppt']


def main():
    """Main function to run the PowerPoint audit trail system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerPoint Audit Trail System")
    parser.add_argument("--watch", default=".", help="Directory to monitor (default: current directory)")
    parser.add_argument("--db", default="audit_trail.db", help="Database file path (default: audit_trail.db)")
    parser.add_argument("--report", default="audit_report.html", help="Report output file (default: audit_report.html)")
    
    args = parser.parse_args()
    
    print("PowerPoint Audit Trail System")
    print("=" * 40)
    
    # Initialize the audit system
    audit_system = PowerPointAuditTrail(watch_directory=args.watch, db_path=args.db)
    
    try:
        # Start monitoring
        audit_system.start_monitoring()
        
        print(f"Monitoring directory: {audit_system.watch_directory}")
        print("Press Ctrl+C to stop monitoring and generate report...")
        
        # Keep the system running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        audit_system.stop_monitoring()
        
        # Generate final report
        print("Generating audit report...")
        audit_system.generate_audit_report(args.report)
        
        print(f"Audit trail system stopped. Check {args.report} for the report.")


if __name__ == "__main__":
    main()