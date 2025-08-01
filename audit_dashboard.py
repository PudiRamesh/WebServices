#!/usr/bin/env python3
"""
PowerPoint Audit Trail Dashboard
Web-based interface for viewing audit reports and statistics.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
from datetime import datetime, timedelta
from ppt_audit_trail import PPTAuditTrail
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Global audit trail instance
audit_trail = None

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(audit_trail.db_path if audit_trail else 'ppt_audit.db')

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total files monitored
        cursor.execute('SELECT COUNT(DISTINCT file_path) FROM audit_log')
        total_files = cursor.fetchone()[0]
        
        # Total events
        cursor.execute('SELECT COUNT(*) FROM audit_log')
        total_events = cursor.fetchone()[0]
        
        # Events today
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM audit_log WHERE DATE(timestamp) = ?', (today,))
        events_today = cursor.fetchone()[0]
        
        # Recent activity (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM audit_log 
            WHERE DATE(timestamp) >= ? 
            GROUP BY DATE(timestamp) 
            ORDER BY date DESC
        ''', (week_ago,))
        recent_activity = dict(cursor.fetchall())
        
        # File types
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN file_path LIKE '%.pptx' THEN 'PPTX'
                    WHEN file_path LIKE '%.ppt' THEN 'PPT'
                    ELSE 'Other'
                END as file_type,
                COUNT(DISTINCT file_path) as count
            FROM audit_log 
            GROUP BY file_type
        ''')
        file_types = dict(cursor.fetchall())
        
        conn.close()
        
        return jsonify({
            'total_files': total_files,
            'total_events': total_events,
            'events_today': events_today,
            'recent_activity': recent_activity,
            'file_types': file_types
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events')
def get_events():
    """Get audit events with pagination and filtering."""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        file_path = request.args.get('file_path', '')
        action = request.args.get('action', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        query = '''
            SELECT timestamp, file_path, action, user, details, 
                   file_size, slide_count, change_type
            FROM audit_log
            WHERE 1=1
        '''
        params = []
        
        if file_path:
            query += " AND file_path LIKE ?"
            params.append(f'%{file_path}%')
            
        if action:
            query += " AND action = ?"
            params.append(action)
            
        if start_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(end_date)
            
        # Get total count
        count_query = query.replace('SELECT timestamp, file_path, action, user, details, file_size, slide_count, change_type', 'SELECT COUNT(*)')
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        events = [
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
        
        conn.close()
        
        return jsonify({
            'events': events,
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files')
def get_files():
    """Get list of monitored files."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT file_path, 
                   MAX(timestamp) as last_modified,
                   COUNT(*) as event_count,
                   MAX(file_size) as current_size,
                   MAX(slide_count) as current_slides
            FROM audit_log 
            GROUP BY file_path 
            ORDER BY last_modified DESC
        ''')
        
        results = cursor.fetchall()
        files = [
            {
                'file_path': row[0],
                'last_modified': row[1],
                'event_count': row[2],
                'current_size': row[3],
                'current_slides': row[4]
            }
            for row in results
        ]
        
        conn.close()
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file/<path:file_path>')
def get_file_details(file_path):
    """Get detailed information about a specific file."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get file events
        cursor.execute('''
            SELECT timestamp, action, user, details, file_size, slide_count, change_type
            FROM audit_log 
            WHERE file_path = ? 
            ORDER BY timestamp DESC
        ''', (file_path,))
        
        events = [
            {
                'timestamp': row[0],
                'action': row[1],
                'user': row[2],
                'details': row[3],
                'file_size': row[4],
                'slide_count': row[5],
                'change_type': row[6]
            }
            for row in cursor.fetchall()
        ]
        
        # Get snapshots
        cursor.execute('''
            SELECT timestamp, file_hash, file_size, slide_count, slide_details, metadata
            FROM file_snapshots 
            WHERE file_path = ? 
            ORDER BY timestamp DESC
        ''', (file_path,))
        
        snapshots = [
            {
                'timestamp': row[0],
                'file_hash': row[1],
                'file_size': row[2],
                'slide_count': row[3],
                'slide_details': json.loads(row[4]) if row[4] else [],
                'metadata': json.loads(row[5]) if row[5] else {}
            }
            for row in cursor.fetchall()
        ]
        
        # Get change history
        cursor.execute('''
            SELECT timestamp, old_hash, new_hash, change_summary, detailed_changes
            FROM change_history 
            WHERE file_path = ? 
            ORDER BY timestamp DESC
        ''', (file_path,))
        
        changes = [
            {
                'timestamp': row[0],
                'old_hash': row[1],
                'new_hash': row[2],
                'change_summary': row[3],
                'detailed_changes': json.loads(row[4]) if row[4] else {}
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return jsonify({
            'file_path': file_path,
            'events': events,
            'snapshots': snapshots,
            'changes': changes
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/actions')
def get_actions():
    """Get list of available actions for filtering."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT action FROM audit_log ORDER BY action')
        actions = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({'actions': actions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reports')
def reports():
    """Reports page."""
    return render_template('reports.html')

@app.route('/files')
def files():
    """Files page."""
    return render_template('files.html')

@app.route('/file/<path:file_path>')
def file_details(file_path):
    """File details page."""
    return render_template('file_details.html', file_path=file_path)

if __name__ == '__main__':
    # Initialize audit trail
    db_path = os.environ.get('PPT_AUDIT_DB', 'ppt_audit.db')
    watch_dir = os.environ.get('PPT_WATCH_DIR', '.')
    audit_trail = PPTAuditTrail(db_path, watch_dir)
    
    # Run the web server
    app.run(debug=True, host='0.0.0.0', port=5000)