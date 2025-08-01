#!/usr/bin/env python3
"""
PowerPoint Audit Trail System - Demo Script
==========================================

This script demonstrates the key features of the PowerPoint audit trail system.
It creates sample PowerPoint files, monitors them, and generates reports.

Author: Auto-generated
Version: 1.0.0
"""

import os
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from pptx import Presentation
from pptx.util import Inches
from rich.console import Console
from rich.panel import Panel
from rich.progress import track

from ppt_audit_trail import PPTAuditTrail, PPTAuditDatabase
from ppt_audit_reports import PPTAuditReportGenerator

console = Console()

class PPTAuditDemo:
    """Demonstration class for PowerPoint audit trail system."""
    
    def __init__(self, demo_dir: str = "demo_presentations"):
        self.demo_dir = Path(demo_dir)
        self.demo_dir.mkdir(exist_ok=True)
        self.db_path = self.demo_dir / "demo_audit.db"
        
    def create_sample_presentations(self) -> list:
        """Create sample PowerPoint presentations for demonstration."""
        presentations = []
        
        console.print("[blue]Creating sample PowerPoint presentations...[/blue]")
        
        # Sample 1: Basic presentation
        prs1 = Presentation()
        slide1 = prs1.slides.add_slide(prs1.slide_layouts[0])  # Title slide
        slide1.shapes.title.text = "Company Overview"
        slide1.placeholders[1].text = "Q4 2024 Business Review"
        
        slide2 = prs1.slides.add_slide(prs1.slide_layouts[1])  # Content slide
        slide2.shapes.title.text = "Key Metrics"
        content = slide2.placeholders[1].text_frame
        content.text = "Revenue: $2.5M\nGrowth: 15%\nCustomers: 1,200"
        
        # Set metadata
        prs1.core_properties.title = "Company Overview Presentation"
        prs1.core_properties.author = "John Doe"
        prs1.core_properties.subject = "Business Review"
        prs1.core_properties.keywords = "company, overview, metrics"
        
        file1 = self.demo_dir / "company_overview.pptx"
        prs1.save(str(file1))
        presentations.append(file1)
        
        # Sample 2: Marketing presentation
        prs2 = Presentation()
        slide1 = prs2.slides.add_slide(prs2.slide_layouts[0])
        slide1.shapes.title.text = "Marketing Strategy 2024"
        slide1.placeholders[1].text = "Digital Transformation Initiative"
        
        slide2 = prs2.slides.add_slide(prs2.slide_layouts[1])
        slide2.shapes.title.text = "Campaign Results"
        content = slide2.placeholders[1].text_frame
        content.text = "Social Media: 45% engagement\nEmail: 23% open rate\nWebsite: 67% conversion"
        
        slide3 = prs2.slides.add_slide(prs2.slide_layouts[6])  # Blank slide
        slide3.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(2)).text_frame.text = "Next Steps: Launch Q1 Campaign"
        
        prs2.core_properties.title = "Marketing Strategy 2024"
        prs2.core_properties.author = "Jane Smith"
        prs2.core_properties.subject = "Marketing"
        prs2.core_properties.keywords = "marketing, strategy, digital"
        
        file2 = self.demo_dir / "marketing_strategy.pptx"
        prs2.save(str(file2))
        presentations.append(file2)
        
        # Sample 3: Financial report
        prs3 = Presentation()
        slide1 = prs3.slides.add_slide(prs3.slide_layouts[0])
        slide1.shapes.title.text = "Financial Report Q4"
        slide1.placeholders[1].text = "Year-End Financial Summary"
        
        prs3.core_properties.title = "Financial Report Q4 2024"
        prs3.core_properties.author = "Finance Team"
        prs3.core_properties.subject = "Financial Report"
        prs3.core_properties.keywords = "finance, report, quarterly"
        
        file3 = self.demo_dir / "financial_report.pptx"
        prs3.save(str(file3))
        presentations.append(file3)
        
        console.print(f"[green]✓ Created {len(presentations)} sample presentations[/green]")
        return presentations
    
    def simulate_file_activities(self, presentations: list):
        """Simulate various file activities for demonstration."""
        console.print("[blue]Simulating file activities...[/blue]")
        
        # Wait a moment for file system to settle
        time.sleep(1)
        
        # Modify the first presentation
        console.print("  • Modifying company_overview.pptx...")
        prs = Presentation(str(presentations[0]))
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Updated Metrics"
        slide.placeholders[1].text_frame.text = "Revenue: $2.8M (Updated)\nGrowth: 18%\nCustomers: 1,350"
        prs.save(str(presentations[0]))
        time.sleep(1)
        
        # Create a new file by copying
        console.print("  • Creating backup copy...")
        backup_file = self.demo_dir / "company_overview_backup.pptx"
        shutil.copy2(presentations[0], backup_file)
        time.sleep(1)
        
        # Modify the marketing presentation
        console.print("  • Updating marketing_strategy.pptx...")
        prs2 = Presentation(str(presentations[1]))
        prs2.core_properties.keywords = "marketing, strategy, digital, updated"
        prs2.save(str(presentations[1]))
        time.sleep(1)
        
        # Delete the backup file to show deletion tracking
        console.print("  • Removing backup file...")
        if backup_file.exists():
            backup_file.unlink()
        
        console.print("[green]✓ File activities simulation completed[/green]")
    
    def run_audit_scan(self):
        """Run the audit trail system to scan and monitor files."""
        console.print("[blue]Initializing audit trail system...[/blue]")
        
        # Initialize audit trail
        audit_trail = PPTAuditTrail(str(self.demo_dir), str(self.db_path))
        
        # Scan existing files
        console.print("  • Scanning existing PowerPoint files...")
        audit_trail.scan_existing_files()
        
        console.print("[green]✓ Audit scan completed[/green]")
        return audit_trail.audit_db
    
    def generate_demo_reports(self, audit_db: PPTAuditDatabase):
        """Generate demonstration reports."""
        console.print("[blue]Generating audit reports...[/blue]")
        
        report_generator = PPTAuditReportGenerator(str(self.db_path))
        
        # Generate reports directory
        reports_dir = self.demo_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Get audit data
        audit_data = report_generator.get_audit_data()
        
        if not audit_data:
            console.print("[yellow]No audit data available for reports[/yellow]")
            return
        
        # Generate HTML report
        html_file = reports_dir / "demo_audit_report.html"
        report_generator.export_to_html(
            audit_data, 
            str(html_file), 
            "PowerPoint Audit Trail - Demo Report"
        )
        
        # Generate CSV report
        csv_file = reports_dir / "demo_audit_report.csv"
        report_generator.export_to_csv(audit_data, str(csv_file))
        
        # Generate JSON report
        json_file = reports_dir / "demo_audit_report.json"
        report_generator.export_to_json(audit_data, str(json_file))
        
        console.print(f"[green]✓ Reports generated in: {reports_dir}[/green]")
        return reports_dir
    
    def display_audit_summary(self, audit_db: PPTAuditDatabase):
        """Display a summary of the audit data."""
        recent_events = audit_db.get_user_activity(limit=20)
        
        if not recent_events:
            console.print("[yellow]No audit events found[/yellow]")
            return
        
        console.print(Panel(
            "[bold green]Audit Trail Summary[/bold green]",
            border_style="green"
        ))
        
        # Count events by type
        event_counts = {}
        for event in recent_events:
            event_type = event['event_type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Display summary
        console.print(f"[bold]Total Events:[/bold] {len(recent_events)}")
        for event_type, count in event_counts.items():
            console.print(f"  • {event_type.title()}: {count}")
        
        console.print("\n[bold]Recent Events:[/bold]")
        for event in recent_events[:5]:
            timestamp = datetime.fromisoformat(event['timestamp']).strftime('%H:%M:%S')
            console.print(f"  {timestamp} - {event['event_type']} - {event['file_name']}")
    
    def run_demo(self):
        """Run the complete demonstration."""
        console.print(Panel(
            "[bold blue]PowerPoint Audit Trail System - Demo[/bold blue]\n"
            "This demonstration will:\n"
            "1. Create sample PowerPoint presentations\n"
            "2. Simulate file activities\n"
            "3. Run audit trail scanning\n"
            "4. Generate comprehensive reports\n"
            "5. Display audit summary",
            title="Demo Starting",
            border_style="blue"
        ))
        
        try:
            # Step 1: Create sample presentations
            presentations = self.create_sample_presentations()
            
            # Step 2: Simulate activities
            self.simulate_file_activities(presentations)
            
            # Step 3: Run audit scan
            audit_db = self.run_audit_scan()
            
            # Step 4: Generate reports
            reports_dir = self.generate_demo_reports(audit_db)
            
            # Step 5: Display summary
            self.display_audit_summary(audit_db)
            
            # Final summary
            console.print(Panel(
                f"[bold green]Demo Completed Successfully![/bold green]\n\n"
                f"📁 Demo files: {self.demo_dir}\n"
                f"🗃️ Database: {self.db_path}\n"
                f"📊 Reports: {reports_dir}\n\n"
                f"[bold]Next Steps:[/bold]\n"
                f"• Open the HTML report: {reports_dir}/demo_audit_report.html\n"
                f"• Explore the database: sqlite3 {self.db_path}\n"
                f"• Try monitoring: python ppt_audit_trail.py monitor -d {self.demo_dir}\n"
                f"• Generate custom reports: python ppt_audit_reports.py export -db {self.db_path}",
                title="Demo Complete",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[red]Demo failed with error: {e}[/red]")
            console.print_exception()
    
    def cleanup_demo(self):
        """Clean up demo files."""
        if self.demo_dir.exists():
            shutil.rmtree(self.demo_dir)
            console.print(f"[yellow]Demo directory {self.demo_dir} cleaned up[/yellow]")

def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerPoint Audit Trail Demo")
    parser.add_argument('--cleanup', action='store_true', 
                       help='Clean up demo files and exit')
    parser.add_argument('--demo-dir', default='demo_presentations',
                       help='Directory for demo files')
    
    args = parser.parse_args()
    
    demo = PPTAuditDemo(args.demo_dir)
    
    if args.cleanup:
        demo.cleanup_demo()
    else:
        demo.run_demo()

if __name__ == "__main__":
    main()