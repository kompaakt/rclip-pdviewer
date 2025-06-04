#!/usr/bin/env python3

import os
import json
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

IMAGES_DIR = "./images"
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

def get_image_files():
    """Get list of all image files in the images directory"""
    image_files = []
    images_path = Path(IMAGES_DIR)
    
    if not images_path.exists():
        return []
    
    for file_path in images_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            image_files.append(file_path.name)
    
    return sorted(image_files)

def run_rclip_search(query, top_k=50, is_image_query=False):
    """Run rclip search and return results"""
    try:
        # Run rclip command - change to images directory and run search
        if is_image_query:
            # For image-based search, prefix the filename with ./ as required by rclip
            image_query = f"./{query}"
            cmd = ['rclip', '--top', str(top_k), '--filepath-only', image_query]
        else:
            # For text-based search
            cmd = ['rclip', '--top', str(top_k), '--filepath-only', query]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=IMAGES_DIR)
        
        # Parse the output - with --filepath-only, we get just file paths
        lines = result.stdout.strip().split('\n')
        results = []
        
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('checking images') and 'images/s' not in line:
                # Since we use --filepath-only, each line is a filepath
                # Extract just the filename from the full path
                filename = os.path.basename(line.strip())
                score = 1.0 - (i / len(lines))  # Score from 1.0 to close to 0
                results.append({'filename': filename, 'score': score})
        
        return results
        
    except subprocess.CalledProcessError as e:
        print(f"rclip command failed: {e}")
        print(f"stderr: {e.stderr}")
        return []
    except Exception as e:
        print(f"Error running rclip: {e}")
        return []

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_file('index.html')

@app.route('/api/images')
def list_images():
    """Get list of all images"""
    try:
        image_files = get_image_files()
        images = [{'filename': img} for img in image_files]
        return jsonify({'images': images})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_images():
    """Search images using rclip"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Check if rclip is available
        try:
            subprocess.run(['rclip', '--help'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return jsonify({'error': 'rclip is not installed or not available in PATH'}), 500
        
        # Check if images directory exists
        if not os.path.exists(IMAGES_DIR):
            return jsonify({'error': f'Images directory {IMAGES_DIR} does not exist'}), 500
        
        # Get search results
        results = run_rclip_search(query)
        
        # Filter results to only include existing files
        image_files = set(get_image_files())
        filtered_results = [
            result for result in results 
            if result.get('filename') in image_files
        ]
        
        return jsonify({'images': filtered_results, 'query': query})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/similar', methods=['POST'])
def search_similar_images():
    """Search for images similar to a given image"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({'error': 'Filename is required'}), 400
        
        filename = data['filename'].strip()
        if not filename:
            return jsonify({'error': 'Filename cannot be empty'}), 400
        
        # Security check - ensure filename is just a filename, not a path
        if '/' in filename or '\\' in filename or '..' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        # Check if the image file exists
        image_path = Path(IMAGES_DIR) / filename
        if not image_path.exists():
            return jsonify({'error': 'Image not found'}), 404
        
        # Check if rclip is available
        try:
            subprocess.run(['rclip', '--help'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return jsonify({'error': 'rclip is not installed or not available in PATH'}), 500
        
        # Check if images directory exists
        if not os.path.exists(IMAGES_DIR):
            return jsonify({'error': f'Images directory {IMAGES_DIR} does not exist'}), 500
        
        # Get search results using the image as query
        results = run_rclip_search(filename, is_image_query=True)
        
        # Filter results to only include existing files and exclude the query image itself
        image_files = set(get_image_files())
        filtered_results = [
            result for result in results 
            if result.get('filename') in image_files and result.get('filename') != filename
        ]
        
        return jsonify({'images': filtered_results, 'query_image': filename})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<path:filename>')
def serve_image(filename):
    """Serve individual image files"""
    try:
        # Security check - ensure filename is just a filename, not a path
        if '/' in filename or '\\' in filename or '..' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        image_path = Path(IMAGES_DIR) / filename
        
        if not image_path.exists():
            return jsonify({'error': 'Image not found'}), 404
        
        if not image_path.is_file():
            return jsonify({'error': 'Not a file'}), 400
        
        return send_from_directory(IMAGES_DIR, filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'images_dir': IMAGES_DIR})

if __name__ == '__main__':
    # Create images directory if it doesn't exist
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    print(f"Starting server...")
    print(f"Images directory: {os.path.abspath(IMAGES_DIR)}")
    print(f"Available images: {len(get_image_files())}")
    
    app.run(host='0.0.0.0', port=8000, debug=True)