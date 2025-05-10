"""Configuration settings for the PSD to Image Converter application."""

# GUI Colors
COLORS = {
    'bg': '#1e1e1e',
    'fg': '#e0e0e0',
    'accent': '#007acc',
    'button': '#2d2d2d',
    'button_hover': '#3d3d3d',
    'entry': '#2d2d2d',
    'listbox': '#2d2d2d',
    'text': '#2d2d2d',
    'progress': '#007acc',
    'border': '#2d2d2d'
}

# Default output settings
DEFAULT_OUTPUT_SETTINGS = {
    'format': 'png',
    'quality': 90,
    'scale': 100,
    'lossless': False,
    'optimize': True,
    'detailed_output': False
}

# Supported output formats
SUPPORTED_FORMATS = ['png', 'jpg', 'webp', 'bmp', 'tiff']

# Application settings
APP_TITLE = "PSD to Image Converter"
APP_GEOMETRY = "800x600" 