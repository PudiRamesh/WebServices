#!/usr/bin/env python3
"""
PowerPoint Audit Trail System
Tracks changes to PowerPoint files and maintains detailed audit logs.
"""

import os
import sqlite3
import hashlib
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pptx import Presentation
from pptx.exc import PackageNotFoundError

class PPTAuditTrail:
    """Main class for PowerPoint audit trail functionality."""
    
    def __init__(self, db_path: str = "ppt_audit.db", watch_directory: str = "."):
        """
        Initialize the audit trail system.
        
        Args:
            db_path: Path to SQLite database for storing audit logs
            watch_directory: Directory to monitor for PowerPoint files
        """
        self.db_path = db_path
        self.watch_directory = Path(watch_directory)
        self.observer = None
        self.setup_logging()
        self.setup_database()
        
    def setup_logging(self):
        """Configure logging for the audit system."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ppt_audit.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_database(self):
        """Initialize SQLite database with audit tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT NOT NULL,
                    action TEXT NOT NULL,
                    user TEXT,
                    details TEXT,
                    file_hash TEXT,
                    file_size INTEGER,
                    slide_count INTEGER,
                    change_type TEXT
                )
            ''')
            
            # Create file snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER,
                    slide_count INTEGER,
                    slide_details TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create change history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS change_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT NOT NULL,
                    old_hash TEXT,
                    new_hash TEXT,
                    change_summary TEXT,
                    detailed_changes TEXT
                )
            ''')
            
            conn.commit()
            
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
            
    def analyze_presentation(self, file_path: str) -> Dict:
        """Analyze PowerPoint presentation and extract metadata."""
        try:
            prs = Presentation(file_path)
            analysis = {
                'slide_count': len(prs.slides),
                'slide_details': [],
                'metadata': {}
            }
            
            # Analyze each slide
            for i, slide in enumerate(prs.slides):
                slide_info = {
                    'slide_number': i + 1,
                    'shapes_count': len(slide.shapes),
                    'text_boxes': 0,
                    'images': 0,
                    'charts': 0
                }
                
                for shape in slide.shapes:
                    if hasattr(shape, 'text') and shape.text.strip():
                        slide_info['text_boxes'] += 1
                    if shape.shape_type == 13:  # Picture
                        slide_info['images'] += 1
                    if shape.shape_type == 17:  # Chart
                        slide_info['charts'] += 1
                        
                analysis['slide_details'].append(slide_info)
                
            # Extract core properties if available
            if prs.core_properties:
                analysis['metadata'] = {
                    'title': prs.core_properties.title or '',
                    'author': prs.core_properties.author or '',
                    'subject': prs.core_properties.subject or '',
                    'created': str(prs.core_properties.created) if prs.core_properties.created else '',
                    'modified': str(prs.core_properties.modified) if prs.core_properties.modified else '',
                    'revision': prs.core_properties.revision or 0
                }
                
            return analysis
            
        except PackageNotFoundError:
            self.logger.warning(f"Not a valid PowerPoint file: {file_path}")
            return {'slide_count': 0, 'slide_details': [], 'metadata': {}}
        except Exception as e:
            self.logger.error(f"Error analyzing presentation {file_path}: {e}")
            return {'slide_count': 0, 'slide_details': [], 'metadata': {}}
            
    def log_audit_event(self, file_path: str, action: str, details: str = "", 
                       user: str = None, change_type: str = None):
        """Log an audit event to the database."""
        try:
            file_hash = self.calculate_file_hash(file_path)
            file_size = os.path.getsize(file_path)
            analysis = self.analyze_presentation(file_path)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO audit_log 
                    (file_path, action, user, details, file_hash, file_size, slide_count, change_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (file_path, action, user, details, file_hash, file_size, 
                     analysis['slide_count'], change_type))
                conn.commit()
                
            self.logger.info(f"Audit event logged: {action} on {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error logging audit event: {e}")
            
    def create_snapshot(self, file_path: str):
        """Create a snapshot of the current file state."""
        try:
            file_hash = self.calculate_file_hash(file_path)
            file_size = os.path.getsize(file_path)
            analysis = self.analyze_presentation(file_path)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO file_snapshots 
                    (file_path, file_hash, file_size, slide_count, slide_details, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (file_path, file_hash, file_size, analysis['slide_count'],
                     json.dumps(analysis['slide_details']), json.dumps(analysis['metadata'])))
                conn.commit()
                
            self.logger.info(f"Snapshot created for {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating snapshot: {e}")
            
    def detect_changes(self, file_path: str) -> Optional[Dict]:
        """Detect changes in a PowerPoint file by comparing with previous snapshot."""
        try:
            current_hash = self.calculate_file_hash(file_path)
            current_analysis = self.analyze_presentation(file_path)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT file_hash, slide_count, slide_details, metadata 
                    FROM file_snapshots 
                    WHERE file_path = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ''', (file_path,))
                
                result = cursor.fetchone()
                if not result:
                    return {
                        'type': 'new_file',
                        'summary': 'New file detected',
                        'details': f"File created with {current_analysis['slide_count']} slides"
                    }
                    
                old_hash, old_slide_count, old_slide_details, old_metadata = result
                
                if current_hash == old_hash:
                    return None  # No changes detected
                    
                # Parse old data
                old_slide_details = json.loads(old_slide_details) if old_slide_details else []
                old_metadata = json.loads(old_metadata) if old_metadata else {}
                
                # Analyze changes
                changes = []
                if current_analysis['slide_count'] != old_slide_count:
                    changes.append(f"Slide count changed from {old_slide_count} to {current_analysis['slide_count']}")
                    
                # Compare slide details
                for i, (old_slide, new_slide) in enumerate(zip(old_slide_details, current_analysis['slide_details'])):
                    if old_slide != new_slide:
                        changes.append(f"Slide {i+1} modified")
                        
                # Check for new slides
                if len(current_analysis['slide_details']) > len(old_slide_details):
                    changes.append(f"Added {len(current_analysis['slide_details']) - len(old_slide_details)} new slides")
                    
                return {
                    'type': 'modified',
                    'summary': '; '.join(changes),
                    'details': {
                        'old_hash': old_hash,
                        'new_hash': current_hash,
                        'changes': changes
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error detecting changes: {e}")
            return None
            
    def get_audit_report(self, file_path: str = None, start_date: str = None, 
                        end_date: str = None) -> List[Dict]:
        """Generate audit report for specified criteria."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT timestamp, file_path, action, user, details, 
                           file_size, slide_count, change_type
                    FROM audit_log
                    WHERE 1=1
                '''
                params = []
                
                if file_path:
                    query += " AND file_path = ?"
                    params.append(file_path)
                    
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date)
                    
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date)
                    
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                return [
                    {
                        'timestamp': row[0],
                        'file_path': row[1],
                        'action': row[2],
                        'user': row[3],
                        'details': row[4],
                        'file_size': row[5],
                        'slide_count': row[6],
                        'change_type': row[7]
                    }
                    for row in results
                ]
                
        except Exception as e:
            self.logger.error(f"Error generating audit report: {e}")
            return []
            
    def start_monitoring(self):
        """Start file system monitoring."""
        event_handler = PPTFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_directory), recursive=True)
        self.observer.start()
        self.logger.info(f"Started monitoring directory: {self.watch_directory}")
        
    def stop_monitoring(self):
        """Stop file system monitoring."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("Stopped monitoring")
            
    def scan_existing_files(self):
        """Scan and create snapshots for existing PowerPoint files."""
        ppt_extensions = {'.pptx', '.ppt'}
        
        for file_path in self.watch_directory.rglob('*'):
            if file_path.suffix.lower() in ppt_extensions:
                self.logger.info(f"Scanning existing file: {file_path}")
                self.create_snapshot(str(file_path))
                self.log_audit_event(str(file_path), "initial_scan", "File discovered during initial scan")


class PPTFileHandler(FileSystemEventHandler):
    """File system event handler for PowerPoint files."""
    
    def __init__(self, audit_trail: PPTAuditTrail):
        self.audit_trail = audit_trail
        self.logger = audit_trail.logger
        
    def on_created(self, event):
        if not event.is_directory and self._is_ppt_file(event.src_path):
            self.logger.info(f"File created: {event.src_path}")
            time.sleep(1)  # Wait for file to be fully written
            self.audit_trail.create_snapshot(event.src_path)
            self.audit_trail.log_audit_event(event.src_path, "file_created", "New PowerPoint file created")
            
    def on_modified(self, event):
        if not event.is_directory and self._is_ppt_file(event.src_path):
            self.logger.info(f"File modified: {event.src_path}")
            time.sleep(1)  # Wait for file to be fully written
            
            changes = self.audit_trail.detect_changes(event.src_path)
            if changes:
                self.audit_trail.create_snapshot(event.src_path)
                self.audit_trail.log_audit_event(
                    event.src_path, 
                    "file_modified", 
                    changes['summary'],
                    change_type=changes['type']
                )
                
                # Log detailed changes
                with sqlite3.connect(self.audit_trail.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO change_history 
                        (file_path, old_hash, new_hash, change_summary, detailed_changes)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (event.src_path, changes['details']['old_hash'], 
                         changes['details']['new_hash'], changes['summary'],
                         json.dumps(changes['details'])))
                    conn.commit()
                    
    def on_deleted(self, event):
        if not event.is_directory and self._is_ppt_file(event.src_path):
            self.logger.info(f"File deleted: {event.src_path}")
            self.audit_trail.log_audit_event(event.src_path, "file_deleted", "PowerPoint file deleted")
            
    def _is_ppt_file(self, file_path: str) -> bool:
        """Check if file is a PowerPoint file."""
        return Path(file_path).suffix.lower() in {'.pptx', '.ppt'}


def main():
    """Main function to run the PowerPoint audit trail system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='PowerPoint Audit Trail System')
    parser.add_argument('--watch-dir', default='.', help='Directory to monitor (default: current directory)')
    parser.add_argument('--db-path', default='ppt_audit.db', help='Database file path')
    parser.add_argument('--scan-only', action='store_true', help='Only scan existing files, don\'t monitor')
    parser.add_argument('--report', help='Generate audit report for specific file')
    parser.add_argument('--start-date', help='Start date for report (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for report (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    audit_trail = PPTAuditTrail(args.db_path, args.watch_dir)
    
    if args.report:
        # Generate report
        report = audit_trail.get_audit_report(args.report, args.start_date, args.end_date)
        print(f"\nAudit Report for: {args.report}")
        print("=" * 50)
        for entry in report:
            print(f"Time: {entry['timestamp']}")
            print(f"Action: {entry['action']}")
            print(f"Details: {entry['details']}")
            print(f"File Size: {entry['file_size']} bytes")
            print(f"Slides: {entry['slide_count']}")
            print("-" * 30)
    else:
        # Start monitoring
        print("PowerPoint Audit Trail System")
        print("=" * 30)
        print(f"Monitoring directory: {args.watch_dir}")
        print(f"Database: {args.db_path}")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            audit_trail.scan_existing_files()
            
            if not args.scan_only:
                audit_trail.start_monitoring()
                
                while True:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            audit_trail.stop_monitoring()
            print("Audit trail system stopped.")


if __name__ == "__main__":
    main()