#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from psd_tools import PSDImage
from xml.etree import ElementTree # For parsing XMP metadata
from dateutil import parser as date_parser # For robust date string parsing

# --- Configuration ---
# IMPORTANT: Please update these paths before running the script!

# List of source directories or direct PSD file paths.
# Example:
# source_file_paths = [
#     "/Users/yourname/Documents/PSD_Projects/ProjectA",
#     "/Users/yourname/Desktop/Old_PSDs",
#     "/Users/yourname/Downloads/single_file.psd"
# ]

#  "D:/For linux hdd/Art/My art/2019 - Digital/400 Dynamic Gesture",
#     "D:/For linux hdd/Art/My art/2019 - Digital/Gesture",
#     "D:/For linux hdd/Art/My art/2019 - Digital/Landscape",
#     "D:/For linux hdd/Art/My art/2019 - Digital/Portrait",
#     "D:/For linux hdd/Art/My art/2019 - Digital/Random",
#     "D:/For linux hdd/Art/My art/2020 - Digital",
#     "D:/For linux hdd/Art/My art/2021"
#     "D:/For linux hdd/Art/My art/2022"
#     "D:/For linux hdd/Art/My art/2023 - PSD"
#     "D:/For linux hdd/Art/My art/2024 - PSD"
#     "D:/Art/2025"

source_file_paths = [
    # Add your source folder paths or specific .psd file paths here
    # e.g., "C:/Users/YourUser/Pictures/MyPSDs",
    #       "/mnt/c/Users/YourUser/Documents/PhotoshopFiles"
    # "D:/For linux hdd/Art/My art/2019 - Digital/400 Dynamic Gesture",
    # "D:/For linux hdd/Art/My art/2019 - Digital/Gesture",
    # "D:/For linux hdd/Art/My art/2019 - Digital/Landscape",
    # "D:/For linux hdd/Art/My art/2019 - Digital/Portrait",
    # "D:/For linux hdd/Art/My art/2019 - Digital/Random",
    # "D:/For linux hdd/Art/My art/2020 - Digital",
    "D:/For linux hdd/Art/My art/2021",
    "D:/For linux hdd/Art/My art/2022",
    "D:/For linux hdd/Art/My art/2023 - PSD",
    "D:/For linux hdd/Art/My art/2024 - PSD",
    # "D:/Art/2025"
]

# Directory where converted files will be saved.
# Example:
# output_save_path = "/Users/yourname/Documents/Converted_Images"
output_save_path = "D:/Art/PNG export" # Add your output folder path here, e.g., "C:/Users/YourUser/Pictures/Converted"

# Desired output format: "png", "jpg", or "webp".
selected_format = "png"  # Change to "jpg" or "webp" as needed

# --- End Configuration ---

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

def parse_xmp_creation_date(xmp_string):
    """
    Parses XMP metadata string to find creation date.
    Tries photoshop:DateCreated first, then dc:date.
    """
    try:
        # Define common XML namespaces
        namespaces = {
            'x': 'adobe:ns:meta/',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'photoshop': 'http://ns.adobe.com/photoshop/1.0/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'xmp': 'http://ns.adobe.com/xap/1.0/'
        }

        # The XMP data might be wrapped in <x:xmpmeta>...
        # We need to find the rdf:Description tag
        root = ElementTree.fromstring(xmp_string)
        
        # Try to find photoshop:DateCreated
        # Path might be: x:xmpmeta/rdf:RDF/rdf:Description/photoshop:DateCreated
        date_created_element = root.find(".//photoshop:DateCreated", namespaces)
        if date_created_element is not None and date_created_element.text:
            dt_obj = date_parser.parse(date_created_element.text)
            return dt_obj.strftime("%Y-%m-%d_%H%M%S")

        # Fallback: Try to find dc:date (could be multiple, often the earliest is creation)
        # Path might be: x:xmpmeta/rdf:RDF/rdf:Description/dc:date
        dc_date_elements = root.findall(".//dc:date", namespaces)
        if dc_date_elements:
            # Assuming the first dc:date is relevant if multiple exist
            # More sophisticated logic might sort them if needed
            dt_obj = date_parser.parse(dc_date_elements[0].text)
            return dt_obj.strftime("%Y-%m-%d_%H%M%S")
            
    except ElementTree.ParseError as pe:
        print(f"    XMP parsing error: {pe}. Malformed XMP data.")
    except Exception as e:
        # Catch other potential errors during parsing (e.g., date_parser.parse)
        print(f"    Could not parse date from XMP: {e}")
    return None

