import sys

def patch_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Hunk 1: Add the Data URL strip to the left side under the SVG input
    search1 = r"""            <div class="input-section">
                <textarea id="svg-input" placeholder="Paste or edit raw SVG code here..."><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#4A90E2" />
  <text x="50" y="58" font-family="sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle">SVG</text>
</svg></textarea>
            </div>"""
    
    replace1 = r"""            <div class="input-section">
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
                        <input type="text" id="live-data-url" readonly placeholder="data:image/svg+xml,..." style="flex-grow: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">
                        <button id="btn-copy-live-data" style="min-height: 40px; padding: 0 16px; white-space: nowrap;">Copy Data URL</button>
                    </div>
                </div>
            </div>"""

    # Hunk 2: Bind new UI Elements
    search2 = r"""            const chkWrap80 = app.querySelector('#chk-wrap-80');
            const selFormat = app.querySelector('#sel-format');
            const lblPrependPrefix = app.querySelector('#lbl-prepend-prefix');
            const headerFavicon = app.querySelector('#header-favicon');
            
            const ctx = canvas.getContext('2d');"""
            
    replace2 = r"""            const chkWrap80 = app.querySelector('#chk-wrap-80');
            const selFormat = app.querySelector('#sel-format');
            const lblPrependPrefix = app.querySelector('#lbl-prepend-prefix');
            const headerFavicon = app.querySelector('#header-favicon');
            
            // Live Data URL Elements
            const liveDataUrlInput = app.querySelector('#live-data-url');
            const chkWrapLink = app.querySelector('#chk-wrap-link');
            const btnCopyLiveData = app.querySelector('#btn-copy-live-data');

            const ctx = canvas.getContext('2d');"""

    # Hunk 3: Add Live Sync Logic
    search3 = r"""            // Custom uncompressed 24-bit BMP encoder to prevent browser fallbacks to PNG format
            function canvasToBMP(canvasElement) {"""
                
    replace3 = r"""            // Live Data URL Sync Functionality
            function syncDataUrl() {
                let svgString = svgInput.value.trim();
                if (!svgString) {
                    liveDataUrlInput.value = '';
                    return;
                }
                
                try {
                    let compact = svgString.replace(/\s+/g, ' ').trim();
                    const encoded = encodeURIComponent(compact)
                        .replace(/['()]/g, escape)
                        .replace(/\*/g, '%2A');
                    
                    const dataUrl = `data:image/svg+xml,${encoded}`;
                    
                    if (chkWrapLink.checked) {
                        liveDataUrlInput.value = `<link rel="icon" type="image/svg+xml" href="${dataUrl}">`;
                    } else {
                        liveDataUrlInput.value = dataUrl;
                    }
                } catch (e) {
                    // Fail silently on partial/invalid edits during live typing
                }
            }

            // Custom uncompressed 24-bit BMP encoder to prevent browser fallbacks to PNG format
            function canvasToBMP(canvasElement) {"""

    # Hunk 4: Update Textarea Input Listeners
    search4 = r"""            // 0. Textarea Input
            let debounceTimer;
            svgInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    const text = e.target.value.trim();
                    if (!text) {
                        resetPreview();
                    } else {
                        loadSVGToCanvas(text, 'edited_image.png', true);
                    }
                }, 400); // 400ms debounce to wait for user to stop typing
            });"""
                
    replace4 = r"""            // 0. Textarea Input
            let debounceTimer;
            svgInput.addEventListener('input', (e) => {
                syncDataUrl(); // Immediate sync for Data URL strip
                
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    const text = e.target.value.trim();
                    if (!text) {
                        resetPreview();
                    } else {
                        loadSVGToCanvas(text, 'edited_image.png', true);
                    }
                }, 400); // 400ms debounce to wait for user to stop typing
            });

            // Live Data URL strip listeners
            chkWrapLink.addEventListener('change', syncDataUrl);
            
            btnCopyLiveData.addEventListener('click', async () => {
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

    # Hunk 5: Sync initial load and clear buttons
    search5 = r"""            // 6. Clear Button
            btnClear.addEventListener('click', () => {
                svgInput.value = '';
                resetPreview();
            });

            // 7. Initial Load
            updateFormatUI();
            if (svgInput.value.trim()) {
                loadSVGToCanvas(svgInput.value.trim(), 'default_image.png', true);
            }"""
            
    replace5 = r"""            // 6. Clear Button
            btnClear.addEventListener('click', () => {
                svgInput.value = '';
                syncDataUrl();
                resetPreview();
            });

            // 7. Initial Load
            updateFormatUI();
            if (svgInput.value.trim()) {
                loadSVGToCanvas(svgInput.value.trim(), 'default_image.png', true);
                syncDataUrl();
            }"""

    # Hunk 6: Sync file uploads / paste
    search6 = r"""                if (!fromTextarea) {
                    svgInput.value = svgString;
                }

                // Parse dimensions from the SVG string using lightweight regex"""
                
    replace6 = r"""                if (!fromTextarea) {
                    svgInput.value = svgString;
                    syncDataUrl(); // Sync the live URL strip if loaded externally
                }

                // Parse dimensions from the SVG string using lightweight regex"""

    # Hunk 7: Version Bump
    search7 = r"""<span class="version">v1.20.0</span>"""
    replace7 = r"""<span class="version">v1.21.0</span>"""

    # Apply patches securely
    if all(s in content for s in [search1, search2, search3, search4, search5, search6, search7]):
        content = content.replace(search1, replace1)
        content = content.replace(search2, replace2)
        content = content.replace(search3, replace3)
        content = content.replace(search4, replace4)
        content = content.replace(search5, replace5)
        content = content.replace(search6, replace6)
        content = content.replace(search7, replace7)

        output_filename = file_path.replace("v1_20_0", "v1_21_0")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_filename} (v1.21.0)!")
    else:
        print("Error: Could not find exact strings to replace. Ensure you are patching the correct file (v1_20_0).")

if __name__ == "__main__":
    patch_file("svg_to_png_converter_v1_20_0.html")