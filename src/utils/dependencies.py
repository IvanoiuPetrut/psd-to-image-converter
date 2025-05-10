"""Utility functions for checking and managing dependencies."""

import sys

def ensure_dependencies():
    """Checks for required libraries and provides installation instructions."""
    missing_libraries = []
    
    try:
        import PIL
    except ImportError:
        missing_libraries.append("Pillow")
        
    try:
        import psd_tools
    except ImportError:
        missing_libraries.append("psd-tools")
        
    try:
        import dateutil
    except ImportError:
        missing_libraries.append("python-dateutil")

    if missing_libraries:
        print("Error: Missing required Python libraries.")
        print("Please install them by running:")
        for lib in missing_libraries:
            print(f"  pip install {lib}")
        sys.exit(1) 