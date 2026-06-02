import sys
import os
import re

def patch_file():
    # Target the v1.26.0 file
    file_path = "svg_to_png_converter_v1_26_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Carefully extract and remove the Data URL UI from its current spot in the right controls
    v26_injection_regex = r'\s*<div style="display: flex; gap: 8px; align-items: center; flex-grow: 1; min-width: 300px; padding-left: 8px; border-left: 1px solid var\(--border-color\);">.*?id="btn-clear-live-data".*?</button>\s*</div>'
    
    content = re.sub(v26_injection_regex, '', content, flags=re.DOTALL | re.IGNORECASE)

    # Clean up the width: 100% that was added to the main controls container in v1.26.0
    content = re.sub(
        r'(<div[^>]*class="controls"[^>]*style="[^"]*)(\s*width:\s*100%;)([^"]*")', 
        r'\1\3', 
        content, 
        flags=re.IGNORECASE
    )

    # Hunk 2: Inject the Data URL UI at the bottom of the input-section (under the textarea)
    # This places it at the bottom-left on desktop, and exactly between input and preview on mobile!
    new_injection = r"""
                <div class="data-url-strip" style="margin-top: 16px; display: flex; flex-direction: column; gap: 8px;">
                    <label class="toggle-label" title="Wrap generated data URL in an HTML link tag">
                        <input type="checkbox" id="chk-wrap-link">
                        <span>Wrap in &lt;link rel="icon"&gt; tag</span>
                    </label>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG..." style="flex-grow: 1; min-width: 200px; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                        <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                        <button id="btn-clear-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap; background: var(--btn-clear-bg); color: var(--text-main); border: 1px solid var(--border-color); transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;" onmouseover="this.style.backgroundColor='var(--btn-clear-hover)'" onmouseout="this.style.backgroundColor='var(--btn-clear-bg)'">Clear</button>
                    </div>
                </div>"""

    # Ensure we successfully removed the old one before injecting the new one to prevent duplicates
    if 'id="live-data-url"' not in content:
        content = re.sub(
            r'(</textarea>)',
            r'\1' + new_injection,
            content,
            count=1,
            flags=re.IGNORECASE
        )
    else:
        print("Notice: It looks like the Data URL strip is still present elsewhere. Proceeding with fix anyway.")

    # Hunk 3: Version Bump
    if '<span class="version">v1.26.0</span>' in content:
        content = content.replace('<span class="version">v1.26.0</span>', '<span class="version">v1.27.0</span>')

    # Output to new version
    output_filename = "svg_to_png_converter_v1_27_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v1.27.0)!")

if __name__ == "__main__":
    patch_file()