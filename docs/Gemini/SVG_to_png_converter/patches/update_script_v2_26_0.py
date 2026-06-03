import os

def update_files():
    html_file = "svg_to_png_converter_v2_25_0.html"
    js_file = "svg_to_png_converter_v2_25_0_tests.js"
    
    html_out = "svg_to_png_converter_v2_26_0.html"
    js_out = "svg_to_png_converter_v2_26_0_tests.js"

    # ---------------------------------------------------------
    # 1. Update the HTML File
    # ---------------------------------------------------------
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Update version tag
        html_search_1 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.25.0</span>"""
        html_replace_1 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.26.0</span>"""
        html_content = html_content.replace(html_search_1, html_replace_1)

        # Replace the test block with explicit boundaries and deletion instructions
        html_search_2 = r"""            // --- Unit Testing Hook ---
            // Conditionally exposes internals and dynamically loads the external test suite.
            if (window.location.search.includes('test=')) {
                window.__TEST_API__ = {
                    formatXML: formatXML,
                    canvasToBMP: canvasToBMP,
                    loadSVGToCanvas: loadSVGToCanvas,
                    syncDataUrl: syncDataUrl,
                    syncFromDataUrl: syncFromDataUrl
                };
                console.log("🧪 Unit Testing API exposed at window.__TEST_API__");
                
                // Dynamically inject the external testing framework
                const script = document.createElement('script');
                script.src = 'svg_to_png_converter_v2_25_0_tests.js';
                script.onload = () => {
                    if (window.location.search.includes('test=run') && window.__runTests) {
                        setTimeout(() => window.__runTests(), 500);
                    }
                };
                script.onerror = () => console.error("❌ Failed to load test_suite_v2_25_0.js. Ensure it is in the same directory.");
                document.body.appendChild(script);
            }"""

        html_replace_2 = r"""            // =========================================================================
            // >>> BEGIN OF TESTING ARCHITECTURE <<<
            // [SAFE TO DELETE]: The following code block is responsible exclusively for 
            // the micro unit testing architecture. It can be safely removed without 
            // altering or affecting the original program's functionality.
            // =========================================================================
            if (window.location.search.includes('test=')) {
                window.__TEST_API__ = {
                    formatXML: formatXML,
                    canvasToBMP: canvasToBMP,
                    loadSVGToCanvas: loadSVGToCanvas,
                    syncDataUrl: syncDataUrl,
                    syncFromDataUrl: syncFromDataUrl
                };
                console.log("🧪 Unit Testing API exposed at window.__TEST_API__");
                
                // Dynamically inject the external testing framework
                const script = document.createElement('script');
                script.src = 'svg_to_png_converter_v2_26_0_tests.js';
                script.onload = () => {
                    if (window.location.search.includes('test=run') && window.__runTests) {
                        setTimeout(() => window.__runTests(), 500);
                    }
                };
                script.onerror = () => console.error("❌ Failed to load test_suite_v2_26_0.js. Ensure it is in the same directory.");
                document.body.appendChild(script);
            }
            // >>> END OF TESTING ARCHITECTURE <<<
            // ========================================================================="""
        html_content = html_content.replace(html_search_2, html_replace_2)

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

        # Bump internal script version string
        js_search_1 = r"""console.log("%c💡 test_suite_v2_25_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_replace_1 = r"""console.log("%c💡 test_suite_v2_26_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_content = js_content.replace(js_search_1, js_replace_1)

        with open(js_out, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Successfully updated {js_out}")
    else:
        print(f"❌ Could not find {js_file}")

if __name__ == "__main__":
    update_files()