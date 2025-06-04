from flask import Flask, request, render_template, send_from_directory
from pathlib import Path
import rclip.main

# Directory containing images
IMAGE_DIR = Path("./images")

app = Flask(__name__)

# Initialise rclip when the app starts
rclip_instance, _model, _db = rclip.main.init_rclip(
    working_directory=str(IMAGE_DIR),
    indexing_batch_size=64,
    device="cpu",
)

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        # search images using rclip
        results = rclip_instance.search(query, str(IMAGE_DIR), top_k=20)
        # Convert absolute file paths to ones relative to IMAGE_DIR
        for r in results:
            rel_path = Path(r.filepath).relative_to(IMAGE_DIR)
            r.filepath = str(rel_path)
    return render_template('index.html', results=results, query=query)

@app.route('/images/<path:filename>')
def images(filename):
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
