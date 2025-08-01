#!/usr/bin/env python3
"""
PowerPoint Audit Trail System
============================

A comprehensive audit trail system for PowerPoint files that tracks:
- File access and modifications
- Metadata changes
- Version history
- User activities
- Content changes

Author: Auto-generated
Version: 1.0.0
"""

import os
import json
import hashlib
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pptx import Presentation
from pptx.exc import PackageNotFoundError
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

console = Console()

@dataclass
class AuditEvent:
    """Represents an audit event for a PowerPoint file."""
    timestamp: str
    event_type: str
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    user: str
    metadata: Dict[str, Any]
    changes: List[str]
    version: int

class PPTMetadataExtractor:
    """Extracts metadata from PowerPoint files."""
    
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from a PowerPoint file."""
        try:
            prs = Presentation(file_path)
            
            # Core properties
            core_props = prs.core_properties
            metadata = {
                'title': core_props.title or '',
                'author': core_props.author or '',
                'subject': core_props.subject or '',
                'keywords': core_props.keywords or '',
                'comments': core_props.comments or '',
                'category': core_props.category or '',
                'created': core_props.created.isoformat() if core_props.created else '',
                'modified': core_props.modified.isoformat() if core_props.modified else '',
                'last_modified_by': core_props.last_modified_by or '',
                'revision': core_props.revision or 0,
                'version': core_props.version or '',
                'language': core_props.language or '',
                'identifier': core_props.identifier or ''
            }
            
            # Presentation structure
            slides_info = []
            for i, slide in enumerate(prs.slides):
                slide_info = {
                    'slide_number': i + 1,
                    'layout_name': slide.slide_layout.name if hasattr(slide.slide_layout, 'name') else 'Unknown',
                    'shapes_count': len(slide.shapes),
                    'has_notes': bool(slide.notes_slide.notes_text_frame.text.strip()) if slide.notes_slide else False
                }
                
                # Count different shape types
                shape_types = {}
                for shape in slide.shapes:
                    shape_type = str(shape.shape_type)
                    shape_types[shape_type] = shape_types.get(shape_type, 0) + 1
                
                slide_info['shape_types'] = shape_types
                slides_info.append(slide_info)
            
            metadata.update({
                'slide_count': len(prs.slides),
                'slide_layouts_count': len(prs.slide_layouts),
                'slides_info': slides_info,
                'presentation_size': f"{prs.slide_width} x {prs.slide_height}"
            })
            
            return metadata
            
        except (PackageNotFoundError, Exception) as e:
            return {
                'error': f"Failed to extract metadata: {str(e)}",
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

class PPTAuditDatabase:
    """Manages the audit trail database."""
    
    def __init__(self, db_path: str = "ppt_audit.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the audit database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Audit events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                file_hash TEXT,
                user TEXT,
                metadata TEXT,
                changes TEXT,
                version INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # File versions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                version INTEGER NOT NULL,
                hash TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User activity table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                file_path TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_event(self, event: AuditEvent):
        """Log an audit event to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_events 
            (timestamp, event_type, file_path, file_name, file_size, file_hash, 
             user, metadata, changes, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            event.event_type,
            event.file_path,
            event.file_name,
            event.file_size,
            event.file_hash,
            event.user,
            json.dumps(event.metadata),
            json.dumps(event.changes),
            event.version
        ))
        
        conn.commit()
        conn.close()
    
    def get_file_history(self, file_path: str) -> List[Dict]:
        """Get the complete history for a specific file."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM audit_events 
            WHERE file_path = ? 
            ORDER BY timestamp DESC
        ''', (file_path,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_user_activity(self, user: str = None, limit: int = 100) -> List[Dict]:
        """Get user activity logs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user:
            cursor.execute('''
                SELECT * FROM audit_events 
                WHERE user = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user, limit))
        else:
            cursor.execute('''
                SELECT * FROM audit_events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results

class PPTFileWatcher(FileSystemEventHandler):
    """Watches PowerPoint files for changes."""
    
    def __init__(self, audit_db: PPTAuditDatabase):
        self.audit_db = audit_db
        self.metadata_extractor = PPTMetadataExtractor()
        self.file_versions = {}  # Track file versions
        
    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def is_ppt_file(self, file_path: str) -> bool:
        """Check if file is a PowerPoint file."""
        ppt_extensions = {'.ppt', '.pptx', '.pptm', '.ppsx', '.ppsm'}
        return Path(file_path).suffix.lower() in ppt_extensions
    
    def create_audit_event(self, event_type: str, file_path: str) -> Optional[AuditEvent]:
        """Create an audit event for a file."""
        if not os.path.exists(file_path):
            return None
            
        try:
            stat = os.stat(file_path)
            file_hash = self.get_file_hash(file_path)
            metadata = self.metadata_extractor.extract_metadata(file_path)
            
            # Determine version number
            current_version = self.file_versions.get(file_path, 0)
            if event_type in ['modified', 'created']:
                current_version += 1
                self.file_versions[file_path] = current_version
            
            # Detect changes (simplified)
            changes = []
            if event_type == 'modified':
                changes.append("File content modified")
            elif event_type == 'created':
                changes.append("File created")
            
            return AuditEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                file_path=file_path,
                file_name=os.path.basename(file_path),
                file_size=stat.st_size,
                file_hash=file_hash,
                user=os.getenv('USER', 'unknown'),
                metadata=metadata,
                changes=changes,
                version=current_version
            )
        except Exception as e:
            console.print(f"[red]Error creating audit event: {e}[/red]")
            return None
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and self.is_ppt_file(event.src_path):
            audit_event = self.create_audit_event('created', event.src_path)
            if audit_event:
                self.audit_db.log_event(audit_event)
                console.print(f"[green]✓[/green] Logged creation: {os.path.basename(event.src_path)}")
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and self.is_ppt_file(event.src_path):
            audit_event = self.create_audit_event('modified', event.src_path)
            if audit_event:
                self.audit_db.log_event(audit_event)
                console.print(f"[yellow]✓[/yellow] Logged modification: {os.path.basename(event.src_path)}")
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory and self.is_ppt_file(event.src_path):
            # For deleted files, we can't extract metadata
            audit_event = AuditEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type='deleted',
                file_path=event.src_path,
                file_name=os.path.basename(event.src_path),
                file_size=0,
                file_hash='',
                user=os.getenv('USER', 'unknown'),
                metadata={'deleted': True},
                changes=['File deleted'],
                version=self.file_versions.get(event.src_path, 0)
            )
            self.audit_db.log_event(audit_event)
            console.print(f"[red]✓[/red] Logged deletion: {os.path.basename(event.src_path)}")

