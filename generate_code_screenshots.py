#!/usr/bin/env python3
"""
Automatic Code Screenshot Generator
Generates syntax-highlighted code screenshots from SCREENSHOT_PLACEMENT_GUIDE.md specifications

Usage:
    python generate_code_screenshots.py                    # Generate all screenshots
    python generate_code_screenshots.py --install-deps     # Install dependencies first
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import subprocess
import sys

class CodeScreenshotGenerator:
    def __init__(self, project_root: str = ".", output_dir: str = "screenshots/code"):
        self.project_root = Path(project_root).resolve()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.guide_path = self.project_root / "SCREENSHOT_PLACEMENT_GUIDE.md"
        
    def parse_guide(self) -> List[Dict]:
        """Parse SCREENSHOT_PLACEMENT_GUIDE.md and extract code screenshot specifications"""
        if not self.guide_path.exists():
            raise FileNotFoundError(f"Guide file not found: {self.guide_path}")
        
        with open(self.guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        screenshots = []
        
        # Split content into sections by "### Screenshot"
        sections = re.split(r'### Screenshot (\d+\.\d+):', content)
        
        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break
                
            figure_num = sections[i]
            section_content = sections[i + 1]
            
            # Check if it's a code screenshot
            if '**Type:** Code Screenshot' not in section_content:
                continue
            
            # Extract title (first line)
            title_match = re.match(r'^([^\n]+)', section_content)
            title = title_match.group(1).strip() if title_match else f"Screenshot {figure_num}"
            
            # Extract file path
            file_match = re.search(r'\*\*File:\*\* `([^`]+)`', section_content)
            if not file_match:
                print(f"  Warning: No file path found for {figure_num}")
                continue
            file_path = file_match.group(1).strip()
            
            # Extract line numbers
            lines_match = re.search(r'\*\*Lines:\*\* (\d+)(?:-(\d+))?', section_content)
            if not lines_match:
                print(f"  Warning: No line numbers found for {figure_num}")
                continue
            
            start_line = int(lines_match.group(1))
            end_line = int(lines_match.group(2)) if lines_match.group(2) else start_line
            
            # Extract caption
            caption_match = re.search(r'\*\*Caption:\*\* "([^"]+)"', section_content)
            caption = caption_match.group(1) if caption_match else title
            
            screenshots.append({
                'figure_num': figure_num,
                'title': title,
                'file_path': file_path,
                'start_line': start_line,
                'end_line': end_line,
                'caption': caption
            })
        
        return screenshots
    
    def read_code_lines(self, file_path: str, start_line: int, end_line: int) -> Tuple[str, str]:
        """Read specified lines from a code file"""
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            print(f"  Warning: File not found: {full_path}")
            return None, None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"  Error reading file {full_path}: {e}")
            return None, None
        
        # Adjust for 0-based indexing
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        if start_idx >= len(lines):
            print(f"  Warning: Start line {start_line} exceeds file length ({len(lines)} lines)")
            return None, None
        
        code_lines = lines[start_idx:end_idx]
        code = ''.join(code_lines)
        
        # Detect language from file extension
        ext = full_path.suffix.lower()
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
            '.sh': 'bash'
        }
        language = lang_map.get(ext, 'python')
        
        return code, language
    
    def generate_html_with_pygments(self, code: str, language: str, start_line: int) -> str:
        """Generate HTML with syntax highlighting using pygments"""
        try:
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name
            from pygments.formatters import HtmlFormatter
            
            lexer = get_lexer_by_name(language)
            formatter = HtmlFormatter(
                style='monokai',
                linenos=True,
                linenostart=start_line,
                cssclass='code-highlight',
                lineanchors='line',
                anchorlinenos=True,
                linespans='line'
            )
            
            html_code = highlight(code, lexer, formatter)
            css_styles = formatter.get_style_defs('.code-highlight')
            
            # Create complete HTML document
            html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background-color: #272822;
            padding: 30px;
            font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        {css_styles}
        .code-highlight {{
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            overflow: visible;
            max-width: 100%;
        }}
        .code-highlight pre {{
            margin: 0;
            background: transparent !important;
        }}
        .code-highlight table {{
            border-spacing: 0;
            width: 100%;
        }}
        .code-highlight td {{
            padding: 2px 10px;
            vertical-align: top;
        }}
        .code-highlight .linenos {{
            color: #75715e;
            background-color: #272822;
            padding-right: 15px;
            text-align: right;
            user-select: none;
            border-right: 1px solid #3e3d32;
        }}
    </style>
</head>
<body>
    {html_code}
</body>
</html>
"""
            return html_doc
            
        except ImportError:
            print("  Error: pygments not installed. Install with: pip install pygments")
            return None
        except Exception as e:
            print(f"  Error generating HTML: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def html_to_image_html2image(self, html_content: str, output_path: Path, height: int = 800) -> bool:
        """Convert HTML to image using html2image"""
        try:
            from html2image import Html2Image
            import platform
            
            # Save temporary HTML file
            temp_html = self.output_dir / f"temp_{output_path.stem}.html"
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Try to find Chrome on macOS
            chrome_paths = []
            if platform.system() == 'Darwin':  # macOS
                chrome_paths = [
                    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                    '/Applications/Chromium.app/Contents/MacOS/Chromium',
                    '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
                ]
            
            hti = Html2Image(size=(1400, height))
            
            # Try to set Chrome path if on macOS
            for chrome_path in chrome_paths:
                if Path(chrome_path).exists():
                    hti.browser_executable = chrome_path
                    break
            
            # Convert HTML to image
            hti.screenshot(
                html_file=str(temp_html),
                save_as=str(output_path.name),
                size=(1400, height)
            )
            
            # Move file to correct location if needed
            temp_img = Path(output_path.name)
            if temp_img.exists() and not output_path.exists():
                temp_img.rename(output_path)
            
            # Cleanup
            if temp_html.exists():
                temp_html.unlink()
            if temp_img.exists() and temp_img != output_path:
                temp_img.unlink()
            
            return output_path.exists()
            
        except ImportError:
            return False
        except Exception as e:
            print(f"  Error with html2image: {e}")
            # Try to provide helpful error message
            if "Chrome" in str(e) or "chromium" in str(e).lower():
                print(f"  Hint: Chrome/Chromium not found. Install Chrome or use playwright method.")
            return False
    
    def html_to_image_playwright(self, html_content: str, output_path: Path, height: int = 800) -> bool:
        """Convert HTML to image using playwright (alternative method)"""
        try:
            from playwright.sync_api import sync_playwright
            
            # Save temporary HTML file
            temp_html = self.output_dir / f"temp_{output_path.stem}.html"
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(f"file://{temp_html.absolute()}")
                page.screenshot(path=str(output_path), full_page=True)
                browser.close()
            
            # Cleanup
            if temp_html.exists():
                temp_html.unlink()
            
            return output_path.exists()
            
        except ImportError:
            return False
        except Exception as e:
            print(f"  Error with playwright: {e}")
            return False
    
    def generate_screenshot_pil(self, code: str, language: str, output_path: Path,
                                 figure_num: str, start_line: int) -> bool:
        """Generate screenshot using PIL directly (fallback method)"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name
            from pygments.formatters import Terminal256Formatter
            
            lexer = get_lexer_by_name(language)
            formatter = Terminal256Formatter(style='monokai')
            
            # Get highlighted code as ANSI text
            highlighted = highlight(code, lexer, formatter)
            
            # Parse ANSI codes and render
            lines = code.split('\n')
            num_lines = len(lines)
            max_line_len = max(len(line) for line in lines) if lines else 80
            
            # Font settings
            try:
                # Try to use a monospace font
                font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
                small_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
            except:
                try:
                    font = ImageFont.truetype("/Library/Fonts/Courier New.ttf", 14)
                    small_font = ImageFont.truetype("/Library/Fonts/Courier New.ttf", 12)
                except:
                    font = ImageFont.load_default()
                    small_font = ImageFont.load_default()
            
            char_width = 8
            line_height = 20
            padding = 25
            line_num_width = 60
            
            width = min(1400, (max_line_len * char_width) + line_num_width + (padding * 2))
            height = (num_lines * line_height) + (padding * 2)
            
            # Create image with dark background
            img = Image.new('RGB', (width, height), color='#272822')
            draw = ImageDraw.Draw(img)
            
            # Color scheme (Monokai-like)
            colors = {
                'default': '#f8f8f2',
                'keyword': '#f92672',
                'string': '#e6db74',
                'comment': '#75715e',
                'number': '#ae81ff',
                'function': '#66d9ef',
                'line_num': '#75715e',
            }
            
            y = padding
            line_num = start_line
            
            for line in lines:
                # Draw line number
                draw.text((padding, y), f"{line_num:4d}", fill=colors['line_num'], font=small_font)
                
                # Draw code line (simplified - basic syntax highlighting)
                x = padding + line_num_width + 10
                
                # Simple keyword highlighting
                if language == 'python':
                    keywords = ['def', 'class', 'import', 'from', 'if', 'elif', 'else', 'for', 'while', 
                               'return', 'async', 'await', 'try', 'except', 'with', 'as']
                    words = line.split()
                    current_x = x
                    for word in words:
                        clean_word = word.strip('.,()[]{}:;')
                        if clean_word in keywords:
                            draw.text((current_x, y), word, fill=colors['keyword'], font=font)
                        elif word.startswith('"') or word.startswith("'") or word.startswith('`'):
                            draw.text((current_x, y), word, fill=colors['string'], font=font)
                        elif word.startswith('#'):
                            draw.text((current_x, y), word, fill=colors['comment'], font=font)
                        else:
                            draw.text((current_x, y), word, fill=colors['default'], font=font)
                        # Approximate width
                        current_x += len(word) * char_width + char_width
                else:
                    draw.text((x, y), line, fill=colors['default'], font=font)
                
                y += line_height
                line_num += 1
            
            # Save image
            img.save(output_path, 'PNG', quality=95)
            return True
            
        except Exception as e:
            print(f"  Error with PIL method: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_screenshot(self, spec: Dict) -> bool:
        """Generate a single code screenshot"""
        # Read code
        code, language = self.read_code_lines(
            spec['file_path'],
            spec['start_line'],
            spec['end_line']
        )
        
        if code is None:
            return False
        
        # Generate output filename
        safe_title = re.sub(r'[^\w\s-]', '', spec['title']).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        output_filename = f"fig-{spec['figure_num']}-{safe_title[:50]}.png"
        output_path = self.output_dir / output_filename
        
        # Try different methods to generate screenshot
        success = False
        
        # Method 1: html2image (best quality, requires Chrome)
        if not success:
            html_content = self.generate_html_with_pygments(code, language, spec['start_line'])
            if html_content:
                line_count = len(code.split('\n'))
                height = max(600, line_count * 24 + 150)
                success = self.html_to_image_html2image(html_content, output_path, height)
                if success:
                    print(f"    ✓ Used html2image")
        
        # Method 2: playwright (alternative, requires Chrome)
        if not success:
            html_content = self.generate_html_with_pygments(code, language, spec['start_line'])
            if html_content:
                line_count = len(code.split('\n'))
                height = max(600, line_count * 24 + 150)
                success = self.html_to_image_playwright(html_content, output_path, height)
                if success:
                    print(f"    ✓ Used playwright")
        
        # Method 3: PIL direct rendering (fallback, no Chrome needed)
        if not success:
            success = self.generate_screenshot_pil(code, language, output_path, spec['figure_num'], spec['start_line'])
            if success:
                print(f"    ✓ Used PIL (basic rendering)")
        
        if success:
            print(f"    Saved: {output_path}")
            return True
        else:
            print(f"    ✗ Failed: Could not generate screenshot")
            return False
    
    def generate_all_screenshots(self):
        """Generate all code screenshots from the guide"""
        screenshots = self.parse_guide()
        
        if not screenshots:
            print("No code screenshots found in guide!")
            return 0, 0
        
        print(f"Found {len(screenshots)} code screenshots to generate\n")
        
        success_count = 0
        failed = []
        
        for i, spec in enumerate(screenshots, 1):
            print(f"[{i}/{len(screenshots)}] {spec['figure_num']}: {spec['title']}")
            print(f"    File: {spec['file_path']} (lines {spec['start_line']}-{spec['end_line']})")
            
            success = self.generate_screenshot(spec)
            
            if success:
                success_count += 1
            else:
                failed.append(spec['figure_num'])
            
            print()  # Empty line for readability
        
        print(f"{'='*60}")
        print(f"Summary: {success_count}/{len(screenshots)} screenshots generated")
        if failed:
            print(f"Failed: {', '.join(failed)}")
        print(f"Output directory: {self.output_dir.absolute()}")
        
        return success_count, len(screenshots)

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import pygments
    except ImportError:
        missing.append("pygments")
    
    try:
        from html2image import Html2Image
    except ImportError:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            missing.append("html2image OR playwright")
    
    return missing

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    packages = ['pygments']
    
    # Try to install html2image first, then playwright as fallback
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 'html2image', '--quiet'
        ])
        print("  ✓ Installed html2image")
    except:
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 'playwright', '--quiet'
            ])
            subprocess.check_call([
                sys.executable, '-m', 'playwright', 'install', 'chromium', '--quiet'
            ])
            print("  ✓ Installed playwright")
        except:
            print("  ⚠ Could not install html2image or playwright")
            print("  You may need to install manually: pip install html2image")
    
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install'] + packages + ['--quiet'
    ])
    print("  ✓ Installed pygments")
    print("\nDependencies installed!")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate code screenshots from SCREENSHOT_PLACEMENT_GUIDE.md',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install dependencies first
  python generate_code_screenshots.py --install-deps
  
  # Generate all screenshots
  python generate_code_screenshots.py
  
  # Custom output directory
  python generate_code_screenshots.py --output-dir my_screenshots
        """
    )
    parser.add_argument(
        '--project-root',
        type=str,
        default='.',
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='screenshots/code',
        help='Output directory for screenshots (default: screenshots/code)'
    )
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install required dependencies (pygments, html2image/playwright)'
    )
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check if dependencies are installed'
    )
    
    args = parser.parse_args()
    
    if args.install_deps:
        install_dependencies()
        return
    
    if args.check_deps:
        missing = check_dependencies()
        if missing:
            print(f"Missing dependencies: {', '.join(missing)}")
            print("Install with: python generate_code_screenshots.py --install-deps")
            sys.exit(1)
        else:
            print("All dependencies are installed!")
            return
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Warning: Missing dependencies: {', '.join(missing)}")
        print("Run with --install-deps to install them")
        print("Continuing anyway...\n")
    
    generator = CodeScreenshotGenerator(
        project_root=args.project_root,
        output_dir=args.output_dir
    )
    
    try:
        success, total = generator.generate_all_screenshots()
        sys.exit(0 if success == total else 1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
