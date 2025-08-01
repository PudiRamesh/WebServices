# PowerPoint Audit Trail System

A comprehensive system for tracking changes to PowerPoint files with detailed audit logging, automatic backups, and reporting capabilities.

## Features

- **Real-time File Monitoring**: Automatically detects changes to PowerPoint files (.pptx, .ppt)
- **Detailed Audit Logging**: Tracks file creation, modification, deletion, and movement
- **Automatic Backups**: Creates timestamped backups of files before changes
- **Content Analysis**: Extracts and tracks slide content and metadata
- **SQLite Database**: Stores all audit information in a searchable database
- **HTML Reports**: Generates comprehensive audit reports
- **Command-line Tools**: Query and analyze audit data
- **Configurable**: Extensive configuration options for customization

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Manual Installation

If you prefer to install dependencies manually:

```bash
pip install python-pptx==0.6.21
pip install watchdog==3.0.0
```

## Quick Start

### 1. Start Monitoring

```bash
python ppt_audit_trail.py
```

This will:
- Start monitoring the current directory for PowerPoint files
- Create a SQLite database (`audit_trail.db`) to store audit information
- Create a backup directory (`audit_backups`) for file backups
- Generate logs in `audit_trail.log`

### 2. Monitor a Specific Directory

```bash
python ppt_audit_trail.py --watch /path/to/your/presentations
```

### 3. Stop Monitoring

Press `Ctrl+C` to stop monitoring. The system will automatically generate an HTML audit report.

## Usage Examples

### Basic Monitoring

```bash
# Start monitoring current directory
python ppt_audit_trail.py

# Monitor specific directory
python ppt_audit_trail.py --watch /path/to/presentations

# Use custom database location
python ppt_audit_trail.py --db /path/to/audit.db
```

### Querying Audit Data

```bash
# Show recent changes
python audit_query.py

# List all tracked files
python audit_query.py --list-files

# Show file history
python audit_query.py --file-history "presentation.pptx"

# Show changes in date range
python audit_query.py --date-range 2024-01-01 2024-01-31

# Show statistics
python audit_query.py --stats

# Export to CSV
python audit_query.py --export audit_data.csv
```

## Configuration

Edit `config.py` to customize the system behavior:

```python
# Database configuration
DATABASE_PATH = "audit_trail.db"

# Monitoring configuration
WATCH_DIRECTORY = "."
RECURSIVE_MONITORING = True

# File extensions to monitor
POWERPOINT_EXTENSIONS = ['.pptx', '.ppt']

# Backup configuration
BACKUP_DIRECTORY = "audit_backups"
MAX_BACKUP_AGE_DAYS = 30
```

## Database Schema

The system uses three main tables:

### Files Table
- `id`: Primary key
- `file_path`: Full path to the file
- `file_name`: File name
- `file_size`: File size in bytes
- `file_hash`: SHA-256 hash of file content
- `first_seen`: When the file was first discovered
- `last_modified`: Last modification timestamp

### Changes Table
- `id`: Primary key
- `file_id`: Foreign key to files table
- `change_type`: Type of change (FILE_CREATED, FILE_MODIFIED, etc.)
- `change_description`: Description of the change
- `old_hash`: Previous file hash
- `new_hash`: New file hash
- `backup_path`: Path to backup file
- `timestamp`: When the change occurred
- `user_info`: User information (future feature)

### Slides Table
- `id`: Primary key
- `file_id`: Foreign key to files table
- `slide_number`: Slide number in presentation
- `slide_hash`: Hash of slide content
- `slide_content`: Extracted text content
- `timestamp`: When slide was analyzed

## File Structure

```
ppt-audit-trail/
├── ppt_audit_trail.py      # Main monitoring script
├── audit_query.py          # Query and analysis tool
├── config.py              # Configuration file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── audit_trail.db        # SQLite database (created automatically)
├── audit_trail.log       # Application logs (created automatically)
├── audit_backups/        # File backups directory (created automatically)
└── audit_report.html     # Generated audit report
```

## Features in Detail

### Real-time Monitoring
- Uses `watchdog` library for efficient file system monitoring
- Detects file creation, modification, deletion, and movement
- Supports recursive directory monitoring
- Configurable file type filtering

### Automatic Backups
- Creates timestamped backups before any file changes
- Stores backups in organized directory structure
- Configurable backup retention policy
- Backup integrity verification

### Content Analysis
- Extracts text content from PowerPoint slides
- Tracks slide-level changes
- Generates content hashes for change detection
- Stores slide metadata

### Audit Reporting
- HTML reports with detailed change history
- CSV export functionality
- Statistical analysis
- Date range filtering

### Database Management
- SQLite database for portability
- Efficient indexing for fast queries
- Automatic schema management
- Data integrity constraints

## Advanced Usage

### Custom Configuration

Create a custom configuration file:

```python
# custom_config.py
from config import *

# Override default settings
WATCH_DIRECTORY = "/path/to/presentations"
MAX_BACKUP_AGE_DAYS = 7
LOG_LEVEL = "DEBUG"
```

### Programmatic Usage

```python
from ppt_audit_trail import PowerPointAuditTrail

# Initialize audit system
audit = PowerPointAuditTrail(watch_directory="/path/to/monitor")

# Start monitoring
audit.start_monitoring()

# Generate report
audit.generate_audit_report("custom_report.html")

# Stop monitoring
audit.stop_monitoring()
```

### Query Database Directly

```python
import sqlite3

conn = sqlite3.connect("audit_trail.db")
cursor = conn.cursor()

# Get all changes for a specific file
cursor.execute("""
    SELECT c.change_type, c.timestamp, f.file_name
    FROM changes c
    JOIN files f ON c.file_id = f.id
    WHERE f.file_name = ?
    ORDER BY c.timestamp DESC
""", ("presentation.pptx",))

changes = cursor.fetchall()
conn.close()
```

## Troubleshooting

### Common Issues

1. **Permission Errors**
   - Ensure the script has read/write permissions to the monitored directory
   - Check database file permissions

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Verify Python version (3.7+)

3. **Database Locked**
   - Close any other applications using the database
   - Check for multiple instances of the monitoring script

4. **Large File Performance**
   - Adjust `MAX_FILE_SIZE_MB` in config.py
   - Increase `HASH_CHUNK_SIZE` for better performance

### Log Files

Check `audit_trail.log` for detailed error information:

```bash
tail -f audit_trail.log
```

### Database Maintenance

```bash
# Compact database
sqlite3 audit_trail.db "VACUUM;"

# Check database integrity
sqlite3 audit_trail.db "PRAGMA integrity_check;"
```

## Security Considerations

- Database files contain sensitive file information
- Backup files may contain confidential presentation content
- Consider encrypting the database for sensitive environments
- Implement proper access controls for audit logs

## Performance Optimization

- Adjust `HASH_CHUNK_SIZE` for optimal performance
- Use `MAX_FILE_SIZE_MB` to skip large files
- Configure `BATCH_SIZE` for database operations
- Enable backup compression for storage efficiency

## Future Enhancements

- Web-based dashboard
- Email notifications
- Integration with version control systems
- Advanced content diffing
- User authentication and authorization
- API for external integrations

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
3. Create an issue on the project repository

## Changelog

### Version 1.0.0
- Initial release
- Basic file monitoring
- SQLite database storage
- HTML report generation
- Command-line query tools