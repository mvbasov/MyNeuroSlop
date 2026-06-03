import sys
import os

def patch_file():
    # Target the v2.4.0 file
    file_path = "svg_to_png_converter_v2_4_0.html"
    
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
    search_logic = r"""                if (format === 'image/svg+xml') {
                    let svgString = svgInput.value.trim();
                    if (!svgString) return showStatus('No SVG to copy.', true);
                    let compact = svgString.replace(/\s+/g, ' ').trim();
                    const encoded = encodeURIComponent(compact).replace(/['()]/g, escape).replace(/\*/g, '%2A');
                    dataUrl = chkPrependPrefix.checked ? `data:image/svg+xml,${encoded}` : encoded;
                }"""
                    
    replace_logic = r"""                if (format === 'image/svg+xml') {
                    dataUrl = liveDataUrlInput.value.trim();
                    if (!dataUrl) return showStatus('No Data URL to copy.', true);
                }"""

    if search_logic in content:
        content = content.replace(search_logic, replace_logic)
    else:
        print("Notice: Existing copy logic not found exactly as expected. Please ensure you are targeting unaltered v2.4.0.")

    # Hunk 2: Global Version Bump
    if 'v2.4.0' in content:
        content = content.replace('v2.4.0', 'v2.5.0')

    # Output to new version
    output_filename = "svg_to_png_converter_v2_5_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v2.5.0)!")

if __name__ == "__main__":
    patch_file()