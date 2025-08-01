# PowerPoint Audit Trail System

A comprehensive system for tracking and auditing changes to PowerPoint files with real-time monitoring, detailed change detection, and a modern web-based dashboard.

## Features

### 🔍 **Real-time File Monitoring**
- Monitors directories for PowerPoint files (.pptx, .ppt)
- Detects file creation, modification, and deletion events
- Uses file system watchers for immediate response

### 📊 **Detailed Change Analysis**
- Calculates SHA-256 hashes for file integrity
- Analyzes presentation structure (slides, shapes, text, images, charts)
- Extracts metadata (title, author, creation date, etc.)
- Tracks slide-level changes and content modifications

### 🗄️ **Comprehensive Audit Logging**
- SQLite database for persistent storage
- Detailed event logging with timestamps
- File snapshots for historical comparison
- Change history with before/after analysis

### 🌐 **Modern Web Dashboard**
- Real-time statistics and charts
- Filterable audit reports
- File management interface
- Detailed file analysis views
- Responsive design for all devices

### 📈 **Advanced Reporting**
- Activity charts and trends
- File type distribution analysis
- Custom date range filtering
- Export capabilities
- Pagination for large datasets

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd powerpoint-audit-trail
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the system**
   ```bash
   # Start the audit trail monitoring
   python ppt_audit_trail.py --watch-dir /path/to/your/presentations
   
   # Start the web dashboard (in another terminal)
   python audit_dashboard.py
   ```

## Usage

### Command Line Interface

#### Basic Monitoring
```bash
# Monitor current directory
python ppt_audit_trail.py

# Monitor specific directory
python ppt_audit_trail.py --watch-dir /path/to/presentations

# Use custom database location
python ppt_audit_trail.py --db-path /path/to/audit.db
```

#### Generate Reports
```bash
# Generate audit report for specific file
python ppt_audit_trail.py --report /path/to/presentation.pptx

# Generate report with date range
python ppt_audit_trail.py --report /path/to/presentation.pptx --start-date 2024-01-01 --end-date 2024-01-31

# Scan existing files only (no monitoring)
python ppt_audit_trail.py --scan-only
```

### Web Dashboard

1. **Start the dashboard server**
   ```bash
   python audit_dashboard.py
   ```

2. **Access the dashboard**
   - Open your browser and go to `http://localhost:5000`
   - The dashboard will show real-time statistics and audit data

3. **Navigate the interface**
   - **Dashboard**: Overview with charts and recent activity
   - **Files**: List of all monitored PowerPoint files
   - **Reports**: Detailed audit reports with filtering options

## Configuration

### Environment Variables
```bash
# Database path
export PPT_AUDIT_DB=/path/to/audit.db

# Watch directory
export PPT_WATCH_DIR=/path/to/presentations
```

### Database Schema

The system uses three main tables:

1. **audit_log**: Records all file events
   - timestamp, file_path, action, user, details, file_hash, file_size, slide_count, change_type

2. **file_snapshots**: Stores file state snapshots
   - timestamp, file_path, file_hash, file_size, slide_count, slide_details, metadata

3. **change_history**: Tracks detailed changes
   - timestamp, file_path, old_hash, new_hash, change_summary, detailed_changes

## API Endpoints

The web dashboard provides RESTful API endpoints:

- `GET /api/stats` - Dashboard statistics
- `GET /api/events` - Audit events with pagination and filtering
- `GET /api/files` - List of monitored files
- `GET /api/file/<path>` - Detailed file information
- `GET /api/actions` - Available action types

## File Structure

```
powerpoint-audit-trail/
├── ppt_audit_trail.py      # Main audit trail system
├── audit_dashboard.py      # Web dashboard server
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── reports.html
│   ├── files.html
│   └── file_details.html
├── static/                # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── ppt_audit.db          # SQLite database (created automatically)
```

## Security Considerations

- The system only monitors file system events and does not modify files
- File hashes are used for integrity verification
- Database access is restricted to local connections
- No sensitive file content is stored, only metadata and structure information

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Ensure the script has read access to the monitored directory
   - Run with appropriate user permissions

2. **Database Locked**
   - Close any other applications using the database
   - Check file permissions on the database file

3. **Dashboard Not Loading**
   - Verify Flask is installed: `pip install Flask`
   - Check if port 5000 is available
   - Review console output for error messages

4. **No Events Detected**
   - Confirm PowerPoint files exist in the monitored directory
   - Check file extensions (.pptx, .ppt)
   - Verify the monitoring process is running

### Log Files

The system creates log files for debugging:
- `ppt_audit.log` - Main application logs
- Console output for real-time monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the log files
3. Create an issue with detailed information about your problem

## Roadmap

- [ ] Email notifications for file changes
- [ ] Integration with version control systems
- [ ] Advanced change visualization
- [ ] Multi-user support with authentication
- [ ] Cloud storage integration
- [ ] Mobile app companion
- [ ] Advanced analytics and machine learning insights