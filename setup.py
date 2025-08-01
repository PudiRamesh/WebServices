#!/usr/bin/env python3
"""
Setup script for PowerPoint Audit Trail System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ppt-audit-trail",
    version="1.0.0",
    author="Auto-generated",
    author_email="admin@example.com",
    description="A comprehensive audit trail system for PowerPoint files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/ppt-audit-trail",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Logging",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ppt-audit=ppt_audit_trail:cli",
            "ppt-reports=ppt_audit_reports:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config.json", "*.md", "*.txt"],
    },
    keywords="powerpoint audit trail monitoring compliance security",
    project_urls={
        "Bug Reports": "https://github.com/example/ppt-audit-trail/issues",
        "Source": "https://github.com/example/ppt-audit-trail",
        "Documentation": "https://github.com/example/ppt-audit-trail/wiki",
    },
)