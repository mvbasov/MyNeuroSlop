import os

def update_files():
    html_file = "base64_converter_v1_3_0.html"
    js_file = "base64_converter_v1_3_0_tests.js"
    
    html_out = "base64_converter_v1_4_0.html"
    js_out = "base64_converter_v1_4_0_tests.js"

    # ---------------------------------------------------------
    # 1. Update the HTML File
    # ---------------------------------------------------------
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        html_search_1 = r"""<span>v1.3.0</span>"""
        html_replace_1 = r"""<span>v1.4.0</span>"""
        html_content = html_content.replace(html_search_1, html_replace_1)

        html_search_2 = r"""script.src = 'base64_converter_v1_3_0_tests.js';"""
        html_replace_2 = r"""script.src = 'base64_converter_v1_4_0_tests.js';"""
        html_content = html_content.replace(html_search_2, html_replace_2)

        html_search_3 = r"""script.onerror = () => console.error("❌ Failed to load base64_converter_v1_3_0_tests.js. Ensure it is in the same directory.");"""
        html_replace_3 = r"""script.onerror = () => console.error("❌ Failed to load base64_converter_v1_4_0_tests.js. Ensure it is in the same directory.");"""
        html_content = html_content.replace(html_search_3, html_replace_3)

        # Inject the instructional footnote at the bottom of the app container
        html_search_4 = r"""        <div class="footer">
            <span>Demo Application</span>
            <span>v1.4.0</span>
        </div>
    </div>"""

        html_replace_4 = r"""        <div class="footer">
            <span>Demo Application</span>
            <span>v1.4.0</span>
        </div>
        
        <div style="margin-top: 1rem; padding: 1rem; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px; font-size: 0.85rem; color: #856404;">
            <strong>🧪 Testing Demonstration:</strong><br>
            To run the automated micro unit tests, append <code>?test=run</code> to this page's URL and refresh.<br><br>
            <em>Note:</em> The tests will intentionally <strong>fail</strong> because an artificial bug was injected into the <code>encodeToBase64()</code> function to demonstrate the UI enforcer. Open the HTML source code and look for the <code>[ARTIFICIAL MISTAKE INJECTED FOR TESTING DEMONSTRATION]</code> comment to fix it!
        </div>
    </div>"""
        html_content = html_content.replace(html_search_4, html_replace_4)

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

        js_search_2 = r"""// base64_converter_v1_3_0_tests.js - Micro Unit Test System"""
        js_replace_2 = r"""// base64_converter_v1_4_0_tests.js - Micro Unit Test System"""
        js_content = js_content.replace(js_search_2, js_replace_2)

        js_search_3 = r"""console.log("%c💡 base64_converter_v1_3_0_tests.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_replace_3 = r"""console.log("%c💡 base64_converter_v1_4_0_tests.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_content = js_content.replace(js_search_3, js_replace_3)

        with open(js_out, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Successfully updated {js_out}")
    else:
        print(f"❌ Could not find {js_file}")

if __name__ == "__main__":
    update_files()