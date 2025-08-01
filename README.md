# PowerPoint Audit Trail System

A comprehensive audit trail system for PowerPoint files that tracks file access, modifications, metadata changes, version history, and user activities. This system provides real-time monitoring, detailed reporting, and comprehensive analysis of PowerPoint file usage.

## Features

### 🔍 **Comprehensive Monitoring**
- Real-time file system monitoring for PowerPoint files
- Tracks all supported formats: `.ppt`, `.pptx`, `.pptm`, `.ppsx`, `.ppsm`
- Monitors file creation, modification, and deletion events
- Recursive directory monitoring with configurable settings

### 📊 **Detailed Metadata Extraction**
- PowerPoint document properties (title, author, subject, keywords)
- Slide structure analysis (layouts, shapes, notes)
- File versioning and change detection
- Cryptographic hash verification (SHA256)

### 📈 **Advanced Reporting**
- Multiple export formats: HTML, CSV, JSON
- Interactive dashboard with statistics
- Customizable report filtering by date, user, or file
- Beautiful HTML reports with responsive design

### 🛡️ **Security & Compliance**
- SQLite database for reliable audit storage
- File integrity verification through hashing
- User activity tracking and attribution
- Configurable retention policies

### ⚡ **Performance Optimized**
- Efficient database operations with indexing
- Batch processing for large file sets
- Configurable monitoring intervals
- Background processing support

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Setup

1. **Clone or download the project files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python ppt_audit_trail.py --help
   ```

### Dependencies
The system uses the following Python packages:
- `python-pptx` - PowerPoint file manipulation
- `watchdog` - File system monitoring
- `click` - Command-line interface
- `rich` - Beautiful terminal output
- `pandas` - Data analysis and reporting
- `jinja2` - HTML template rendering

## Quick Start

### 1. Start Monitoring
Monitor the current directory for PowerPoint file changes:
```bash
python ppt_audit_trail.py monitor
```

Monitor a specific directory:
```bash
python ppt_audit_trail.py monitor -d /path/to/presentations
```

### 2. View Audit History
Show recent audit events:
```bash
python ppt_audit_trail.py history
```

Show history for a specific file:
```bash
python ppt_audit_trail.py history -f "presentation.pptx"
```

### 3. Analyze Files
Analyze a specific PowerPoint file:
```bash
python ppt_audit_trail.py analyze presentation.pptx
```

### 4. Generate Reports
Generate an HTML audit report:
```bash
python ppt_audit_reports.py export --format html
```

Generate reports in all formats:
```bash
python ppt_audit_reports.py export --format all
```

## Detailed Usage

### Command Line Interface

#### Main Audit System (`ppt_audit_trail.py`)

**Monitor Command:**
```bash
python ppt_audit_trail.py monitor [OPTIONS]

Options:
  -d, --directory TEXT    Directory to monitor (default: current directory)
  -db, --database TEXT    Database file path (default: ppt_audit.db)
```

**History Command:**
```bash
python ppt_audit_trail.py history [OPTIONS]

Options:
  -db, --database TEXT    Database file path
  -f, --file-path TEXT    Specific file to show history for
  -l, --limit INTEGER     Number of recent events to show (default: 50)
```

**Analyze Command:**
```bash
python ppt_audit_trail.py analyze FILE_PATH [OPTIONS]

Options:
  -db, --database TEXT    Database file path
```

#### Report Generator (`ppt_audit_reports.py`)

**Export Command:**
```bash
python ppt_audit_reports.py export [OPTIONS]

Options:
  -db, --database TEXT      Database file path
  -f, --format [html|csv|json|all]  Export format (default: html)
  -o, --output TEXT         Output file path (without extension)
  --start-date TEXT         Start date filter (YYYY-MM-DD)
  --end-date TEXT           End date filter (YYYY-MM-DD)
  --user TEXT               Filter by user
  --file-path TEXT          Filter by file path (partial match)
  --title TEXT              Report title
```

**Dashboard Command:**
```bash
python ppt_audit_reports.py dashboard [OPTIONS]

Options:
  -db, --database TEXT    Database file path
```

## Configuration

The system uses a `config.json` file for customization:

```json
{
  "audit_settings": {
    "database_path": "ppt_audit.db",
    "watch_directory": ".",
    "recursive_monitoring": true,
    "supported_extensions": [".ppt", ".pptx", ".pptm", ".ppsx", ".ppsm"]
  },
  "monitoring": {
    "enable_file_watching": true,
    "scan_interval_minutes": 60,
    "backup_database": true,
    "max_file_size_mb": 100
  },
  "reporting": {
    "default_export_format": "html",
    "max_events_per_report": 10000,
    "report_output_directory": "./reports"
  }
}
```

## Examples

### Example 1: Basic Monitoring Setup
```bash
# Start monitoring the current directory
python ppt_audit_trail.py monitor

