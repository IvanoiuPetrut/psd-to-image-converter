"""Core functionality for PSD to image conversion."""

import os
import sys
from PIL import Image, UnidentifiedImageError

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.metadata import get_file_creation_date_str

class OutputSettings:
    """Class to hold output settings for image conversion."""
    def __init__(self, **kwargs):
        self.format = kwargs.get('format', 'png')
        self.quality = kwargs.get('quality', 90)
        self.scale = kwargs.get('scale', 100)
        self.lossless = kwargs.get('lossless', False)
        self.optimize = kwargs.get('optimize', True)
        self.detailed_output = kwargs.get('detailed_output', False)

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

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Handle filename collisions
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
        save_kwargs = _get_save_kwargs(output_settings)
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

def _get_save_kwargs(output_settings):
    """Get the appropriate save parameters based on output format."""
    format_lower = output_settings.format.lower()
    
    if format_lower == 'webp':
        return {
            'format': 'WEBP',
            'quality': output_settings.quality,
            'lossless': output_settings.lossless,
            'optimize': output_settings.optimize
        }
    elif format_lower in ['jpg', 'jpeg']:
        return {
            'format': 'JPEG',
            'quality': output_settings.quality,
            'optimize': output_settings.optimize
        }
    elif format_lower == 'png':
        return {
            'format': 'PNG',
            'optimize': output_settings.optimize
        }
    elif format_lower == 'bmp':
        return {
            'format': 'BMP'
        }
    elif format_lower == 'tiff':
        return {
            'format': 'TIFF',
            'compression': 'tiff_lzw' if output_settings.optimize else None
        }
    else:
        raise ValueError(f"Unsupported output format '{output_settings.format}'") 