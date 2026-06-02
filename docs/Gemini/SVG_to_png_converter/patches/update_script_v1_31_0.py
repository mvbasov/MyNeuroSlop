import sys
import os
import re

def patch_file():
    # Target the v1.30.0 file
    file_path = "svg_to_png_converter_v1_30_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Move Version Badge to Header
    # Wrap the h1 tag in a flex container and inject the version span next to it
    if 'v1.31.0' not in content:
        header_regex = r'(<h1>.*?</h1>)'
        header_replacement = r'''<div style="display: flex; align-items: center; gap: 12px;">
                    \1
                    <span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px;">v1.31.0</span>
                </div>'''
        content = re.sub(header_regex, header_replacement, content, count=1)

    # Hunk 2: Remove the "Runs completely offline" sign and old version footer
    footer_regex = r'\s*<div class="app-footer">.*?</div>'
    content = re.sub(footer_regex, '', content, flags=re.DOTALL)

    # Hunk 3: Update Labels
    content = content.replace('<span>Wrap 80x80</span>', '<span>Wrap 80 chars</span>')
    content = content.replace('<span>Prefix</span>', "<span>Include 'data:...' Prefix</span>")
    
    # Sweep any residual v1.30.0 strings
    content = content.replace('v1.30.0', 'v1.31.0')

    # Output to new version
    output_filename = "svg_to_png_converter_v1_31_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v1.31.0)!")

if __name__ == "__main__":
    patch_file()