# In another terminal, check the activity
python ppt_audit_trail.py history -l 10
```

### Example 2: Enterprise Report Generation
```bash
# Generate a comprehensive report for the last month
python ppt_audit_reports.py export \
  --format all \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --title "January 2024 PowerPoint Activity Report"
```

### Example 3: User Activity Analysis
```bash
# View dashboard with statistics
python ppt_audit_reports.py dashboard

# Generate user-specific report
python ppt_audit_reports.py export \
  --user "john.doe" \
  --format html \
  --title "John Doe Activity Report"
```

### Example 4: File-Specific Audit Trail
```bash
# Analyze a specific presentation
python ppt_audit_trail.py analyze important_presentation.pptx

# Get detailed history for the file
python ppt_audit_trail.py history -f important_presentation.pptx
```

## Database Schema

The system creates an SQLite database with the following tables:

### `audit_events`
- `id` - Primary key
- `timestamp` - Event timestamp (ISO format)
- `event_type` - Type of event (created, modified, deleted, scanned)
- `file_path` - Full file path
- `file_name` - File name only
- `file_size` - File size in bytes
- `file_hash` - SHA256 hash of file content
- `user` - System user who performed the action
- `metadata` - JSON metadata from PowerPoint file
- `changes` - JSON array of detected changes
- `version` - File version number

### `file_versions`
- `id` - Primary key
- `file_path` - File path
- `version` - Version number
- `hash` - File hash for this version
- `timestamp` - Version timestamp
- `metadata` - Version metadata

### `user_activity`
- `id` - Primary key
- `user` - Username
- `action` - Action performed
- `file_path` - Affected file
- `timestamp` - Action timestamp
- `details` - Additional details

## Advanced Features

### 1. Automated Scanning
The system can automatically scan existing PowerPoint files in a directory:
```bash
python ppt_audit_trail.py monitor --scan-existing
```

### 2. Custom Database Location
Use a custom database file:
```bash
python ppt_audit_trail.py monitor -db /path/to/custom_audit.db
```

### 3. Filtered Reporting
Generate reports with specific criteria:
```bash
# Last week's activity
python ppt_audit_reports.py export \
  --start-date $(date -d '7 days ago' +%Y-%m-%d) \
  --format html

# Specific file type analysis
python ppt_audit_reports.py export \
  --file-path ".pptx" \
  --format csv
```

## Troubleshooting

### Common Issues

**1. Permission Errors**
- Ensure Python has read/write access to the monitoring directory
- Run with appropriate user permissions for file access

**2. Missing Dependencies**
```bash
pip install --upgrade -r requirements.txt
```

**3. Database Locked Errors**
- Ensure only one monitoring instance is running
- Check file permissions on the database file

**4. Large File Processing**
- Adjust `max_file_size_mb` in config.json
- Use batch processing for large datasets

### Performance Optimization

1. **Database Maintenance:**
   ```bash
   # Vacuum the database periodically
   sqlite3 ppt_audit.db "VACUUM;"
   ```

2. **Log Rotation:**
   - Configure log rotation for long-running instances
   - Set appropriate retention policies

3. **Memory Usage:**
   - Monitor memory usage for large file sets
   - Adjust batch sizes in configuration

## Security Considerations

- **File Hashing:** SHA256 ensures file integrity verification
- **Database Security:** Store audit database in secure location
- **Access Control:** Implement proper file system permissions
- **Data Retention:** Configure appropriate retention policies
- **Audit Trail Integrity:** Protect audit database from unauthorized modification

## Integration

### With Other Systems
The audit system can be integrated with:
- SIEM systems via JSON/CSV exports
- Backup systems for audit data preservation
- Monitoring systems via database queries
- Reporting dashboards via REST API (custom implementation)

### Programmatic Access
```python
from ppt_audit_trail import PPTAuditDatabase

# Connect to audit database
audit_db = PPTAuditDatabase("ppt_audit.db")

# Get file history
history = audit_db.get_file_history("presentation.pptx")

# Get user activity
activity = audit_db.get_user_activity("username", limit=100)
```

## License

This project is provided as-is for educational and compliance purposes. Ensure compliance with your organization's data handling and privacy policies when implementing audit trails.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the command help: `python ppt_audit_trail.py --help`
3. Examine log files for detailed error information
4. Verify file permissions and system requirements

---

**Version:** 1.0.0  
**Last Updated:** $(date)  
**Python Compatibility:** 3.8+