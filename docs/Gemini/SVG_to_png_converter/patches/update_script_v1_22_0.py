import sys

def patch_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Hunk 1: Add Clear button to HTML layout
    search1 = r"""                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="live-data-url" readonly placeholder="data:image/svg+xml,..." style="flex-grow: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                        <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                    </div>"""
    
    replace1 = r"""                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="live-data-url" readonly placeholder="data:image/svg+xml,..." style="flex-grow: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                        <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                        <button id="btn-clear-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap; background: var(--btn-clear-bg); color: var(--text-main); border: 1px solid var(--border-color); transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;" onmouseover="this.style.backgroundColor='var(--btn-clear-hover)'" onmouseout="this.style.backgroundColor='var(--btn-clear-bg)'">Clear</button>
                    </div>"""

    # Hunk 2: Bind new Clear button element
    search2 = r"""            // Live Data URL Elements
            const liveDataUrlInput = app.querySelector('#live-data-url');
            const chkWrapLink = app.querySelector('#chk-wrap-link');
            const btnCopyLiveData = app.querySelector('#btn-copy-live-data');

            const ctx = canvas.getContext('2d');"""
            
    replace2 = r"""            // Live Data URL Elements
            const liveDataUrlInput = app.querySelector('#live-data-url');
            const chkWrapLink = app.querySelector('#chk-wrap-link');
            const btnCopyLiveData = app.querySelector('#btn-copy-live-data');
            const btnClearLiveData = app.querySelector('#btn-clear-live-data');

            const ctx = canvas.getContext('2d');"""

    # Hunk 3: Add Clear Event Listener
    search3 = r"""            btnCopyLiveData.addEventListener('click', async () => {
                const text = liveDataUrlInput.value;
                if (!text) return showStatus('No Data URL to copy.', true);
                
                try {
                    await navigator.clipboard.writeText(text);
                    showStatus('Data URL copied to clipboard!');
                } catch (err) {
                    liveDataUrlInput.select();
                    try {
                        document.execCommand('copy');
                        showStatus('Data URL copied to clipboard!');
                    } catch (ex) {
                        showStatus('Failed to copy Data URL.', true);
                    }
                }
            });"""
                
    replace3 = r"""            btnCopyLiveData.addEventListener('click', async () => {
                const text = liveDataUrlInput.value;
                if (!text) return showStatus('No Data URL to copy.', true);
                
                try {
                    await navigator.clipboard.writeText(text);
                    showStatus('Data URL copied to clipboard!');
                } catch (err) {
                    liveDataUrlInput.select();
                    try {
                        document.execCommand('copy');
                        showStatus('Data URL copied to clipboard!');
                    } catch (ex) {
                        showStatus('Failed to copy Data URL.', true);
                    }
                }
            });

            btnClearLiveData.addEventListener('click', () => {
                svgInput.value = '';
                syncDataUrl();
                resetPreview();
            });"""

    # Hunk 4: Version Bump
    search4 = r"""<span class="version">v1.21.0</span>"""
    replace4 = r"""<span class="version">v1.22.0</span>"""

    # Apply patches securely
    if all(s in content for s in [search1, search2, search3, search4]):
        content = content.replace(search1, replace1)
        content = content.replace(search2, replace2)
        content = content.replace(search3, replace3)
        content = content.replace(search4, replace4)

        output_filename = file_path.replace("v1_21_0", "v1_22_0")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_filename} (v1.22.0)!")
    else:
        print("Error: Could not find exact strings to replace. Ensure you are patching the correct file (v1_21_0).")

if __name__ == "__main__":
    patch_file("svg_to_png_converter_v1_21_0.html")