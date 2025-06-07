#!/usr/bin/env python
"""
Test script to verify PIL image processing functionality.
This script creates a test image, saves it to a temporary file,
then tries to open and process it to verify PIL is working correctly.
"""

import os
import io
import base64
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import PIL
try:
    from PIL import Image, ImageDraw, ImageFont
    logger.info("Successfully imported PIL modules")
except ImportError as e:
    logger.error(f"Failed to import PIL: {e}")
    exit(1)

def create_test_image(color='red', size=(100, 100)):
    """Create a test image and return it."""
    try:
        logger.info(f"Creating test image with color {color} and size {size}")
        img = Image.new('RGB', size, color=color)
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 90, 90], fill='blue', outline='white')
        draw.text((25, 40), "Test", fill='white')
        return img
    except Exception as e:
        logger.error(f"Error creating test image: {e}")
        return None

def save_and_load_image():
    """Save a test image to a temporary file and then load it back."""
    try:
        # Create a test image
        img = create_test_image()
        if not img:
            return False
            
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_path = temp_file.name
        temp_file.close()
        
        logger.info(f"Saving test image to {temp_path}")
        img.save(temp_path)
        
        # Try to open the image
        logger.info(f"Attempting to open image from {temp_path}")
        with Image.open(temp_path) as loaded_img:
            logger.info(f"Successfully opened image: format={loaded_img.format}, size={loaded_img.size}, mode={loaded_img.mode}")
            
            # Convert to base64 for testing
            img_byte_arr = io.BytesIO()
            loaded_img.save(img_byte_arr, format='PNG')
            encoded_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            logger.info(f"Successfully encoded image to base64, length: {len(encoded_data)}")
            
        # Clean up
        os.remove(temp_path)
        logger.info(f"Removed temporary file {temp_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in save_and_load_image: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting PIL test")
    logger.info(f"PIL version: {Image.__version__}")
    
    if save_and_load_image():
        logger.info("PIL test completed successfully")
    else:
        logger.error("PIL test failed") 