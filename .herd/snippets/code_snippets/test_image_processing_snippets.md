# Code Snippets from toollama/API/--storage/test_image_processing.py

File: `toollama/API/--storage/test_image_processing.py`  
Language: Python  
Extracted: 2025-06-07 05:16:42  

## Snippet 1
Lines 1-20

```Python
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
```

## Snippet 2
Lines 21-37

```Python
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
```

## Snippet 3
Lines 38-59

```Python
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
```

## Snippet 4
Lines 60-68

```Python
def test_anthropic_provider():
    """Test image processing in AnthropicProvider."""
    logger.info("Testing AnthropicProvider image processing")

    # Create a dummy provider with an empty API key
    provider = AnthropicProvider(api_key="dummy_key")

    # Create a test image
    temp_path = create_test_image()
```

## Snippet 5
Lines 69-77

```Python
if not temp_path:
        logger.error("Failed to create test image")
        return False

    try:
        # Test process_image
        logger.info(f"Testing process_image with {temp_path}")
        image_data = provider.process_image(temp_path)
```

## Snippet 6
Lines 85-88

```Python
if data_length > 0:
                        logger.info("AnthropicProvider process_image test passed")
                        return True
```

## Snippet 7
Lines 91-95

```Python
except Exception as e:
        logger.error(f"Error testing AnthropicProvider: {e}")
        return False
    finally:
        # Clean up
```

## Snippet 8
Lines 100-108

```Python
def test_mistral_provider():
    """Test image processing in MistralProvider."""
    logger.info("Testing MistralProvider image processing")

    # Create a dummy provider with an empty API key
    provider = MistralProvider(api_key="dummy_key")

    # Create a test image
    temp_path = create_test_image()
```

## Snippet 9
Lines 109-117

```Python
if not temp_path:
        logger.error("Failed to create test image")
        return False

    try:
        # Test process_image
        logger.info(f"Testing process_image with {temp_path}")
        encoded_image = provider.process_image(temp_path)
```

## Snippet 10
Lines 118-120

```Python
if encoded_image:
            logger.info(f"Successfully processed image: {type(encoded_image)}")
            logger.info(f"Encoded image length: {len(encoded_image)}")
```

## Snippet 11
Lines 121-124

```Python
if len(encoded_image) > 0:
                logger.info("MistralProvider process_image test passed")
                return True
```

## Snippet 12
Lines 127-131

```Python
except Exception as e:
        logger.error(f"Error testing MistralProvider: {e}")
        return False
    finally:
        # Clean up
```

## Snippet 13
Lines 142-147

```Python
if anthropic_result and mistral_result:
        logger.info("All provider image processing tests passed")
        sys.exit(0)
    else:
        logger.error("Some provider image processing tests failed")
        sys.exit(1)
```