def get_file_creation_date_str(psd_file_path):
    """
    Tries to get the creation date from PSD metadata (XMP).
    Falls back to file system's ctime if metadata is not found or unparsable.
    Returns a string formatted as 'YYYY-MM-DD_HHMMSS'.
    """
    # Attempt 1: Extract from XMP metadata using psd-tools
    try:
        psd_image = PSDImage.open(psd_file_path)
        if psd_image.xmp_metadata:
            # xmp_metadata is typically a string of XML data
            date_from_xmp = parse_xmp_creation_date(psd_image.xmp_metadata)
            if date_from_xmp:
                print(f"  Successfully extracted XMP creation date for {os.path.basename(psd_file_path)}")
                return date_from_xmp
            else:
                print(f"  XMP metadata found for {os.path.basename(psd_file_path)}, but no recognized creation date tag.")
        else:
            print(f"  No XMP metadata found in {os.path.basename(psd_file_path)}.")
    except Exception as e:
        print(f"  Could not read or parse PSD metadata for {os.path.basename(psd_file_path)}: {e}")

    # Attempt 2: Fallback to file system's creation time (or last metadata change on Unix)
    print(f"  Falling back to file system timestamp for {os.path.basename(psd_file_path)}.")
    try:
        # os.path.getctime() behavior varies:
        # - Windows: File creation time.
        # - Unix/Linux: Time of last metadata change.
        # os.path.getmtime() is last modification time, might also be an option.
        timestamp = os.path.getctime(psd_file_path)
        dt_object = datetime.fromtimestamp(timestamp)
        return dt_object.strftime("%Y-%m-%d_%H%M%S")
    except Exception as e:
        print(f"  Could not get file system timestamp for {os.path.basename(psd_file_path)}: {e}")
        # Ultimate fallback if everything else fails (e.g., permissions issues)
        return datetime.now().strftime("%Y-%m-%d_%H%M%S") + "_fallback"

def convert_psd_to_image(psd_path, output_dir, output_settings, filename_base):
    """
    Converts a single PSD file to the specified image format.
    Handles filename collisions by appending a counter.
    """
    try:
        # Open the PSD file
        image = Image.open(psd_path)
        
        if output_settings.detailed_output:
            print(f"  Original image size: {image.width}x{image.height}")
            print(f"  Image mode: {image.mode}")

        # Apply scaling if needed
        if output_settings.scale != 100:
            new_width = int(image.width * output_settings.scale / 100)
            new_height = int(image.height * output_settings.scale / 100)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            if output_settings.detailed_output:
                print(f"  Scaled to: {new_width}x{new_height}")

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")

        # Determine output filename and handle potential collisions
        base_output_filename = f"{filename_base}.{output_settings.format.lower()}"
        output_path = os.path.join(output_dir, base_output_filename)
        
        counter = 1
        while os.path.exists(output_path):
            new_filename_base = f"{filename_base}_{counter}"
            output_filename_with_counter = f"{new_filename_base}.{output_settings.format.lower()}"
            output_path = os.path.join(output_dir, output_filename_with_counter)
            counter += 1
        
        final_output_filename = os.path.basename(output_path)

        print(f"  Converting '{os.path.basename(psd_path)}' to '{final_output_filename}' as {output_settings.format.upper()}...")

        # Handle transparency and color modes
        if output_settings.format.lower() in ['png', 'webp']:
            if image.mode in ('P', 'PA') and 'transparency' in image.info:
                image = image.convert("RGBA")
                if output_settings.detailed_output:
                    print("  Converted palette image with transparency to RGBA")
            elif image.mode not in ('RGBA', 'LA'):
                pass

        elif output_settings.format.lower() in ['jpg', 'jpeg']:
            if image.mode in ['RGBA', 'LA', 'P', 'PA']:
                background = Image.new("RGB", image.size, (255, 255, 255))
                try:
                    background.paste(image, mask=image.split()[-1] if image.mode in ['RGBA', 'LA', 'PA'] else None)
                except IndexError:
                    background.paste(image)
                image = background
                if output_settings.detailed_output:
                    print("  Converted image with transparency to RGB with white background")
            elif image.mode == 'CMYK':
                image = image.convert('RGB')
                if output_settings.detailed_output:
                    print("  Converted CMYK to RGB")

        # Save the image with appropriate settings
        save_kwargs = {}
        
        if output_settings.format.lower() == 'webp':
            save_kwargs.update({
                'format': 'WEBP',
                'quality': output_settings.quality,
                'lossless': output_settings.lossless,
                'optimize': output_settings.optimize
            })
            if output_settings.detailed_output:
                print(f"  WebP settings: quality={output_settings.quality}, lossless={output_settings.lossless}, optimize={output_settings.optimize}")
        elif output_settings.format.lower() in ['jpg', 'jpeg']:
            save_kwargs.update({
                'format': 'JPEG',
                'quality': output_settings.quality,
                'optimize': output_settings.optimize
            })
            if output_settings.detailed_output:
                print(f"  JPEG settings: quality={output_settings.quality}, optimize={output_settings.optimize}")
        elif output_settings.format.lower() == 'png':
            save_kwargs.update({
                'format': 'PNG',
                'optimize': output_settings.optimize
            })
            if output_settings.detailed_output:
                print(f"  PNG settings: optimize={output_settings.optimize}")
        elif output_settings.format.lower() == 'bmp':
            save_kwargs.update({
                'format': 'BMP'
            })
            if output_settings.detailed_output:
                print("  BMP format selected (no additional settings)")
        elif output_settings.format.lower() == 'tiff':
            save_kwargs.update({
                'format': 'TIFF',
                'compression': 'tiff_lzw' if output_settings.optimize else None
            })
            if output_settings.detailed_output:
                print(f"  TIFF settings: compression={'LZW' if output_settings.optimize else 'None'}")
        else:
            print(f"    Unsupported output format '{output_settings.format}' for saving. Skipping.")
            return False

        image.save(output_path, **save_kwargs)
        
        if output_settings.detailed_output:
            file_size = os.path.getsize(output_path) / 1024  # Size in KB
            print(f"  Saved file size: {file_size:.1f} KB")
            
        print(f"  Successfully converted and saved to '{output_path}'")
        return True

    except FileNotFoundError:
        print(f"  Error: PSD file not found at '{psd_path}'")
    except UnidentifiedImageError:
        print(f"  Error: Cannot identify image file. '{psd_path}' might be corrupted or not a valid PSD.")
    except Exception as e:
        print(f"  Error converting '{os.path.basename(psd_path)}': {e}")
    return False

