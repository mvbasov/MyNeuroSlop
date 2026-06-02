import sys
import os
import re

def patch_file():
    # Target the version where the injection failed
    file_path = "svg_to_png_converter_v1_25_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # The exact injection string for the Data URL UI
    injection = r"""
                <div style="display: flex; gap: 8px; align-items: center; flex-grow: 1; min-width: 300px; padding-left: 8px; border-left: 1px solid var(--border-color);">
                    <label class="toggle-label" title="Wrap generated data URL in an HTML link tag" style="white-space: nowrap;">
                        <input type="checkbox" id="chk-wrap-link">
                        <span>Wrap &lt;link&gt;</span>
                    </label>
                    <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG..." style="flex-grow: 1; min-width: 100px; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                    <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                    <button id="btn-clear-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap; background: var(--btn-clear-bg); color: var(--text-main); border: 1px solid var(--border-color); transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;" onmouseover="this.style.backgroundColor='var(--btn-clear-hover)'" onmouseout="this.style.backgroundColor='var(--btn-clear-bg)'">Clear</button>
                </div>"""
        
    # Hunk 1: Robustly inject the Data UI immediately after the btn-download using regex
    # This ignores strict indentation and just looks for the HTML tag natively.
    if 'id="live-data-url"' not in content:
        content = re.sub(
            r'(<button[^>]*id="btn-download"[^>]*>.*?</button>)',
            r'\1' + injection,
            content,
            flags=re.IGNORECASE | re.DOTALL,
            count=1
        )
    else:
        print("Notice: Data URL strip seems to already exist in the file. Proceeding with fix anyway.")
    
    # Hunk 2: Make sure the controls container is full width to accommodate the layout flex
    # Regex ensures we add width: 100% even if the tag formatting is unique
    if 'class="controls"' in content:
        def add_width_100(match):
            style_content = match.group(2)
            if 'width: 100%' not in style_content:
                style_content = style_content.strip()
                if style_content and not style_content.endswith(';'):
                    style_content += ';'
                style_content += ' width: 100%;'
            return match.group(1) + style_content + match.group(3)
            
        content = re.sub(
            r'(<div[^>]*class="controls"[^>]*style=")([^"]*)(")',
            add_width_100,
            content,
            flags=re.IGNORECASE
        )

    # Hunk 3: Version Bump
    if '<span class="version">v1.25.0</span>' in content:
        content = content.replace('<span class="version">v1.25.0</span>', '<span class="version">v1.26.0</span>')

    # Output to new version
    output_filename = "svg_to_png_converter_v1_26_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v1.26.0)!")

if __name__ == "__main__":
    patch_file()