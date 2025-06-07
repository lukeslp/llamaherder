#!/bin/bash

# Run Camina Chat API with Flask
# This script sets up the necessary environment and runs the Flask application

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
fi

# Set Flask environment variables
export FLASK_APP=api.app
export FLASK_ENV=development
export FLASK_DEBUG=1

echo "Starting Camina Chat API server on port 8435..."
python -m flask run --host=0.0.0.0 --port=8435 