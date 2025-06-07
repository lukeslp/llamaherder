#!/usr/bin/env python3
"""
Convert Swagger YAML to JSON
This script converts the swagger.yaml file to swagger.json in the API's static directory.
"""

from ruamel.yaml import YAML
import json
import os
from pathlib import Path

def convert_yaml_to_json():
    """Convert the Swagger YAML file to JSON format."""
    try:
        # Define paths
        yaml_path = Path('api/static/swagger/swagger.yaml')
        json_path = Path('api/static/swagger/swagger.json')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
        
        # Read YAML file
        yaml = YAML(typ='safe')
        with open(yaml_path, 'r') as yaml_file:
            yaml_data = yaml.load(yaml_file)
        
        # Write JSON file
        with open(json_path, 'w') as json_file:
            json.dump(yaml_data, json_file, indent=2)
        
        print(f"Successfully converted {yaml_path} to {json_path}")
        return True
    except Exception as e:
        print(f"Error converting YAML to JSON: {e}")
        return False

if __name__ == "__main__":
    convert_yaml_to_json() 