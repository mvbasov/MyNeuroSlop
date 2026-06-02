import sys

def patch_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Hunk 1: Add SVG to the format dropdown
    search1 = r"""                    <select id="sel-format">
                        <option value="image/png">PNG</option>
                        <option value="image/bmp">BMP</option>
                    </select>"""
    
    replace1 = r"""                    <select id="sel-format">
                        <option value="image/png">PNG</option>
                        <option value="image/bmp">BMP</option>
                        <option value="image/svg+xml">SVG Data URL</option>
                    </select>"""
    
    # Hunk 2: Update Format UI to change button text and tooltips dynamically
    search2 = r"""            // Sets up button labels and hover tips corresponding to chosen format
            function updateFormatUI() {
                const format = selFormat.value;
                const selectedText = selFormat.options[selFormat.selectedIndex].text;
                btnDownload.textContent = `Save ${selectedText}`;
                
                if (lblPrependPrefix) {
                    lblPrependPrefix.setAttribute('title', `When checked, prepends 'data:${format};base64,' to copied string`);
                }
            }"""
            
    replace2 = r"""            // Sets up button labels and hover tips corresponding to chosen format
            function updateFormatUI() {
                const format = selFormat.value;
                const selectedText = selFormat.options[selFormat.selectedIndex].text;
                btnDownload.textContent = `Save ${selectedText.split(' ')[0]}`;
                
                if (format === 'image/svg+xml') {
                    btnCopyBase64.textContent = 'Copy Data URL';
                    if (lblPrependPrefix) lblPrependPrefix.setAttribute('title', `When checked, prepends 'data:image/svg+xml,' to copied string`);
                } else {
                    btnCopyBase64.textContent = 'Copy Base64';
                    if (lblPrependPrefix) lblPrependPrefix.setAttribute('title', `When checked, prepends 'data:${format};base64,' to copied string`);
                }
            }"""

    # Hunk 3: Add Download Logic for SVG files
    search3 = r"""            // 4. Download file
            btnDownload.addEventListener('click', () => {
                const format = selFormat.value;
                if (format === 'image/bmp') {"""
                
    replace3 = r"""            // 4. Download file
            btnDownload.addEventListener('click', () => {
                const format = selFormat.value;
                if (format === 'image/svg+xml') {
                    const svgString = svgInput.value.trim();
                    if (!svgString) return showStatus('No SVG to save.', true);
                    const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    const downloadName = currentFileName.replace(/\.(png|bmp)$/i, '.svg');
                    a.download = downloadName;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    showStatus('SVG file downloaded!');
                } else if (format === 'image/bmp') {"""

    # Hunk 4: Add URI encoding logic for SVG copying
    search4 = r"""            // 5. Copy Base64
            btnCopyBase64.addEventListener('click', async () => {
                const format = selFormat.value;
                let dataUrl;
                
                if (format === 'image/bmp') {"""
                
    replace4 = r"""            // 5. Copy Base64
            btnCopyBase64.addEventListener('click', async () => {
                const format = selFormat.value;
                let dataUrl;
                
                if (format === 'image/svg+xml') {
                    let svgString = svgInput.value.trim();
                    if (!svgString) return showStatus('No SVG to copy.', true);
                    let compact = svgString.replace(/\s+/g, ' ').trim();
                    const encoded = encodeURIComponent(compact)
                        .replace(/['()]/g, escape)
                        .replace(/\*/g, '%2A');
                    
                    dataUrl = chkPrependPrefix.checked ? `data:image/svg+xml,${encoded}` : encoded;
                } else if (format === 'image/bmp') {"""

    # Hunk 5: Version Bump
    search5 = r"""<span class="version">v1.19.0</span>"""
    replace5 = r"""<span class="version">v1.20.0</span>"""

    # Apply patches securely
    if search1 in content and search2 in content and search3 in content and search4 in content and search5 in content:
        content = content.replace(search1, replace1)
        content = content.replace(search2, replace2)
        content = content.replace(search3, replace3)
        content = content.replace(search4, replace4)
        content = content.replace(search5, replace5)

        output_filename = file_path.replace("v1_19_0", "v1_20_0")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_filename} (v1.20.0)!")
    else:
        print("Error: Could not find exact strings to replace. Ensure you are patching the correct file.")

if __name__ == "__main__":
    patch_file("svg_to_png_converter_v1_19_0.html")