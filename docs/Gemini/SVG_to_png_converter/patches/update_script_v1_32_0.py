import sys
import os
import re

def patch_file():
    # Target the v1.31.0 file
    file_path = "svg_to_png_converter_v1_31_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Remove the HTML button from the right-side controls
    search_html = r"""                <button id="btn-copy-base64">Copy Base64</button>
                <button id="btn-clear" class="btn-clear">Clear</button>
            </div>"""
    replace_html = r"""                <button id="btn-copy-base64">Copy Base64</button>
            </div>"""
    
    if search_html in content:
        content = content.replace(search_html, replace_html)
    else:
        # Fallback regex in case of slight whitespace changes
        content = re.sub(r'\s*<button id="btn-clear" class="btn-clear">Clear</button>', '', content)

    # Hunk 2: Remove the JS DOM query to prevent 'null' errors
    search_js1 = r"""            const btnCopyBase64 = app.querySelector('#btn-copy-base64');
            const btnClear = app.querySelector('#btn-clear');
            const chkPrependPrefix = app.querySelector('#chk-prepend-prefix');"""
    replace_js1 = r"""            const btnCopyBase64 = app.querySelector('#btn-copy-base64');
            const chkPrependPrefix = app.querySelector('#chk-prepend-prefix');"""
            
    if search_js1 in content:
        content = content.replace(search_js1, replace_js1)
    else:
        content = re.sub(r'\s*const btnClear = app\.querySelector\(\'#btn-clear\'\);', '', content)

    # Hunk 3: Remove the redundant Event Listener
    search_js2 = r"""            // 6. Clear Button
            btnClear.addEventListener('click', () => {
                svgInput.value = '';
                syncDataUrl();
                resetPreview();
            });

            // 7. Initial Load"""
    replace_js2 = r"""            // 7. Initial Load"""
    
    if search_js2 in content:
        content = content.replace(search_js2, replace_js2)
    else:
        content = re.sub(r'\s*// 6\. Clear Button\s*btnClear\.addEventListener[\s\S]*?// 7\. Initial Load', r'\n\n            // 7. Initial Load', content)

    # Hunk 4: Global Version Bump
    content = content.replace('v1.31.0', 'v1.32.0')

    # Output to new version
    output_filename = "svg_to_png_converter_v1_32_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v1.32.0)!")

if __name__ == "__main__":
    patch_file()