import sys
import os

def patch_file():
    # Target the v1.29.0 file
    file_path = "svg_to_png_converter_v1_29_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Version Bump
    search1 = r"""<span class="version">v1.29.0</span>"""
    replace1 = r"""<span class="version">v1.30.0</span>"""

    # Apply patches
    if search1 in content:
        content = content.replace(search1, replace1)

        output_filename = "svg_to_png_converter_v1_30_0.html"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_filename} (v1.30.0)!")
    else:
        print("Error: Could not find target strings to replace. Ensure you are targeting the unaltered v1.29.0 file.")

if __name__ == "__main__":
    patch_file()