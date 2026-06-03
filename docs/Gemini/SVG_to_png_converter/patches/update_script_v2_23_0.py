import os

def update_files():
    html_file = "svg_to_png_converter_v2_22_1.html"
    js_file = "svg_to_png_converter_v2_22_1_tests.js"
    
    html_out = "svg_to_png_converter_v2_23_0.html"
    js_out = "svg_to_png_converter_v2_23_0_tests.js"

    # ---------------------------------------------------------
    # 1. Update the HTML File
    # ---------------------------------------------------------
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        html_search_1 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.22.0</span>"""
        html_replace_1 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.23.0</span>"""
        html_content = html_content.replace(html_search_1, html_replace_1)

        html_search_2 = r"""script.src = 'svg_to_png_converter_v2_22_1_tests.js';"""
        html_replace_2 = r"""script.src = 'svg_to_png_converter_v2_23_0_tests.js';"""
        html_content = html_content.replace(html_search_2, html_replace_2)

        html_search_3 = r"""script.onerror = () => console.error("❌ Failed to load test_suite_v2_22_0.js. Ensure it is in the same directory.");"""
        html_replace_3 = r"""script.onerror = () => console.error("❌ Failed to load test_suite_v2_23_0.js. Ensure it is in the same directory.");"""
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

        js_search_1 = r"""    // ==================== SUMMARY, RESET, AND ENLARGED FINAL TOAST ====================
    const color = failed > 0 ? '#f44336' : '#4CAF50';"""

        js_replace_1 = r"""    // ==================== BMP ROW PADDING TEST ====================
    console.log("%c📝 Running BMP Row Padding Test...", "color: #FF9800; font-weight: bold;");
    try {
        const oddSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"><rect width="1" height="1" fill="#000000"/></svg>`;
        await loadTestSVG(oddSvg, "odd.svg");
        const canvas = document.querySelector('#svg-to-png-app canvas');
        const bmpURL = api.canvasToBMP(canvas);
        const bytes = base64ToBytes(bmpURL.split(',')[1]);
        // 1 pixel = 3 bytes (BGR). Next multiple of 4 is 4 bytes. 1 byte padding.
        // 54 bytes (header) + 4 bytes (pixel row) = 58 bytes.
        assertTrue("BMP Padding: 1x1 image generates exact 58 byte file", bytes.byteLength === 58);
    } catch (err) {
        assertTrue("BMP Padding test should not throw", false, err.message);
    }

    // ==================== DATA URL SYNC TESTS ====================
    console.log("%c📝 Running Data URL Sync Tests...", "color: #FF9800; font-weight: bold;");
    try {
        const svgInput = document.querySelector('#svg-input');
        const liveDataUrlInput = document.querySelector('#live-data-url');
        const chkWrapLink = document.querySelector('#chk-wrap-link');

        svgInput.value = '<svg><circle/></svg>';
        api.syncDataUrl();
        assertTrue("Data URL Sync: Encodes properly", liveDataUrlInput.value.includes('%3Csvg%3E%3Ccircle/%3E%3C/svg%3E'));

        chkWrapLink.checked = true;
        api.syncDataUrl();
        assertStartsWith("Data URL Sync: Wraps in <link> tag", liveDataUrlInput.value, '<link rel="icon"');
        chkWrapLink.checked = false;

        liveDataUrlInput.value = 'data:image/svg+xml,%3Csvg%3E%3Crect/%3E%3C/svg%3E';
        api.syncFromDataUrl();
        assertTrue("Sync From Data URL: Decodes safely", svgInput.value.includes('<rect/>'));
    } catch (err) {
        assertTrue("Data URL Sync test should not throw", false, err.message);
    }

    // ==================== DIMENSION PARSING TESTS ====================
    console.log("%c📝 Running Dimension Parsing Failsafe Tests...", "color: #FF9800; font-weight: bold;");
    try {
        await loadTestSVG(`<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><rect/></svg>`, "perc.svg");
        const canvas = document.querySelector('#svg-to-png-app canvas');
        assertTrue("Dimensions: 100% width falls back to default 300", canvas.width === 300);

        await loadTestSVG(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150" width="100%" height="100%"><rect/></svg>`, "viewbox.svg");
        assertTrue("Dimensions: Percentage widths yield to viewBox", canvas.width === 150);
    } catch (err) {
        assertTrue("Dimension parsing test should not throw", false, err.message);
    }

    // ==================== ADVANCED XML FORMAT TESTS ====================
    console.log("%c📝 Running Advanced XML Formatting Tests...", "color: #FF9800; font-weight: bold;");
    assert("formatXML: Multi-attribute spacing cleaned", api.formatXML('<rect id="a"  class="b" />'), '<rect id="a" class="b"/>');
    assert("formatXML: Style tag kept open", api.formatXML('<svg><style>.a{fill:red;}</style></svg>'), '<svg>\n  <style>.a{fill:red;}</style>\n</svg>');

    // ==================== SUMMARY, RESET, AND ENLARGED FINAL TOAST ====================
    const color = failed > 0 ? '#f44336' : '#4CAF50';"""

        js_content = js_content.replace(js_search_1, js_replace_1)

        js_search_2 = r"""console.log("%c💡 test_suite_v2_22_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_replace_2 = r"""console.log("%c💡 test_suite_v2_23_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_content = js_content.replace(js_search_2, js_replace_2)

        with open(js_out, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Successfully updated {js_out}")
    else:
        print(f"❌ Could not find {js_file}")

if __name__ == "__main__":
    update_files()