import sys
import os
import re

def patch_file():
    # Target the v2.5.0 file
    file_path = "svg_to_png_converter_v2_5_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Link the Copy button directly to the Live Data Input text
    # Using robust regex to bypass \r\n vs \n line-ending mismatches that caused v2.5.0 to fail silently
    regex_pattern = r"if\s*\(\s*format\s*===\s*'image/svg\+xml'\s*\)\s*\{[\s\S]*?dataUrl\s*=\s*chkPrependPrefix\.checked[\s\S]*?encoded;\s*\}"
    
    replace_logic = r"""if (format === 'image/svg+xml') {
                    dataUrl = liveDataUrlInput.value.trim();
                    if (!dataUrl) return showStatus('No Data URL to copy.', true);
                }"""

    if re.search(regex_pattern, content):
        content = re.sub(regex_pattern, replace_logic, content)
        print("Successfully patched the copy logic!")
    else:
        print("Notice: Existing copy logic not found. The script might have already been applied.")

    # Hunk 2: Global Version Bump
    if 'v2.5.0' in content:
        content = content.replace('v2.5.0', 'v2.6.0')

    # Output to new version
    output_filename = "svg_to_png_converter_v2_6_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v2.6.0)!")

if __name__ == "__main__":
    patch_file()