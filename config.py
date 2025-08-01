"""
Configuration file for PowerPoint Audit Trail System
"""

import os
from pathlib import Path

# Database configuration
DATABASE_PATH = "audit_trail.db"

# Monitoring configuration
WATCH_DIRECTORY = "."  # Current directory by default
RECURSIVE_MONITORING = True  # Monitor subdirectories

# File extensions to monitor
POWERPOINT_EXTENSIONS = ['.pptx', '.ppt']

# Backup configuration
BACKUP_DIRECTORY = "audit_backups"
MAX_BACKUP_AGE_DAYS = 30  # Delete backups older than this
MAX_BACKUP_SIZE_MB = 1000  # Maximum backup directory size in MB

# Logging configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "audit_trail.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Report configuration
REPORT_OUTPUT_FILE = "audit_report.html"
REPORT_TEMPLATE_DIR = "templates"

# Performance configuration
HASH_CHUNK_SIZE = 4096  # Bytes to read at once when calculating file hashes
FILE_SCAN_INTERVAL = 60  # Seconds between file system scans

# Notification configuration (future feature)
ENABLE_EMAIL_NOTIFICATIONS = False
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_FROM = ""
EMAIL_TO = []

# Security configuration
ENCRYPT_DATABASE = False
ENCRYPTION_KEY = ""  # Set this for database encryption

# Retention policy
MAX_LOG_ENTRIES = 10000  # Maximum number of log entries to keep
CLEANUP_INTERVAL_HOURS = 24  # How often to run cleanup

# Advanced configuration
ENABLE_SLIDE_LEVEL_TRACKING = True  # Track individual slide changes
ENABLE_CONTENT_EXTRACTION = True  # Extract text content from slides
ENABLE_METADATA_TRACKING = True  # Track file metadata changes

# File size limits
MAX_FILE_SIZE_MB = 100  # Skip files larger than this
MIN_FILE_SIZE_BYTES = 1024  # Skip files smaller than this

# Exclude patterns (files/directories to ignore)
EXCLUDE_PATTERNS = [
    "*.tmp",
    "~*",
    ".git/*",
    "node_modules/*",
    "__pycache__/*",
    "*.log"
]

# Include patterns (only monitor these if specified)
INCLUDE_PATTERNS = []  # Empty means monitor all PowerPoint files

# Database schema version
SCHEMA_VERSION = "1.0"

# Performance tuning
BATCH_SIZE = 100  # Number of records to process in batches
CONNECTION_TIMEOUT = 30  # Database connection timeout in seconds

# Export configuration
CSV_EXPORT_ENCODING = "utf-8"
JSON_EXPORT_INDENT = 2

# Web interface configuration (future feature)
WEB_INTERFACE_ENABLED = False
WEB_INTERFACE_PORT = 8080
WEB_INTERFACE_HOST = "localhost"

# Backup verification
VERIFY_BACKUPS = True  # Verify backup integrity after creation
BACKUP_COMPRESSION = False  # Compress backup files

# Change detection sensitivity
MIN_CHANGE_INTERVAL_SECONDS = 1  # Minimum time between change detections
IGNORE_TEMPORARY_CHANGES = True  # Ignore changes that are quickly reverted

# User interface
SHOW_PROGRESS_BAR = True
VERBOSE_OUTPUT = False
COLOR_OUTPUT = True  # Use colors in terminal output

# Error handling
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5
CONTINUE_ON_ERROR = True  # Continue monitoring even if errors occur

# Memory management
MAX_MEMORY_USAGE_MB = 512  # Maximum memory usage for the application
GARBAGE_COLLECTION_INTERVAL = 1000  # Run garbage collection every N operations