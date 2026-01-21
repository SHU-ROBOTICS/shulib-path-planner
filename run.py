#!/usr/bin/env python3
"""
shulib Path Planner - Entry Point

Run this script to start the path planner application.

Usage:
    python run.py
"""

import sys


def main():
    """Main entry point."""
    # Check Python version
    if sys.version_info < (3, 10):
        print(f"Error: Python 3.10+ required, you have {sys.version}")
        sys.exit(1)
    
    # Check tkinter
    try:
        import tkinter
    except ImportError:
        print("Error: tkinter not found.")
        print("Install it with:")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  Fedora: sudo dnf install python3-tkinter")
        print("  macOS: brew install python-tk")
        sys.exit(1)
    
    # Run the app
    from path_planner.app import PathPlannerApp
    app = PathPlannerApp()
    app.run()


if __name__ == "__main__":
    main()