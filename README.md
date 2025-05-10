# PSD to Image Converter

A modern, cross-platform application for converting Adobe Photoshop (PSD) files to various image formats. Built with Python and Tkinter, this tool provides a user-friendly interface for batch processing PSD files.

## Features

- Convert PSD files to multiple formats (PNG, JPEG, WebP, BMP, TIFF)
- Batch processing of multiple files and folders
- Adjustable output quality and scaling
- Lossless compression options
- Detailed conversion logging
- Modern dark theme UI
- Cross-platform support (Windows, Linux, macOS)

## Installation

### From Source

1. Clone the repository:

```bash
git clone https://github.com/yourusername/psd-to-image-converter.git
cd psd-to-image-converter
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running from Source

```bash
python src/main.py
```

### Building Executable

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Build the executable:

```bash
pyinstaller psd_converter.spec
```

The executable will be created in the `dist` directory.

## Usage

1. Launch the application
2. Add PSD files or folders using the "Add File" or "Add Folder" buttons
3. Select an output directory
4. Configure output settings:
   - Choose output format
   - Adjust quality (1-100)
   - Set scale percentage
   - Enable/disable lossless compression
   - Toggle optimization
   - Enable detailed output for conversion logs
5. Click "Start Conversion" to begin processing
6. Monitor progress in the status window

## Output Formats

- PNG: Supports transparency, lossless compression
- JPEG: High compression, no transparency
- WebP: Modern format with good compression and transparency support
- BMP: Uncompressed, high quality
- TIFF: High quality with optional compression

## Development

### Project Structure

```
psd-to-image-converter/
├── src/
│   ├── config/
│   │   └── settings.py
│   ├── core/
│   │   └── converter.py
│   ├── gui/
│   │   └── app.py
│   ├── utils/
│   │   ├── dependencies.py
│   │   └── metadata.py
│   └── main.py
├── requirements.txt
├── psd_converter.spec
└── README.md
```

### Dependencies

- Python 3.8+
- Pillow (PIL)
- psd-tools
- python-dateutil

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Pillow](https://python-pillow.org/) for image processing
- [psd-tools](https://github.com/psd-tools/psd-tools) for PSD file handling
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework
