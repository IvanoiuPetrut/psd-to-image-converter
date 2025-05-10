"""Utility functions for handling file metadata."""

import os
from datetime import datetime
from xml.etree import ElementTree
from dateutil import parser as date_parser
from psd_tools import PSDImage

def parse_xmp_creation_date(xmp_string):
    """
    Parses XMP metadata string to find creation date.
    Tries photoshop:DateCreated first, then dc:date.
    """
    try:
        namespaces = {
            'x': 'adobe:ns:meta/',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'photoshop': 'http://ns.adobe.com/photoshop/1.0/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'xmp': 'http://ns.adobe.com/xap/1.0/'
        }

        root = ElementTree.fromstring(xmp_string)
        
        # Try photoshop:DateCreated
        date_created_element = root.find(".//photoshop:DateCreated", namespaces)
        if date_created_element is not None and date_created_element.text:
            dt_obj = date_parser.parse(date_created_element.text)
            return dt_obj.strftime("%Y-%m-%d_%H%M%S")

        # Fallback to dc:date
        dc_date_elements = root.findall(".//dc:date", namespaces)
        if dc_date_elements:
            dt_obj = date_parser.parse(dc_date_elements[0].text)
            return dt_obj.strftime("%Y-%m-%d_%H%M%S")
            
    except (ElementTree.ParseError, Exception) as e:
        print(f"    Could not parse date from XMP: {e}")
    return None

def get_file_creation_date_str(psd_file_path):
    """
    Gets the creation date from PSD metadata (XMP) or falls back to file system's ctime.
    Returns a string formatted as 'YYYY-MM-DD_HHMMSS'.
    """
    try:
        psd_image = PSDImage.open(psd_file_path)
        if psd_image.xmp_metadata:
            date_from_xmp = parse_xmp_creation_date(psd_image.xmp_metadata)
            if date_from_xmp:
                print(f"  Successfully extracted XMP creation date for {os.path.basename(psd_file_path)}")
                return date_from_xmp
            print(f"  XMP metadata found for {os.path.basename(psd_file_path)}, but no recognized creation date tag.")
        else:
            print(f"  No XMP metadata found in {os.path.basename(psd_file_path)}.")
    except Exception as e:
        print(f"  Could not read or parse PSD metadata for {os.path.basename(psd_file_path)}: {e}")

    # Fallback to file system timestamp
    print(f"  Falling back to file system timestamp for {os.path.basename(psd_file_path)}.")
    try:
        timestamp = os.path.getctime(psd_file_path)
        dt_object = datetime.fromtimestamp(timestamp)
        return dt_object.strftime("%Y-%m-%d_%H%M%S")
    except Exception as e:
        print(f"  Could not get file system timestamp for {os.path.basename(psd_file_path)}: {e}")
        return datetime.now().strftime("%Y-%m-%d_%H%M%S") + "_fallback" 