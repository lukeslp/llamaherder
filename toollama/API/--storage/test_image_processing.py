#!/usr/bin/env python
"""
Test script to verify image processing in provider classes.
This script tests the image processing functions in both Anthropic and Mistral providers.
"""

import os
import io
import base64
import tempfile
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow importing API modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import PIL for creating test images
try:
    from PIL import Image, ImageDraw
    logger.info("Successfully imported PIL modules")
except ImportError as e:
    logger.error(f"Failed to import PIL: {e}")
    exit(1)

# Import provider classes
try:
    from api.services.providers.anthropic import AnthropicProvider
    from api.services.providers.mistral import MistralProvider
    logger.info("Successfully imported provider classes")
except ImportError as e:
    logger.error(f"Failed to import provider classes: {e}")
    exit(1)

def create_test_image():
    """Create a test image and save it to a temporary file."""
    try:
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 90, 90], fill='blue', outline='white')
        draw.text((25, 40), "Test", fill='white')
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_path = temp_file.name
        temp_file.close()
        
        logger.info(f"Saving test image to {temp_path}")
        img.save(temp_path)
        
        return temp_path
    except Exception as e:
        logger.error(f"Error creating test image: {e}")
        return None

def test_anthropic_provider():
    """Test image processing in AnthropicProvider."""
    logger.info("Testing AnthropicProvider image processing")
    
    # Create a dummy provider with an empty API key
    provider = AnthropicProvider(api_key="dummy_key")
    
    # Create a test image
    temp_path = create_test_image()
    if not temp_path:
        logger.error("Failed to create test image")
        return False
    
    try:
        # Test process_image
        logger.info(f"Testing process_image with {temp_path}")
        image_data = provider.process_image(temp_path)
        
        if image_data:
            logger.info(f"Successfully processed image: {type(image_data)}")
            if isinstance(image_data, dict):
                logger.info(f"Image data keys: {image_data.keys()}")
                if 'source' in image_data and 'data' in image_data['source']:
                    data_length = len(image_data['source']['data'])
                    logger.info(f"Image data length: {data_length}")
                    if data_length > 0:
                        logger.info("AnthropicProvider process_image test passed")
                        return True
        
        logger.error("AnthropicProvider process_image test failed")
        return False
    except Exception as e:
        logger.error(f"Error testing AnthropicProvider: {e}")
        return False
    finally:
        # Clean up
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Removed temporary file {temp_path}")

def test_mistral_provider():
    """Test image processing in MistralProvider."""
    logger.info("Testing MistralProvider image processing")
    
    # Create a dummy provider with an empty API key
    provider = MistralProvider(api_key="dummy_key")
    
    # Create a test image
    temp_path = create_test_image()
    if not temp_path:
        logger.error("Failed to create test image")
        return False
    
    try:
        # Test process_image
        logger.info(f"Testing process_image with {temp_path}")
        encoded_image = provider.process_image(temp_path)
        
        if encoded_image:
            logger.info(f"Successfully processed image: {type(encoded_image)}")
            logger.info(f"Encoded image length: {len(encoded_image)}")
            if len(encoded_image) > 0:
                logger.info("MistralProvider process_image test passed")
                return True
        
        logger.error("MistralProvider process_image test failed")
        return False
    except Exception as e:
        logger.error(f"Error testing MistralProvider: {e}")
        return False
    finally:
        # Clean up
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Removed temporary file {temp_path}")

if __name__ == "__main__":
    logger.info("Starting provider image processing tests")
    
    anthropic_result = test_anthropic_provider()
    mistral_result = test_mistral_provider()
    
    if anthropic_result and mistral_result:
        logger.info("All provider image processing tests passed")
        sys.exit(0)
    else:
        logger.error("Some provider image processing tests failed")
        sys.exit(1) 