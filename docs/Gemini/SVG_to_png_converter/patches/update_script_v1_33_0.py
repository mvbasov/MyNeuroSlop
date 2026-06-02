import sys
import os
import re

def patch_file():
    # Target the v1.32.0 file
    file_path = "svg_to_png_converter_v1_32_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Remove the HTML button from the Data URL strip
    search_html = r"""                    <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG...">
                    <button id="btn-copy-live-data">Copy Data URL</button>
                    <button id="btn-clear-live-data" class="btn-clear">Clear</button>"""
    replace_html = r"""                    <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG...">
                    <button id="btn-clear-live-data" class="btn-clear">Clear</button>"""
    
    if search_html in content:
        content = content.replace(search_html, replace_html)
    else:
        # Fallback regex
        content = re.sub(r'\s*<button id="btn-copy-live-data">[^<]*</button>', '', content)

    # Hunk 2: Remove the JS DOM query
    search_js1 = r"""            const chkWrapLink = app.querySelector('#chk-wrap-link');
            const btnCopyLiveData = app.querySelector('#btn-copy-live-data');
            const btnClearLiveData = app.querySelector('#btn-clear-live-data');"""
    replace_js1 = r"""            const chkWrapLink = app.querySelector('#chk-wrap-link');
            const btnClearLiveData = app.querySelector('#btn-clear-live-data');"""
            
    if search_js1 in content:
        content = content.replace(search_js1, replace_js1)
    else:
        content = re.sub(r'\s*const btnCopyLiveData = app\.querySelector\(\'#btn-copy-live-data\'\);', '', content)

    # Hunk 3: Remove the associated Event Listener
    # Using a robust regex to safely match the entire block since it contains many lines
    event_listener_regex = r'\s*btnCopyLiveData\.addEventListener\(\'click\', async \(\) => \{[\s\S]*?\}\);\s*'
    content = re.sub(event_listener_regex, '\n\n            ', content)

    # Hunk 4: Global Version Bump
    content = content.replace('v1.32.0', 'v1.33.0')

    # Output to new version
    output_filename = "svg_to_png_converter_v1_33_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v1.33.0)!")

if __name__ == "__main__":
    patch_file()