class PPTAuditTrail:
    """Main audit trail controller."""
    
    def __init__(self, watch_directory: str = ".", db_path: str = "ppt_audit.db"):
        self.watch_directory = Path(watch_directory).resolve()
        self.audit_db = PPTAuditDatabase(db_path)
        self.file_watcher = PPTFileWatcher(self.audit_db)
        self.observer = Observer()
        
    def start_monitoring(self):
        """Start monitoring the directory for PowerPoint file changes."""
        console.print(Panel(
            f"[bold green]Starting PowerPoint Audit Trail[/bold green]\n"
            f"Monitoring directory: {self.watch_directory}\n"
            f"Database: {self.audit_db.db_path}",
            title="PPT Audit Trail",
            border_style="green"
        ))
        
        self.observer.schedule(
            self.file_watcher, 
            str(self.watch_directory), 
            recursive=True
        )
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring."""
        console.print("[yellow]Stopping audit trail monitoring...[/yellow]")
        self.observer.stop()
        self.observer.join()
        console.print("[green]✓ Audit trail stopped[/green]")
    
    def scan_existing_files(self):
        """Scan existing PowerPoint files and create audit entries."""
        console.print("[blue]Scanning existing PowerPoint files...[/blue]")
        
        ppt_files = []
        for ext in ['*.ppt', '*.pptx', '*.pptm', '*.ppsx', '*.ppsm']:
            ppt_files.extend(self.watch_directory.rglob(ext))
        
        if not ppt_files:
            console.print("[yellow]No PowerPoint files found in the directory.[/yellow]")
            return
        
        for file_path in track(ppt_files, description="Processing files..."):
            if file_path.is_file():
                audit_event = self.file_watcher.create_audit_event('scanned', str(file_path))
                if audit_event:
                    self.audit_db.log_event(audit_event)
        
        console.print(f"[green]✓ Scanned {len(ppt_files)} PowerPoint files[/green]")

# CLI Interface
@click.group()
def cli():
    """PowerPoint Audit Trail System"""
    pass

@cli.command()
@click.option('--directory', '-d', default='.', help='Directory to monitor')
@click.option('--database', '-db', default='ppt_audit.db', help='Database file path')
def monitor(directory, database):
    """Start monitoring PowerPoint files for changes."""
    audit_trail = PPTAuditTrail(directory, database)
    audit_trail.scan_existing_files()
    audit_trail.start_monitoring()

@cli.command()
@click.option('--database', '-db', default='ppt_audit.db', help='Database file path')
@click.option('--file-path', '-f', help='Specific file path to show history for')
@click.option('--limit', '-l', default=50, help='Number of recent events to show')
def history(database, file_path, limit):
    """Show audit history for PowerPoint files."""
    audit_db = PPTAuditDatabase(database)
    
    if file_path:
        events = audit_db.get_file_history(file_path)
        title = f"History for {os.path.basename(file_path)}"
    else:
        events = audit_db.get_user_activity(limit=limit)
        title = f"Recent Audit Events (Last {limit})"
    
    if not events:
        console.print("[yellow]No audit events found.[/yellow]")
        return
    
    table = Table(title=title)
    table.add_column("Timestamp")
    table.add_column("Event")
    table.add_column("File")
    table.add_column("User")
    table.add_column("Version")
    table.add_column("Size")
    
    for event in events:
        timestamp = datetime.fromisoformat(event['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        file_size = f"{event['file_size']:,} bytes" if event['file_size'] else "N/A"
        
        table.add_row(
            timestamp,
            event['event_type'],
            os.path.basename(event['file_name']),
            event['user'] or 'Unknown',
            str(event['version']),
            file_size
        )
    
    console.print(table)

@cli.command()
@click.argument('file_path')
@click.option('--database', '-db', default='ppt_audit.db', help='Database file path')
def analyze(file_path, database):
    """Analyze a specific PowerPoint file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Error: File '{file_path}' not found.[/red]")
        return
    
    extractor = PPTMetadataExtractor()
    metadata = extractor.extract_metadata(file_path)
    
    # Display metadata
    console.print(Panel(
        f"[bold]File Analysis: {os.path.basename(file_path)}[/bold]",
        border_style="blue"
    ))
    
    # Basic info
    info_table = Table(title="Basic Information")
    info_table.add_column("Property")
    info_table.add_column("Value")
    
    basic_props = ['title', 'author', 'subject', 'created', 'modified', 'last_modified_by']
    for prop in basic_props:
        if prop in metadata and metadata[prop]:
            info_table.add_row(prop.replace('_', ' ').title(), str(metadata[prop]))
    
    console.print(info_table)
    
    # Slides info
    if 'slides_info' in metadata:
        slides_table = Table(title="Slides Information")
        slides_table.add_column("Slide #")
        slides_table.add_column("Layout")
        slides_table.add_column("Shapes")
        slides_table.add_column("Has Notes")
        
        for slide in metadata['slides_info']:
            slides_table.add_row(
                str(slide['slide_number']),
                slide['layout_name'],
                str(slide['shapes_count']),
                "Yes" if slide['has_notes'] else "No"
            )
        
        console.print(slides_table)
    
    # Show audit history if available
    audit_db = PPTAuditDatabase(database)
    history_events = audit_db.get_file_history(file_path)
    
    if history_events:
        console.print(f"\n[bold]Audit History ({len(history_events)} events)[/bold]")
        for event in history_events[:5]:  # Show last 5 events
            timestamp = datetime.fromisoformat(event['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            console.print(f"  {timestamp} - {event['event_type']} (v{event['version']})")

if __name__ == "__main__":
    cli()