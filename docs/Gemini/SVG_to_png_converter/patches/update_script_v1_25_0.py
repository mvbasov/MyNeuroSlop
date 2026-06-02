import sys
import os

def patch_file():
    # Smart file detection: checks if you reverted to 23 or kept 24
    target_files = ["svg_to_png_converter_v1_24_0.html", "svg_to_png_converter_v1_23_0.html"]
    file_path = None
    
    for f in target_files:
        if os.path.exists(f):
            file_path = f
            break
            
    if not file_path:
        print("Error: Could not find v1.23.0 or v1.24.0 file to patch.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Clean up the old Data URL Strip (Handles both v23 and v24 positions)
    search_v23_strip = r"""                <div class="data-url-strip" style="margin-top: 16px; display: flex; flex-direction: column; gap: 8px;">
                    <label class="toggle-label" title="Wrap generated data URL in an HTML link tag">
                        <input type="checkbox" id="chk-wrap-link">
                        <span>Wrap in &lt;link rel="icon"&gt; tag</span>
                    </label>
                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG..." style="flex-grow: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                        <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                        <button id="btn-clear-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap; background: var(--btn-clear-bg); color: var(--text-main); border: 1px solid var(--border-color); transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;" onmouseover="this.style.backgroundColor='var(--btn-clear-hover)'" onmouseout="this.style.backgroundColor='var(--btn-clear-bg)'">Clear</button>
                    </div>
                </div>"""

    search_v24_strip = r"""            <div class="data-url-strip" style="display: flex; flex-direction: column; gap: 8px; width: 100%;">
                <label class="toggle-label" title="Wrap generated data URL in an HTML link tag">
                    <input type="checkbox" id="chk-wrap-link">
                    <span>Wrap in &lt;link rel="icon"&gt; tag</span>
                </label>
                <div style="display: flex; gap: 8px;">
                    <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG..." style="flex-grow: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                    <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                    <button id="btn-clear-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap; background: var(--btn-clear-bg); color: var(--text-main); border: 1px solid var(--border-color); transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;" onmouseover="this.style.backgroundColor='var(--btn-clear-hover)'" onmouseout="this.style.backgroundColor='var(--btn-clear-bg)'">Clear</button>
                </div>
            </div>"""

    if search_v23_strip in content:
        content = content.replace(search_v23_strip, "")
    if search_v24_strip in content:
        content = content.replace(search_v24_strip, "")

    # Clean up v24 specific CSS if present
    search_v24_css1 = r"""            #svg-to-png-app .main-content {
                flex-direction: row;
                align-items: stretch;
                flex-wrap: wrap;
            }"""
    replace_v24_css1 = r"""            #svg-to-png-app .main-content {
                flex-direction: row;
                align-items: stretch;
            }"""
    if search_v24_css1 in content:
        content = content.replace(search_v24_css1, replace_v24_css1)

    search_v24_css2 = r"""            #svg-to-png-app .data-url-strip {
                flex: 0 0 100%;
                order: 3;
            }"""
    if search_v24_css2 in content:
        content = content.replace(search_v24_css2, "")

    # Hunk 2: Make the controls container 100% wide so it can absorb the layout
    search_controls = r"""<div class="controls" style="display: flex; gap: 8px; align-items: center; justify-content: center; margin-top: 16px; flex-wrap: wrap;">"""
    replace_controls = r"""<div class="controls" style="display: flex; gap: 8px; align-items: center; justify-content: center; margin-top: 16px; flex-wrap: wrap; width: 100%;">"""
    if search_controls in content:
        content = content.replace(search_controls, replace_controls)

    # Hunk 3: Inject the Data URL tools directly onto the same line as Save PNG
    search_append = r"""                <button id="btn-download">Save PNG</button>
            </div>"""
            
    replace_append = r"""                <button id="btn-download">Save PNG</button>
                <div style="display: flex; gap: 8px; align-items: center; flex-grow: 1; min-width: 300px; padding-left: 8px; border-left: 1px solid var(--border-color);">
                    <label class="toggle-label" title="Wrap generated data URL in an HTML link tag" style="white-space: nowrap;">
                        <input type="checkbox" id="chk-wrap-link">
                        <span>Wrap &lt;link&gt;</span>
                    </label>
                    <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG..." style="flex-grow: 1; min-width: 100px; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                    <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                    <button id="btn-clear-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap; background: var(--btn-clear-bg); color: var(--text-main); border: 1px solid var(--border-color); transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;" onmouseover="this.style.backgroundColor='var(--btn-clear-hover)'" onmouseout="this.style.backgroundColor='var(--btn-clear-bg)'">Clear</button>
                </div>
            </div>"""
            
    if search_append in content:
        content = content.replace(search_append, replace_append)

    # Hunk 4: Version Bump
    if '<span class="version">v1.24.0</span>' in content:
        content = content.replace('<span class="version">v1.24.0</span>', '<span class="version">v1.25.0</span>')
    elif '<span class="version">v1.23.0</span>' in content:
        content = content.replace('<span class="version">v1.23.0</span>', '<span class="version">v1.25.0</span>')

    # Output to new version
    output_filename = "svg_to_png_converter_v1_25_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v1.25.0)!")

if __name__ == "__main__":
    patch_file()