#!/usr/bin/env python3
"""
Simple PowerPoint Audit Trail Test
==================================

A simplified test to demonstrate the audit trail concept without requiring
all external dependencies.
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path

class SimpleAuditDB:
    """Simplified audit database for testing."""
    
    def __init__(self, db_path="test_audit.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_event(self, event_type, file_path, file_size=0, file_hash=""):
        """Log an audit event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_events 
            (timestamp, event_type, file_path, file_name, file_size, file_hash, user)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(timezone.utc).isoformat(),
            event_type,
            file_path,
            os.path.basename(file_path),
            file_size,
            file_hash,
            os.getenv('USER', 'testuser')
        ))
        
        conn.commit()
        conn.close()
    
    def get_events(self):
        """Get all audit events."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM audit_events ORDER BY timestamp DESC')
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results

def calculate_hash(file_path):
    """Calculate file hash."""
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return ""

def create_test_files():
    """Create test files to simulate PowerPoint files."""
    test_dir = Path("test_presentations")
    test_dir.mkdir(exist_ok=True)
    
    files = []
    
    # Create test "PowerPoint" files (just text files for testing)
    for i, name in enumerate(["presentation1.pptx", "meeting_slides.pptx", "quarterly_report.pptx"], 1):
        file_path = test_dir / name
        content = f"""Test PowerPoint File {i}
Title: {name.replace('.pptx', '').replace('_', ' ').title()}
Created: {datetime.now()}
Content: This is a test file simulating a PowerPoint presentation.
Slides: 5
Author: Test User {i}
"""
        file_path.write_text(content)
        files.append(file_path)
    
    return files

def simulate_audit_trail():
    """Simulate the audit trail system."""
    print("🎯 PowerPoint Audit Trail - Test Simulation")
    print("=" * 50)
    
    # Initialize audit database
    audit_db = SimpleAuditDB()
    
    # Create test files
    print("\n📁 Creating test PowerPoint files...")
    files = create_test_files()
    
    # Log file creation events
    for file_path in files:
        file_size = file_path.stat().st_size
        file_hash = calculate_hash(file_path)
        audit_db.log_event("created", str(file_path), file_size, file_hash)
        print(f"   ✓ Created: {file_path.name}")
    
    # Simulate file modifications
    print("\n📝 Simulating file modifications...")
    modified_file = files[0]
    original_content = modified_file.read_text()
    modified_content = original_content + "\nUPDATED: File modified for testing"
    modified_file.write_text(modified_content)
    
    new_hash = calculate_hash(modified_file)
    audit_db.log_event("modified", str(modified_file), modified_file.stat().st_size, new_hash)
    print(f"   ✓ Modified: {modified_file.name}")
    
    # Simulate file deletion
    print("\n🗑️  Simulating file deletion...")
    deleted_file = files[-1]
    audit_db.log_event("deleted", str(deleted_file), 0, "")
    deleted_file.unlink()
    print(f"   ✓ Deleted: {deleted_file.name}")
    
    # Display audit events
    print("\n📊 Audit Trail Events:")
    print("-" * 50)
    events = audit_db.get_events()
    
    for event in events:
        timestamp = datetime.fromisoformat(event['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} | {event['event_type'].upper():8} | {event['file_name']:20} | {event['user']}")
    
    # Generate simple report
    print(f"\n📈 Audit Summary:")
    print(f"   • Total Events: {len(events)}")
    
    event_counts = {}
    for event in events:
        event_type = event['event_type']
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    for event_type, count in event_counts.items():
        print(f"   • {event_type.title()}: {count}")
    
    # Export to JSON
    report_file = "test_audit_report.json"
    with open(report_file, 'w') as f:
        json.dump(events, f, indent=2, default=str)
    
    print(f"\n✅ Test completed successfully!")
    print(f"   • Database: {audit_db.db_path}")
    print(f"   • Report: {report_file}")
    print(f"   • Test files: test_presentations/")
    
    return audit_db

if __name__ == "__main__":
    try:
        simulate_audit_trail()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()