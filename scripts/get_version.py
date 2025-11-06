#!/usr/bin/env python3
"""
Simple script to get the current project version.

Usage:
    python scripts/get_version.py
"""

from pathlib import Path


def get_version() -> str:
    """Read version from VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    if not version_file.exists():
        raise FileNotFoundError("VERSION file not found")
    return version_file.read_text().strip()


if __name__ == "__main__":
    print(get_version())
