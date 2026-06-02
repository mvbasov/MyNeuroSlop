import sys
import os

def patch_file():
    # Target the v1.33.0 file
    file_path = "svg_to_png_converter_v1_33_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Global Version Bump
    # This safely replaces the version text in the header badge
    if 'v1.33.0' in content:
        content = content.replace('v1.33.0', 'v2.0.0')
    else:
        print("Notice: 'v1.33.0' string not found. Ensure you are targeting the correct file.")

    # Output to new version
    output_filename = "svg_to_png_converter_v2_0_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v2.0.0)!")

if __name__ == "__main__":
    patch_file()