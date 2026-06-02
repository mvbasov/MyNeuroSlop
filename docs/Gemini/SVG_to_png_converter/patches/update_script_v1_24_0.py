import sys

def patch_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Hunk 1: Extract the data URL strip out of the input-section in the DOM layout
    search1 = r"""            <div class="input-section">
                <textarea id="svg-input" placeholder="Paste or edit raw SVG code here..."><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#4A90E2" />
  <text x="50" y="58" font-family="sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle">SVG</text>
</svg></textarea>
                <div class="data-url-strip" style="margin-top: 16px; display: flex; flex-direction: column; gap: 8px;">
                    <label class="toggle-label" title="Wrap generated data URL in an HTML link tag">
                        <input type="checkbox" id="chk-wrap-link">
                        <span>Wrap in &lt;link rel="icon"&gt; tag</span>
                    </label>
                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG..." style="flex-grow: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                        <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                        <button id="btn-clear-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap; background: var(--btn-clear-bg); color: var(--text-main); border: 1px solid var(--border-color); transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;" onmouseover="this.style.backgroundColor='var(--btn-clear-hover)'" onmouseout="this.style.backgroundColor='var(--btn-clear-bg)'">Clear</button>
                    </div>
                </div>
            </div>

            <div class="preview-section">"""
    
    replace1 = r"""            <div class="input-section">
                <textarea id="svg-input" placeholder="Paste or edit raw SVG code here..."><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#4A90E2" />
  <text x="50" y="58" font-family="sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle">SVG</text>
</svg></textarea>
            </div>

            <div class="data-url-strip" style="display: flex; flex-direction: column; gap: 8px; width: 100%;">
                <label class="toggle-label" title="Wrap generated data URL in an HTML link tag">
                    <input type="checkbox" id="chk-wrap-link">
                    <span>Wrap in &lt;link rel="icon"&gt; tag</span>
                </label>
                <div style="display: flex; gap: 8px;">
                    <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG..." style="flex-grow: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                    <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                    <button id="btn-clear-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap; background: var(--btn-clear-bg); color: var(--text-main); border: 1px solid var(--border-color); transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;" onmouseover="this.style.backgroundColor='var(--btn-clear-hover)'" onmouseout="this.style.backgroundColor='var(--btn-clear-bg)'">Clear</button>
                </div>
            </div>

            <div class="preview-section">"""

    # Hunk 2: Apply CSS rules to push the strip to the bottom as a full-width row on wide screens
    search2 = r"""        @media (min-width: 700px) {
            #svg-to-png-app .main-content {
                flex-direction: row;
                align-items: stretch;
            }
            #svg-to-png-app .input-section {
                flex: 6;
                display: flex;
                flex-direction: column;
                min-width: 0;
            }
            #svg-to-png-app .preview-section {
                flex: 4;
                display: flex;
                flex-direction: column;
                min-width: 0;
            }
            #svg-to-png-app #svg-input {
                min-height: 450px;
            }
        }"""
            
    replace2 = r"""        @media (min-width: 700px) {
            #svg-to-png-app .main-content {
                flex-direction: row;
                align-items: stretch;
                flex-wrap: wrap;
            }
            #svg-to-png-app .input-section {
                flex: 6;
                display: flex;
                flex-direction: column;
                min-width: 0;
            }
            #svg-to-png-app .preview-section {
                flex: 4;
                display: flex;
                flex-direction: column;
                min-width: 0;
            }
            #svg-to-png-app .data-url-strip {
                flex: 0 0 100%;
                order: 3;
            }
            #svg-to-png-app #svg-input {
                min-height: 450px;
            }
        }"""

    # Hunk 3: Version Bump
    search3 = r"""<span class="version">v1.23.0</span>"""
    replace3 = r"""<span class="version">v1.24.0</span>"""

    # Apply patches securely
    if all(s in content for s in [search1, search2, search3]):
        content = content.replace(search1, replace1)
        content = content.replace(search2, replace2)
        content = content.replace(search3, replace3)

        output_filename = file_path.replace("v1_23_0", "v1_24_0")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_filename} (v1.24.0)!")
    else:
        print("Error: Could not find exact strings to replace. Ensure you are patching the correct file (v1_23_0).")

if __name__ == "__main__":
    patch_file("svg_to_png_converter_v1_23_0.html")