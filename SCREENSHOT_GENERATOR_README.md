# Code Screenshot Generator

Automatically generates syntax-highlighted code screenshots from `SCREENSHOT_PLACEMENT_GUIDE.md`.

## Quick Start

### 1. Install Dependencies

```bash
python generate_code_screenshots.py --install-deps
```

This will install:
- `pygments` - Syntax highlighting
- `html2image` or `playwright` - HTML to image conversion

### 2. Generate All Screenshots

```bash
python generate_code_screenshots.py
```

Screenshots will be saved to `screenshots/code/` directory.

## Usage

```bash
# Check if dependencies are installed
python generate_code_screenshots.py --check-deps

# Install dependencies
python generate_code_screenshots.py --install-deps

# Generate screenshots (default output: screenshots/code/)
python generate_code_screenshots.py

# Custom output directory
python generate_code_screenshots.py --output-dir my_screenshots

# Custom project root
python generate_code_screenshots.py --project-root /path/to/project
```

## How It Works

1. **Parses** `SCREENSHOT_PLACEMENT_GUIDE.md` to extract code screenshot specifications
2. **Reads** the specified code files and line ranges
3. **Generates** syntax-highlighted HTML using Pygments
4. **Converts** HTML to PNG images using html2image or playwright
5. **Saves** screenshots with naming: `fig-X.Y-title.png`

## Output

Screenshots are saved as:
- `fig-5.2-fastapi-application-setup.png`
- `fig-6.2-livenessdetector-class-initialization.png`
- etc.

Each screenshot includes:
- Syntax highlighting (Monokai theme)
- Line numbers
- Proper formatting
- Dark background (#272822)

## Requirements

- Python 3.7+
- pygments
- html2image OR playwright

## Troubleshooting

### "No HTML-to-image converter available"
Install one of:
```bash
pip install html2image
# OR
pip install playwright
playwright install chromium
```

### "File not found" errors
Make sure you're running the script from the project root directory, or use `--project-root` to specify the correct path.

### "Pygments not installed"
```bash
pip install pygments
```

## Manual Installation

If automatic installation doesn't work:

```bash
pip install pygments html2image pillow
# OR
pip install pygments playwright pillow
playwright install chromium
```

## Notes

- The script only generates **code screenshots** (not UI screenshots)
- UI screenshots must be taken manually from the browser/kiosk
- Code screenshots use the Monokai color scheme
- Line numbers start from the specified start_line in the guide

