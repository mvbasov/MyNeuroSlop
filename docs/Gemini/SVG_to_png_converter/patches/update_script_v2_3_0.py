import sys
import os
import re

def patch_file():
    # Target the v2.2.0 file
    file_path = "svg_to_png_converter_v2_2_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Relocate the Checkbox UI
    # First, safely rip it out of its original position
    content = re.sub(
        r'\s*<label class="toggle-label"[^>]*>\s*<input type="checkbox" id="chk-wrap-80"[^>]*>\s*<span>Wrap 80 chars</span>\s*</label>',
        '',
        content,
        flags=re.IGNORECASE
    )

    # Next, inject it directly after the "Copy Base64" button
    content = re.sub(
        r'(<button id="btn-copy-base64">.*?</button>)',
        r'\1\n                <label class="toggle-label" title="Wrap output with newlines every 80 characters">\n                    <input type="checkbox" id="chk-wrap-80">\n                    <span>Wrap 80 chars</span>\n                </label>',
        content,
        flags=re.IGNORECASE
    )

    # Hunk 2: Remove the 80x80 scaling logic from canvas sizing
    dim_regex = r'\s*// Apply optional 80x80 wrapping\s*if \(chkWrap80\.checked\) \{[\s\S]*?canvas\.height = 80;\s*\} else \{\s*(canvas\.width = parsedWidth;\s*canvas\.height = parsedHeight;)\s*\}'
    content = re.sub(dim_regex, r'\n                \1', content)

    # Hunk 3: Remove the 80x80 drawing logic from the canvas painting engine
    draw_regex = r'\s*if \(chkWrap80\.checked\) \{[\s\S]*?ctx\.drawImage\(img, offsetX, offsetY, drawWidth, drawHeight\);\s*\} else \{\s*(ctx\.drawImage\(img, 0, 0, canvas\.width, canvas\.height\);)\s*\}'
    content = re.sub(draw_regex, r'\n                    \1', content)

    # Hunk 4: Remove the old event listener that caused the canvas to re-render
    listener_regex = r'\s*// 1\. Checkbox formatting options trigger re-render\s*chkWrap80\.addEventListener\(\'change\', \(\) => \{[\s\S]*?\}\);'
    content = re.sub(listener_regex, '', content)

    # Hunk 5: Inject the 80-character line break logic into the Copy function
    wrap_logic_regex = r'(\s*// If raw string gets incredibly large[^\n]*\n\s*)if \(dataUrl\.length > 2000000\) \{'
    wrap_logic_replacement = r'''
                // Apply 80-character line wrapping if checked
                if (chkWrap80.checked) {
                    const chunks = [];
                    for (let i = 0; i < dataUrl.length; i += 80) {
                        chunks.push(dataUrl.substring(i, i + 80));
                    }
                    dataUrl = chunks.join('\n');
                } else if (dataUrl.length > 2000000) {'''
    content = re.sub(wrap_logic_regex, wrap_logic_replacement, content)

    # Hunk 6: Global Version Bump
    if 'v2.2.0' in content:
        content = content.replace('v2.2.0', 'v2.3.0')

    # Output to new version
    output_filename = "svg_to_png_converter_v2_3_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v2.3.0)!")

if __name__ == "__main__":
    patch_file()