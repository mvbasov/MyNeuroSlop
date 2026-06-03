import os

def update_files():
    html_file = "svg_to_png_converter_v2_23_0.html"
    js_file = "svg_to_png_converter_v2_23_0_tests.js"
    
    html_out = "svg_to_png_converter_v2_24_0.html"
    js_out = "svg_to_png_converter_v2_24_0_tests.js"

    # ---------------------------------------------------------
    # 1. Update the HTML File
    # ---------------------------------------------------------
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        html_search_1 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.23.0</span>"""
        html_replace_1 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.24.0</span>"""
        html_content = html_content.replace(html_search_1, html_replace_1)

        html_search_2 = r"""script.src = 'svg_to_png_converter_v2_23_0_tests.js';"""
        html_replace_2 = r"""script.src = 'svg_to_png_converter_v2_24_0_tests.js';"""
        html_content = html_content.replace(html_search_2, html_replace_2)

        html_search_3 = r"""script.onerror = () => console.error("❌ Failed to load test_suite_v2_23_0.js. Ensure it is in the same directory.");"""
        html_replace_3 = r"""script.onerror = () => console.error("❌ Failed to load test_suite_v2_24_0.js. Ensure it is in the same directory.");"""
        html_content = html_content.replace(html_search_3, html_replace_3)

        with open(html_out, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Successfully updated {html_out}")
    else:
        print(f"❌ Could not find {html_file}")


    # ---------------------------------------------------------
    # 2. Update the JS Test File
    # ---------------------------------------------------------
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # Fix the exact encoded string expectation (changing '/' to '%2F')
        js_search_1 = r"""        assertTrue("Data URL Sync: Encodes properly", liveDataUrlInput.value.includes('%3Csvg%3E%3Ccircle/%3E%3C/svg%3E'));"""
        js_replace_1 = r"""        assertTrue("Data URL Sync: Encodes properly", liveDataUrlInput.value.includes('%3Csvg%3E%3Ccircle%2F%3E%3C%2Fsvg%3E'));"""
        js_content = js_content.replace(js_search_1, js_replace_1)

        # Standardize the decoding test to use %2F as well for consistency
        js_search_2 = r"""        liveDataUrlInput.value = 'data:image/svg+xml,%3Csvg%3E%3Crect/%3E%3C/svg%3E';"""
        js_replace_2 = r"""        liveDataUrlInput.value = 'data:image/svg+xml,%3Csvg%3E%3Crect%2F%3E%3C%2Fsvg%3E';"""
        js_content = js_content.replace(js_search_2, js_replace_2)

        # Bump internal script version string
        js_search_3 = r"""console.log("%c💡 test_suite_v2_23_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_replace_3 = r"""console.log("%c💡 test_suite_v2_24_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_content = js_content.replace(js_search_3, js_replace_3)

        with open(js_out, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Successfully updated {js_out}")
    else:
        print(f"❌ Could not find {js_file}")

if __name__ == "__main__":
    update_files()