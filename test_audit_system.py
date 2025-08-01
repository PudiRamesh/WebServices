#!/usr/bin/env python3
"""
Test script for PowerPoint Audit Trail System
Demonstrates the system functionality with sample operations.
"""

import os
import time
import tempfile
import shutil
from pathlib import Path
from ppt_audit_trail import PowerPointAuditTrail
from audit_query import AuditQuery

def create_sample_presentation(file_path):
    """Create a sample PowerPoint file for testing."""
    try:
        from pptx import Presentation
        from pptx.util import Inches
        
        # Create presentation
        prs = Presentation()
        
        # Add title slide
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = "Sample Presentation"
        subtitle.text = "Created for Audit Trail Testing"
        
        # Add content slide
        bullet_slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(bullet_slide_layout)
        shapes = slide.shapes
        
        title_shape = shapes.title
        body_shape = shapes.placeholders[1]
        
        title_shape.text = "Sample Content"
        
        tf = body_shape.text_frame
        tf.text = "This is a test presentation"
        
        p = tf.add_paragraph()
        p.text = "Created to test the audit trail system"
        p.level = 1
        
        p = tf.add_paragraph()
        p.text = "Features being tested:"
        p.level = 1
        
        p = tf.add_paragraph()
        p.text = "File monitoring"
        p.level = 2
        
        p = tf.add_paragraph()
        p.text = "Change detection"
        p.level = 2
        
        p = tf.add_paragraph()
        p.text = "Backup creation"
        p.level = 2
        
        # Save presentation
        prs.save(file_path)
        print(f"Created sample presentation: {file_path}")
        return True
        
    except ImportError:
        print("python-pptx not available. Skipping sample presentation creation.")
        return False
    except Exception as e:
        print(f"Error creating sample presentation: {e}")
        return False

def test_audit_system():
    """Test the audit trail system with sample operations."""
    print("PowerPoint Audit Trail System - Test")
    print("=" * 50)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Using temporary directory: {temp_path}")
        
        # Initialize audit system
        audit_system = PowerPointAuditTrail(watch_directory=str(temp_path))
        
        try:
            # Start monitoring
            print("\n1. Starting file monitoring...")
            audit_system.start_monitoring()
            time.sleep(2)  # Allow monitoring to start
            
            # Create sample presentation
            print("\n2. Creating sample presentation...")
            sample_file = temp_path / "test_presentation.pptx"
            if create_sample_presentation(sample_file):
                time.sleep(2)  # Allow file system to register the change
                
                # Modify the presentation
                print("\n3. Modifying presentation...")
                if create_sample_presentation(sample_file):  # Overwrite with new content
                    time.sleep(2)
                
                # Create another presentation
                print("\n4. Creating second presentation...")
                sample_file2 = temp_path / "test_presentation2.pptx"
                if create_sample_presentation(sample_file2):
                    time.sleep(2)
                
                # Stop monitoring
                print("\n5. Stopping monitoring...")
                audit_system.stop_monitoring()
                
                # Generate report
                print("\n6. Generating audit report...")
                audit_system.generate_audit_report("test_audit_report.html")
                
                # Query audit data
                print("\n7. Querying audit data...")
                query = AuditQuery(audit_system.db_path)
                
                print("\n--- Recent Changes ---")
                query.get_recent_changes(10)
                
                print("\n--- All Tracked Files ---")
                query.list_all_files()
                
                print("\n--- Statistics ---")
                query.get_statistics()
                
                # Export data
                print("\n8. Exporting audit data...")
                query.export_to_csv("test_audit_export.csv")
                
                print("\nTest completed successfully!")
                print(f"Check the following files:")
                print(f"- test_audit_report.html (HTML report)")
                print(f"- test_audit_export.csv (CSV export)")
                print(f"- {audit_system.db_path} (SQLite database)")
                print(f"- {audit_system.backup_directory} (Backup files)")
                
            else:
                print("Could not create sample presentation. Test incomplete.")
                
        except Exception as e:
            print(f"Error during testing: {e}")
            audit_system.stop_monitoring()

def test_query_functions():
    """Test the query functions independently."""
    print("\n" + "=" * 50)
    print("Testing Query Functions")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists("audit_trail.db"):
        print("No audit database found. Run the main test first.")
        return
    
    query = AuditQuery()
    
    print("\n1. Testing file listing...")
    query.list_all_files()
    
    print("\n2. Testing recent changes...")
    query.get_recent_changes(5)
    
    print("\n3. Testing statistics...")
    query.get_statistics()
    
    print("\n4. Testing CSV export...")
    query.export_to_csv("query_test_export.csv")

def main():
    """Main test function."""
    print("PowerPoint Audit Trail System - Comprehensive Test")
    print("=" * 60)
    
    # Test the main audit system
    test_audit_system()
    
    # Test query functions
    test_query_functions()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()