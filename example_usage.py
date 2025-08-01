#!/usr/bin/env python3
"""
Example usage of the PowerPoint Audit Trail System
Demonstrates how to use the system programmatically.
"""

import os
import time
import tempfile
import shutil
from pathlib import Path
from ppt_audit_trail import PPTAuditTrail

def create_sample_presentation():
    """Create a sample PowerPoint file for testing."""
    try:
        from pptx import Presentation
        from pptx.util import Inches
        
        # Create a new presentation
        prs = Presentation()
        
        # Add a title slide
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = "Sample Presentation"
        subtitle.text = "Created for Audit Trail Testing"
        
        # Add a content slide
        bullet_slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(bullet_slide_layout)
        shapes = slide.shapes
        
        title_shape = shapes.title
        body_shape = shapes.placeholders[1]
        
        title_shape.text = "Sample Content"
        
        tf = body_shape.text_frame
        tf.text = "First bullet point"
        
        p = tf.add_paragraph()
        p.text = "Second bullet point"
        p.level = 1
        
        p = tf.add_paragraph()
        p.text = "Third bullet point"
        p.level = 1
        
        # Save the presentation
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, "sample_presentation.pptx")
        prs.save(file_path)
        
        return temp_dir, file_path
        
    except ImportError:
        print("python-pptx not available. Creating a dummy file instead.")
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, "sample_presentation.pptx")
        
        # Create a dummy file
        with open(file_path, 'w') as f:
            f.write("This is a dummy PowerPoint file for testing.")
        
        return temp_dir, file_path

def demonstrate_audit_trail():
    """Demonstrate the audit trail functionality."""
    print("PowerPoint Audit Trail System - Example Usage")
    print("=" * 50)
    
    # Create a temporary directory for testing
    temp_dir, sample_file = create_sample_presentation()
    
    try:
        # Initialize the audit trail system
        print(f"Initializing audit trail for directory: {temp_dir}")
        audit_trail = PPTAuditTrail(db_path="example_audit.db", watch_directory=temp_dir)
        
        # Scan existing files
        print("\n1. Scanning existing files...")
        audit_trail.scan_existing_files()
        
        # Create a snapshot of the current file
        print("\n2. Creating initial snapshot...")
        audit_trail.create_snapshot(sample_file)
        
        # Log some events
        print("\n3. Logging audit events...")
        audit_trail.log_audit_event(
            sample_file, 
            "file_created", 
            "Sample presentation created for testing",
            user="example_user"
        )
        
        # Simulate file modification
        print("\n4. Simulating file modification...")
        time.sleep(1)  # Ensure different timestamp
        
        # Modify the file (in a real scenario, this would be done by editing the PPT)
        with open(sample_file, 'a') as f:
            f.write("\nModified content")
        
        # Detect changes
        changes = audit_trail.detect_changes(sample_file)
        if changes:
            print(f"   Changes detected: {changes['summary']}")
            audit_trail.create_snapshot(sample_file)
            audit_trail.log_audit_event(
                sample_file,
                "file_modified",
                changes['summary'],
                user="example_user",
                change_type=changes['type']
            )
        
        # Generate audit report
        print("\n5. Generating audit report...")
        report = audit_trail.get_audit_report(sample_file)
        
        print(f"\nAudit Report for: {sample_file}")
        print("-" * 40)
        for entry in report:
            print(f"Time: {entry['timestamp']}")
            print(f"Action: {entry['action']}")
            print(f"Details: {entry['details']}")
            print(f"File Size: {entry['file_size']} bytes")
            print(f"Slides: {entry['slide_count']}")
            print("-" * 20)
        
        # Demonstrate file deletion
        print("\n6. Simulating file deletion...")
        audit_trail.log_audit_event(
            sample_file,
            "file_deleted",
            "Sample file deleted",
            user="example_user"
        )
        
        print("\nExample completed successfully!")
        print(f"Database created: example_audit.db")
        print(f"Log file created: ppt_audit.log")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
    
    finally:
        # Clean up
        print(f"\nCleaning up temporary files...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Remove example database and log
        try:
            os.remove("example_audit.db")
            os.remove("ppt_audit.log")
        except FileNotFoundError:
            pass

def demonstrate_api_usage():
    """Demonstrate API usage for the web dashboard."""
    print("\n" + "=" * 50)
    print("API Usage Examples")
    print("=" * 50)
    
    print("""
To use the web dashboard API:

1. Start the dashboard:
   python audit_dashboard.py

2. Available endpoints:
   - GET /api/stats - Dashboard statistics
   - GET /api/events - Audit events with pagination
   - GET /api/files - List of monitored files
   - GET /api/file/<path> - Detailed file information
   - GET /api/actions - Available action types

3. Example API calls:
   curl http://localhost:5000/api/stats
   curl http://localhost:5000/api/events?per_page=10
   curl http://localhost:5000/api/files

4. Access the web interface:
   Open http://localhost:5000 in your browser
""")

if __name__ == "__main__":
    demonstrate_audit_trail()
    demonstrate_api_usage()
    
    print("\n" + "=" * 50)
    print("Next Steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the system: python start_audit_system.py")
    print("3. Access dashboard: http://localhost:5000")
    print("4. Place PowerPoint files in the monitored directory")
    print("=" * 50)