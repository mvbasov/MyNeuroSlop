import os
import re

html_file = 'svg_component_editor_v7_7_0.html'
new_html_file = 'svg_component_editor_v7_8_0.html'

test_file = 'svg_component_editor_v7_7_0_tests.js'
new_test_file = 'svg_component_editor_v7_8_0_tests.js'

# HTML Patching
if os.path.exists(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Bump version string
    html_content = html_content.replace(
        r"""<div class="footer-right">v7.7.0</div>""",
        r"""<div class="footer-right">v7.8.0</div>"""
    )
    
    # Bulletproof Regex to update the test suite filename mapping
    html_content = re.sub(
        r"script\.src = 'svg_component_editor_v7_[0-9]+_0_tests\.js';",
        r"script.src = 'svg_component_editor_v7_8_0_tests.js';",
        html_content
    )
    html_content = re.sub(
        r'script\.onerror = \(\) => console\.error\("Test suite not found: svg_component_editor_v7_[0-9]+_0_tests\.js"\);',
        r'script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_8_0_tests.js");',
        html_content
    )

    with open(new_html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ Successfully patched and created {new_html_file}")
else:
    print(f"⚠️ HTML file {html_file} not found. Ensure you generated v7.7.0 first.")

# Test File Patching
if os.path.exists(test_file):
    with open(test_file, 'r', encoding='utf-8') as f:
        test_content = f.read()

    test_replacements = [
        (
            r"""            // --- Test 16: Uncomment Functionality (Inline & Multiline Ghost Lines) ---
            console.log("Running Test 16: Uncomment functionality...");
            const commentCode = `<svg viewBox="0 0 100 100">\n  <!--<rect width="10" height="10"/>-->\n  <!--\n    <circle cx="50" cy="50" r="40" />\n  -->\n</svg>`;""",
            r"""            // --- Test 16: Uncomment Functionality (Inline & Multiline Ghost Lines) ---
            const commentCode = `<svg viewBox="0 0 100 100">\n  <!--<rect width="10" height="10"/>-->\n  <!--\n    <circle cx="50" cy="50" r="40" />\n  -->\n</svg>`;"""
        ),
        (
            r"""* SVG Component Editor - Micro Unit Test Suite (v7.7.0)""",
            r"""* SVG Component Editor - Micro Unit Test Suite (v7.8.0)"""
        )
    ]
    
    for search_str, replace_str in test_replacements:
        test_content = test_content.replace(search_str, replace_str)

    with open(new_test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    print(f"✅ Successfully patched and created {new_test_file}")
else:
    print(f"⚠️ Test file {test_file} not found. Skipping test file update.")