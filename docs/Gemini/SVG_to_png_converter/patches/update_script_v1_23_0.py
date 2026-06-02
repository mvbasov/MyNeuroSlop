import sys

def patch_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Hunk 1: Remove readonly and update placeholder
    search1 = r"""                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="live-data-url" readonly placeholder="data:image/svg+xml,..." style="flex-grow: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">"""
    
    replace1 = r"""                    <div style="display: flex; gap: 8px;">
                        <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG..." style="flex-grow: 1; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-input); color: var(--text-main); font-family: monospace; font-size: 0.85rem; outline: none; transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;">"""

    # Hunk 2: Add Bidirectional Sync and XML Formatter
    search2 = r"""            // Live Data URL Sync Functionality
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
            }"""
            
    replace2 = r"""            // Live Data URL Sync Functionality
            let isSyncingData = false;

            function formatXML(xmlString) {
                const parser = new DOMParser();
                const doc = parser.parseFromString(xmlString, 'image/svg+xml');
                if (doc.querySelector('parsererror')) return xmlString;
                
                let indentLevel = 0;
                function serializeNode(node) {
                    let str = '';
                    const indent = '  '.repeat(indentLevel);
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        str += indent + '<' + node.tagName;
                        for (let i = 0; i < node.attributes.length; i++) {
                            str += ' ' + node.attributes[i].name + '="' + node.attributes[i].value.replace(/"/g, '&quot;') + '"';
                        }
                        const hasChildElements = Array.from(node.childNodes).some(n => n.nodeType === Node.ELEMENT_NODE);
                        if (hasChildElements) {
                            str += '>\n';
                            indentLevel++;
                            for (let i = 0; i < node.childNodes.length; i++) str += serializeNode(node.childNodes[i]);
                            indentLevel--;
                            str += indent + '</' + node.tagName + '>\n';
                        } else if (node.textContent.trim()) {
                            str += '>' + node.textContent.trim() + '</' + node.tagName + '>\n';
                        } else {
                            str += '/>\n';
                        }
                    } else if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                        str += indent + node.textContent.trim() + '\n';
                    }
                    return str;
                }
                return serializeNode(doc.documentElement).trim();
            }

            function syncDataUrl() {
                if (isSyncingData) return;
                let svgString = svgInput.value.trim();
                if (!svgString) {
                    isSyncingData = true;
                    liveDataUrlInput.value = '';
                    isSyncingData = false;
                    return;
                }
                
                try {
                    let compact = svgString.replace(/\s+/g, ' ').trim();
                    const encoded = encodeURIComponent(compact)
                        .replace(/['()]/g, escape)
                        .replace(/\*/g, '%2A');
                    
                    const dataUrl = `data:image/svg+xml,${encoded}`;
                    
                    isSyncingData = true;
                    if (chkWrapLink.checked) {
                        liveDataUrlInput.value = `<link rel="icon" type="image/svg+xml" href="${dataUrl}">`;
                    } else {
                        liveDataUrlInput.value = dataUrl;
                    }
                    isSyncingData = false;
                } catch (e) {
                    // Fail silently
                }
            }

            function syncFromDataUrl() {
                if (isSyncingData) return;
                let input = liveDataUrlInput.value.trim();
                if (!input) {
                    isSyncingData = true;
                    svgInput.value = '';
                    resetPreview();
                    isSyncingData = false;
                    return;
                }

                if (input.toLowerCase().includes('<link')) {
                    const match = input.match(/href=["'](data:image\/svg\+xml[^"']+)["']/i);
                    if (match) input = match[1];
                }

                try {
                    let svgContent = '';
                    if (input.startsWith('data:image/svg+xml;base64,')) {
                        svgContent = atob(input.substring(26));
                    } else if (input.startsWith('data:image/svg+xml,')) {
                        svgContent = decodeURIComponent(input.substring(19));
                    } else {
                        return; // Ignore incomplete/invalid typing
                    }

                    isSyncingData = true;
                    svgInput.value = formatXML(svgContent);
                    
                    // Trigger preview update
                    if (typeof debounceTimer !== 'undefined') clearTimeout(debounceTimer);
                    loadSVGToCanvas(svgInput.value, 'edited_image.png', true);
                    isSyncingData = false;
                } catch (e) {
                    // Fail silently on typing mid-paste
                }
            }"""

    # Hunk 3: Add event listener to the Data URL input
    search3 = r"""            // Live Data URL strip listeners
            chkWrapLink.addEventListener('change', syncDataUrl);
            
            btnCopyLiveData.addEventListener('click', async () => {"""
                
    replace3 = r"""            // Live Data URL strip listeners
            chkWrapLink.addEventListener('change', syncDataUrl);
            liveDataUrlInput.addEventListener('input', syncFromDataUrl);
            
            btnCopyLiveData.addEventListener('click', async () => {"""

    # Hunk 4: Version Bump
    search4 = r"""<span class="version">v1.22.0</span>"""
    replace4 = r"""<span class="version">v1.23.0</span>"""

    # Apply patches securely
    if all(s in content for s in [search1, search2, search3, search4]):
        content = content.replace(search1, replace1)
        content = content.replace(search2, replace2)
        content = content.replace(search3, replace3)
        content = content.replace(search4, replace4)

        output_filename = file_path.replace("v1_22_0", "v1_23_0")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_filename} (v1.23.0)!")
    else:
        print("Error: Could not find exact strings to replace. Ensure you are patching the correct file (v1_22_0).")

if __name__ == "__main__":
    patch_file("svg_to_png_converter_v1_22_0.html")