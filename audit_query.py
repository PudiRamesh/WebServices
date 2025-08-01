#!/usr/bin/env python3
"""
PowerPoint Audit Trail Query Utility
Provides various queries and analysis tools for the audit trail database.
"""

import sqlite3
import argparse
from datetime import datetime, timedelta
from pathlib import Path

class AuditQuery:
    def __init__(self, db_path="audit_trail.db"):
        self.db_path = db_path
        
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
        
    def list_all_files(self):
        """List all tracked PowerPoint files."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.file_name, f.file_path, f.first_seen, f.last_modified, f.file_size,
                   COUNT(c.id) as change_count
            FROM files f
            LEFT JOIN changes c ON f.id = c.file_id
            GROUP BY f.id
            ORDER BY f.last_modified DESC
        ''')
        
        files = cursor.fetchall()
        conn.close()
        
        print(f"\nTracked PowerPoint Files ({len(files)}):")
        print("-" * 80)
        print(f"{'File Name':<30} {'First Seen':<20} {'Last Modified':<20} {'Changes':<8}")
        print("-" * 80)
        
        for file_info in files:
            print(f"{file_info[0]:<30} {file_info[2]:<20} {file_info[3]:<20} {file_info[5]:<8}")
            
    def get_recent_changes(self, limit=20):
        """Get recent changes to PowerPoint files."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.file_name, c.change_type, c.change_description, c.timestamp
            FROM changes c
            JOIN files f ON c.file_id = f.id
            ORDER BY c.timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        changes = cursor.fetchall()
        conn.close()
        
        print(f"\nRecent Changes (Last {len(changes)}):")
        print("-" * 80)
        print(f"{'File Name':<25} {'Change Type':<15} {'Description':<25} {'Timestamp':<20}")
        print("-" * 80)
        
        for change in changes:
            print(f"{change[0]:<25} {change[1]:<15} {change[2] or '':<25} {change[3]:<20}")
            
    def get_file_history(self, file_name):
        """Get complete history for a specific file."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.change_type, c.change_description, c.timestamp, c.backup_path
            FROM changes c
            JOIN files f ON c.file_id = f.id
            WHERE f.file_name = ?
            ORDER BY c.timestamp DESC
        ''', (file_name,))
        
        history = cursor.fetchall()
        conn.close()
        
        if not history:
            print(f"No history found for file: {file_name}")
            return
            
        print(f"\nFile History for: {file_name}")
        print("-" * 80)
        print(f"{'Change Type':<15} {'Description':<30} {'Timestamp':<20} {'Backup':<15}")
        print("-" * 80)
        
        for record in history:
            backup_info = "Yes" if record[3] else "No"
            print(f"{record[0]:<15} {record[1] or '':<30} {record[2]:<20} {backup_info:<15}")
            
    def get_changes_by_date_range(self, start_date, end_date):
        """Get changes within a specific date range."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.file_name, c.change_type, c.change_description, c.timestamp
            FROM changes c
            JOIN files f ON c.file_id = f.id
            WHERE DATE(c.timestamp) BETWEEN ? AND ?
            ORDER BY c.timestamp DESC
        ''', (start_date, end_date))
        
        changes = cursor.fetchall()
        conn.close()
        
        print(f"\nChanges from {start_date} to {end_date} ({len(changes)} changes):")
        print("-" * 80)
        print(f"{'File Name':<25} {'Change Type':<15} {'Description':<25} {'Timestamp':<20}")
        print("-" * 80)
        
        for change in changes:
            print(f"{change[0]:<25} {change[1]:<15} {change[2] or '':<25} {change[3]:<20}")
            
    def get_statistics(self):
        """Get overall statistics about the audit trail."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total files
        cursor.execute("SELECT COUNT(*) FROM files")
        total_files = cursor.fetchone()[0]
        
        # Total changes
        cursor.execute("SELECT COUNT(*) FROM changes")
        total_changes = cursor.fetchone()[0]
        
        # Changes by type
        cursor.execute('''
            SELECT change_type, COUNT(*) as count
            FROM changes
            GROUP BY change_type
            ORDER BY count DESC
        ''')
        changes_by_type = cursor.fetchall()
        
        # Most active files
        cursor.execute('''
            SELECT f.file_name, COUNT(c.id) as change_count
            FROM files f
            LEFT JOIN changes c ON f.id = c.file_id
            GROUP BY f.id
            ORDER BY change_count DESC
            LIMIT 5
        ''')
        most_active_files = cursor.fetchall()
        
        conn.close()
        
        print("\nAudit Trail Statistics:")
        print("-" * 40)
        print(f"Total Files Tracked: {total_files}")
        print(f"Total Changes Logged: {total_changes}")
        
        print(f"\nChanges by Type:")
        for change_type, count in changes_by_type:
            print(f"  {change_type}: {count}")
            
        print(f"\nMost Active Files:")
        for file_name, count in most_active_files:
            print(f"  {file_name}: {count} changes")
            
    def export_to_csv(self, output_file="audit_export.csv"):
        """Export audit data to CSV format."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT f.file_name, f.file_path, c.change_type, c.change_description, 
                   c.timestamp, c.backup_path
            FROM changes c
            JOIN files f ON c.file_id = f.id
            ORDER BY c.timestamp DESC
        ''')
        
        data = cursor.fetchall()
        conn.close()
        
        with open(output_file, 'w') as f:
            f.write("File Name,File Path,Change Type,Description,Timestamp,Backup Path\n")
            for row in data:
                # Escape commas and quotes in CSV
                escaped_row = [f'"{str(field).replace('"', '""')}"' for field in row]
                f.write(','.join(escaped_row) + '\n')
                
        print(f"Audit data exported to: {output_file}")
        print(f"Total records exported: {len(data)}")


def main():
    parser = argparse.ArgumentParser(description="PowerPoint Audit Trail Query Utility")
    parser.add_argument("--db", default="audit_trail.db", help="Database file path")
    parser.add_argument("--list-files", action="store_true", help="List all tracked files")
    parser.add_argument("--recent", type=int, default=20, help="Show recent changes (default: 20)")
    parser.add_argument("--file-history", help="Show history for specific file")
    parser.add_argument("--date-range", nargs=2, metavar=("START", "END"), 
                       help="Show changes in date range (YYYY-MM-DD)")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--export", help="Export to CSV file")
    
    args = parser.parse_args()
    
    query = AuditQuery(args.db)
    
    if args.list_files:
        query.list_all_files()
    elif args.file_history:
        query.get_file_history(args.file_history)
    elif args.date_range:
        query.get_changes_by_date_range(args.date_range[0], args.date_range[1])
    elif args.stats:
        query.get_statistics()
    elif args.export:
        query.export_to_csv(args.export)
    else:
        # Default: show recent changes
        query.get_recent_changes(args.recent)


if __name__ == "__main__":
    main()