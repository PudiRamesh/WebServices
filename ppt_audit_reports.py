#!/usr/bin/env python3
"""
PowerPoint Audit Trail Report Generator
=======================================

Generates comprehensive audit reports from the PPT audit database.
Supports multiple export formats: HTML, PDF, CSV, and JSON.

Author: Auto-generated
Version: 1.0.0
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import csv
from dataclasses import dataclass

import pandas as pd
from jinja2 import Template
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

@dataclass
class AuditSummary:
    """Summary statistics for audit reports."""
    total_files: int
    total_events: int
    unique_users: int
    date_range: tuple
    most_active_user: str
    most_modified_file: str
    total_file_size: int
    avg_file_size: float

class PPTAuditReportGenerator:
    """Generates audit reports in various formats."""
    
    def __init__(self, db_path: str = "ppt_audit.db"):
        self.db_path = db_path
        
    def get_audit_data(self, start_date: str = None, end_date: str = None, 
                      user: str = None, file_path: str = None) -> List[Dict]:
        """Get audit data with optional filters."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        if user:
            query += " AND user = ?"
            params.append(user)
        
        if file_path:
            query += " AND file_path LIKE ?"
            params.append(f"%{file_path}%")
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def generate_summary(self, audit_data: List[Dict]) -> AuditSummary:
        """Generate summary statistics from audit data."""
        if not audit_data:
            return AuditSummary(0, 0, 0, ("", ""), "", "", 0, 0.0)
        
        df = pd.DataFrame(audit_data)
        
        # Basic counts
        total_files = df['file_path'].nunique()
        total_events = len(df)
        unique_users = df['user'].nunique()
        
        # Date range
        timestamps = pd.to_datetime(df['timestamp'])
        date_range = (timestamps.min().strftime('%Y-%m-%d'), 
                     timestamps.max().strftime('%Y-%m-%d'))
        
        # Most active user
        user_counts = df['user'].value_counts()
        most_active_user = user_counts.index[0] if len(user_counts) > 0 else ""
        
        # Most modified file
        file_counts = df['file_path'].value_counts()
        most_modified_file = os.path.basename(file_counts.index[0]) if len(file_counts) > 0 else ""
        
        # File sizes
        valid_sizes = df[df['file_size'] > 0]['file_size']
        total_file_size = valid_sizes.sum() if len(valid_sizes) > 0 else 0
        avg_file_size = valid_sizes.mean() if len(valid_sizes) > 0 else 0.0
        
        return AuditSummary(
            total_files=total_files,
            total_events=total_events,
            unique_users=unique_users,
            date_range=date_range,
            most_active_user=most_active_user,
            most_modified_file=most_modified_file,
            total_file_size=int(total_file_size),
            avg_file_size=avg_file_size
        )
    
    def export_to_csv(self, audit_data: List[Dict], output_file: str):
        """Export audit data to CSV format."""
        if not audit_data:
            console.print("[yellow]No data to export.[/yellow]")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=audit_data[0].keys())
            writer.writeheader()
            
            for row in audit_data:
                # Handle JSON fields
                processed_row = row.copy()
                for key, value in processed_row.items():
                    if key in ['metadata', 'changes'] and isinstance(value, str):
                        try:
                            # Flatten JSON for CSV
                            parsed = json.loads(value)
                            processed_row[key] = str(parsed)
                        except (json.JSONDecodeError, TypeError):
                            processed_row[key] = str(value)
                
                writer.writerow(processed_row)
        
        console.print(f"[green]✓ CSV report exported to: {output_file}[/green]")
    
    def export_to_json(self, audit_data: List[Dict], output_file: str):
        """Export audit data to JSON format."""
        if not audit_data:
            console.print("[yellow]No data to export.[/yellow]")
            return
        
        # Process the data to parse JSON fields
        processed_data = []
        for row in audit_data:
            processed_row = row.copy()
            for key in ['metadata', 'changes']:
                if key in processed_row and isinstance(processed_row[key], str):
                    try:
                        processed_row[key] = json.loads(processed_row[key])
                    except (json.JSONDecodeError, TypeError):
                        pass
            processed_data.append(processed_row)
        
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(processed_data, jsonfile, indent=2, default=str)
        
        console.print(f"[green]✓ JSON report exported to: {output_file}[/green]")
    
    def export_to_html(self, audit_data: List[Dict], output_file: str, 
                      title: str = "PowerPoint Audit Trail Report"):
        """Export audit data to HTML format with styling."""
        summary = self.generate_summary(audit_data)
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 20px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .summary-card .value {
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9em;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .event-type {
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .event-created { background-color: #d4edda; color: #155724; }
        .event-modified { background-color: #fff3cd; color: #856404; }
        .event-deleted { background-color: #f8d7da; color: #721c24; }
        .event-scanned { background-color: #d1ecf1; color: #0c5460; }
        .timestamp {
            font-family: monospace;
            font-size: 0.85em;
        }
        .file-size {
            text-align: right;
        }
        .metadata-preview {
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 0.8em;
            color: #666;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #dee2e6;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <p>Generated on: {{ generation_date }}</p>
        
        <h2>Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Files</h3>
                <div class="value">{{ summary.total_files }}</div>
            </div>
            <div class="summary-card">
                <h3>Total Events</h3>
                <div class="value">{{ summary.total_events }}</div>
            </div>
            <div class="summary-card">
                <h3>Unique Users</h3>
                <div class="value">{{ summary.unique_users }}</div>
            </div>
            <div class="summary-card">
                <h3>Date Range</h3>
                <div class="value" style="font-size: 1.2em;">{{ summary.date_range[0] }} to {{ summary.date_range[1] }}</div>
            </div>
            <div class="summary-card">
                <h3>Most Active User</h3>
                <div class="value" style="font-size: 1.3em;">{{ summary.most_active_user }}</div>
            </div>
            <div class="summary-card">
                <h3>Most Modified File</h3>
                <div class="value" style="font-size: 1.1em;">{{ summary.most_modified_file }}</div>
            </div>
        </div>
        
        <h2>Audit Events ({{ audit_data|length }} events)</h2>
        {% if audit_data %}
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Event Type</th>
                    <th>File Name</th>
                    <th>User</th>
                    <th>Version</th>
                    <th>Size</th>
                    <th>Hash (first 8)</th>
                </tr>
            </thead>
            <tbody>
                {% for event in audit_data %}
                <tr>
                    <td class="timestamp">{{ event.timestamp[:19] }}</td>
                    <td>
                        <span class="event-type event-{{ event.event_type }}">
                            {{ event.event_type }}
                        </span>
                    </td>
                    <td>{{ event.file_name }}</td>
                    <td>{{ event.user or 'Unknown' }}</td>
                    <td>{{ event.version }}</td>
                    <td class="file-size">
                        {% if event.file_size %}
                            {{ "{:,}".format(event.file_size) }} bytes
                        {% else %}
                            N/A
                        {% endif %}
                    </td>
                    <td>
                        {% if event.file_hash %}
                            {{ event.file_hash[:8] }}...
                        {% else %}
                            N/A
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No audit events found for the specified criteria.</p>
        {% endif %}
        
        <div class="footer">
            <p>PowerPoint Audit Trail Report | Generated by PPT Audit System</p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            title=title,
            generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            summary=summary,
            audit_data=audit_data
        )
        
        with open(output_file, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)
        
        console.print(f"[green]✓ HTML report exported to: {output_file}[/green]")
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for a dashboard view."""
        audit_data = self.get_audit_data()
        
        if not audit_data:
            return {"error": "No audit data available"}
        
        df = pd.DataFrame(audit_data)
        
        # Timeline data (events per day)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        timeline = df.groupby('date').size().to_dict()
        timeline = {str(k): v for k, v in timeline.items()}
        
        # User activity
        user_activity = df['user'].value_counts().head(10).to_dict()
        
        # Event types distribution
        event_types = df['event_type'].value_counts().to_dict()
        
        # File types (extensions)
        df['extension'] = df['file_name'].str.split('.').str[-1].str.lower()
        file_types = df['extension'].value_counts().to_dict()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent = df[pd.to_datetime(df['timestamp']) > yesterday]
        recent_activity = len(recent)
        
        return {
            "summary": self.generate_summary(audit_data).__dict__,
            "timeline": timeline,
            "user_activity": user_activity,
            "event_types": event_types,
            "file_types": file_types,
            "recent_activity": recent_activity,
            "last_updated": datetime.now().isoformat()
        }

# CLI for report generation
@click.group()
def cli():
    """PowerPoint Audit Trail Report Generator"""
    pass

@cli.command()
@click.option('--database', '-db', default='ppt_audit.db', help='Database file path')
@click.option('--format', '-f', type=click.Choice(['html', 'csv', 'json', 'all']), 
              default='html', help='Export format')
@click.option('--output', '-o', help='Output file path (without extension)')
@click.option('--start-date', help='Start date filter (YYYY-MM-DD)')
@click.option('--end-date', help='End date filter (YYYY-MM-DD)')
@click.option('--user', help='Filter by user')
@click.option('--file-path', help='Filter by file path (partial match)')
@click.option('--title', default='PowerPoint Audit Trail Report', help='Report title')
def export(database, format, output, start_date, end_date, user, file_path, title):
    """Export audit data to various formats."""
    if not os.path.exists(database):
        console.print(f"[red]Error: Database file '{database}' not found.[/red]")
        return
    
    generator = PPTAuditReportGenerator(database)
    audit_data = generator.get_audit_data(start_date, end_date, user, file_path)
    
    if not audit_data:
        console.print("[yellow]No audit data found for the specified criteria.[/yellow]")
        return
    
    # Generate default output filename if not provided
    if not output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = f"ppt_audit_report_{timestamp}"
    
    console.print(f"[blue]Generating report with {len(audit_data)} audit events...[/blue]")
    
    if format == 'html' or format == 'all':
        generator.export_to_html(audit_data, f"{output}.html", title)
    
    if format == 'csv' or format == 'all':
        generator.export_to_csv(audit_data, f"{output}.csv")
    
    if format == 'json' or format == 'all':
        generator.export_to_json(audit_data, f"{output}.json")
    
    console.print("[green]✓ Report generation completed![/green]")

@cli.command()
@click.option('--database', '-db', default='ppt_audit.db', help='Database file path')
def dashboard(database):
    """Display dashboard with audit statistics."""
    if not os.path.exists(database):
        console.print(f"[red]Error: Database file '{database}' not found.[/red]")
        return
    
    generator = PPTAuditReportGenerator(database)
    dashboard_data = generator.generate_dashboard_data()
    
    if "error" in dashboard_data:
        console.print(f"[red]Error: {dashboard_data['error']}[/red]")
        return
    
    # Display dashboard
    console.print(Panel(
        "[bold blue]PowerPoint Audit Trail Dashboard[/bold blue]",
        border_style="blue"
    ))
    
    summary = dashboard_data["summary"]
    
    # Summary table
    summary_table = Table(title="Summary Statistics")
    summary_table.add_column("Metric")
    summary_table.add_column("Value")
    
    summary_table.add_row("Total Files", str(summary["total_files"]))
    summary_table.add_row("Total Events", str(summary["total_events"]))
    summary_table.add_row("Unique Users", str(summary["unique_users"]))
    summary_table.add_row("Date Range", f"{summary['date_range'][0]} to {summary['date_range'][1]}")
    summary_table.add_row("Most Active User", summary["most_active_user"])
    summary_table.add_row("Most Modified File", summary["most_modified_file"])
    summary_table.add_row("Recent Activity (24h)", str(dashboard_data["recent_activity"]))
    
    console.print(summary_table)
    
    # Event types
    if dashboard_data["event_types"]:
        event_table = Table(title="Event Types Distribution")
        event_table.add_column("Event Type")
        event_table.add_column("Count")
        
        for event_type, count in dashboard_data["event_types"].items():
            event_table.add_row(event_type, str(count))
        
        console.print(event_table)
    
    # Top users
    if dashboard_data["user_activity"]:
        user_table = Table(title="Most Active Users")
        user_table.add_column("User")
        user_table.add_column("Activity Count")
        
        for user, count in list(dashboard_data["user_activity"].items())[:5]:
            user_table.add_row(user, str(count))
        
        console.print(user_table)

if __name__ == "__main__":
    cli()