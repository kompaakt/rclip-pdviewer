#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install rclip
echo "Installing rclip..."
pip install rclip

# Create images directory if it doesn't exist
mkdir -p images

# Start the server
echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
python server.py