def process_source_paths(sources, output_directory, target_format):
    """
    Iterates through source paths (files or directories).
    Finds PSD files and processes them.
    """
    if not os.path.exists(output_directory):
        try:
            os.makedirs(output_directory, exist_ok=True)
            print(f"Output directory created: {output_directory}")
        except OSError as e:
            print(f"Critical Error: Could not create output directory '{output_directory}': {e}")
            return

    psd_files_found = 0
    successful_conversions = 0

    for item_path in sources:
        if not os.path.exists(item_path):
            print(f"Warning: Source path '{item_path}' does not exist. Skipping.")
            continue

        if os.path.isfile(item_path):
            if item_path.lower().endswith(".psd"):
                print(f"\nProcessing single file: {item_path}")
                psd_files_found += 1
                creation_date_filename_base = get_file_creation_date_str(item_path)
                if convert_psd_to_image(item_path, output_directory, target_format, creation_date_filename_base):
                    successful_conversions +=1
            else:
                print(f"Skipping non-PSD file: {item_path}")
        elif os.path.isdir(item_path):
            print(f"\nScanning directory: {item_path}")
            for root, _, files in os.walk(item_path):
                for file in files:
                    if file.lower().endswith(".psd"):
                        full_psd_path = os.path.join(root, file)
                        print(f"Found PSD: {full_psd_path}")
                        psd_files_found += 1
                        creation_date_filename_base = get_file_creation_date_str(full_psd_path)
                        if convert_psd_to_image(full_psd_path, output_directory, target_format, creation_date_filename_base):
                            successful_conversions +=1
        else:
            print(f"Warning: Source path '{item_path}' is neither a file nor a directory. Skipping.")
            
    print(f"\n--- Process Summary ---")
    print(f"Total PSD files found: {psd_files_found}")
    print(f"Successfully converted: {successful_conversions}")
    print(f"Files saved to: {os.path.abspath(output_directory)}")


if __name__ == "__main__":
    # Ensure required libraries are installed
    ensure_dependencies()

    # Validate configuration
    if not source_file_paths:
        print("Configuration Error: 'source_file_paths' list is empty.")
        print("Please edit the script and add paths to your PSD files or folders.")
        sys.exit(1)

    if not output_save_path:
        print("Configuration Error: 'output_save_path' is not set.")
        print("Please edit the script and specify an output directory.")
        sys.exit(1)

    selected_format = selected_format.lower()
    if selected_format not in ["png", "jpg", "jpeg", "webp"]:
        print(f"Configuration Error: Invalid 'selected_format': {selected_format}.")
        print("Please choose 'png', 'jpg', or 'webp'.")
        sys.exit(1)
    if selected_format == "jpeg": # Normalize to jpg
        selected_format = "jpg"


    print("Starting PSD conversion process...")
    print(f"Source locations: {source_file_paths}")
    print(f"Output directory: {output_save_path}")
    print(f"Target format: {selected_format.upper()}")
    print("-" * 30)

    process_source_paths(source_file_paths, output_save_path, selected_format)

    print("\nConversion process finished.")
