# rclip-pdviewer

This is a minimal Flask web application that allows browsing and searching images
stored in the `./images` folder using the [rclip](https://github.com/yurijmikhalevich/rclip)
command line tool.

## Setup

Install dependencies (requires Python 3.10+ and access to PyTorch wheels):

```bash
pip install -r requirements.txt -f https://download.pytorch.org/whl/cpu
```

Place your images inside the `images` directory. On the first run rclip will index
all files in this folder which might take a while depending on the number of
images.

## Running

```bash
python app.py
```

Open `http://localhost:5000` in your browser and use the search field to query
images by description. Results are displayed with similarity scores.
