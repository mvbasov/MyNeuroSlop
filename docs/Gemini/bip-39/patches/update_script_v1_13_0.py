import sys
import os

def patch_html():
    input_file = "bip39_converter_v1_12_0.html"
    output_file = "bip39_converter_v1_13_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # 1. Bump the application version dynamically
    content = content.replace("v1.12.0", "v1.13.0")

    # 2. Inject the inline SVG Data URI Favicon into the <head>
    search_html_head = r"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIP-39 Offline Converter</title>"""

    replace_html_head = r"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIP-39 Offline Converter</title>
    <!-- 100% Offline SVG Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cG9seWdvbiBwb2ludHM9IjUwLDUgOTAsMjUgOTAsNzUgNTAsOTUgMTAsNzUgMTAsMjUiIGZpbGw9IiMwMDdiZmYiLz48dGV4dCB4PSI1MCIgeT0iNjUiIGZvbnQtZmFtaWx5PSJzeXN0ZW0tdWksIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iNDAiIGZvbnQtd2VpZ2h0PSJib2xkIiBmaWxsPSIjZmZmZmZmIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj4zOTwvdGV4dD48L3N2Zz4=">"""

    # 3. Update the dynamic test script loader reference
    search_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_12_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_12_0_tests.js");
        document.body.appendChild(script);"""

    replace_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_13_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_13_0_tests.js");
        document.body.appendChild(script);"""

    if search_html_head not in content:
        print(f"Error: Target HTML <head> string not found in {input_file}.")
        return False
        
    content = content.replace(search_html_head, replace_html_head)
    content = content.replace(search_html_script, replace_html_script)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_file}")
    return True

def patch_js():
    input_file = "bip39_converter_v1_12_0_tests.js"
    output_file = "bip39_converter_v1_13_0_tests.js"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # The test script logic doesn't actually need changing for a favicon, 
    # but we must copy it over to match the new v1.13.0 versioning protocol.
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully copied tests to {output_file}")
    return True

if __name__ == "__main__":
    html_success = patch_html()
    js_success = patch_js()
    if html_success and js_success:
        print("v1.13.0 Upgrade Complete. Offline SVG Favicon applied successfully.")