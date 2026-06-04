import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_12_0.html"
    output_filename = "svg_component_editor_v6_13_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.12.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.12.0</div>"""
    replace1 = r"""<div class="footer-right">v6.13.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.13.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_12_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_12_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_13_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_13_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_12_0_tests.js"
    output_filename = "svg_component_editor_v6_13_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.12.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.13.0)"""
    content = content.replace(search1, replace1)

    # 2. Implement robust, dynamic cursor targeting based on RegExp
    search2 = r"""            // Test 7: Deep Coordinates Recalculation (Mirroring / Flip)
            // Execute horizontal mirror which heavily relies on matrix math translation
            // Re-acquire contextual focus deep inside the tag (index 15) to guarantee parser lock-on
            window.TEST_API.textarea.selectionStart = 15;
            window.TEST_API.textarea.selectionEnd = 15;
            window.TEST_API.transformShape('mirror', 'horizontal');"""
    
    replace2 = r"""            // Test 7: Deep Coordinates Recalculation (Mirroring / Flip)
            // Execute horizontal mirror which heavily relies on matrix math translation
            // Re-acquire contextual focus dynamically based on actual element index to prevent formatting misses
            const codeRef = window.TEST_API.textarea.value;
            const dynamicTagIndex = codeRef.search(/<(rect|path|polygon|circle|ellipse|use)/);
            window.TEST_API.textarea.selectionStart = dynamicTagIndex + 5;
            window.TEST_API.textarea.selectionEnd = dynamicTagIndex + 5;
            window.TEST_API.transformShape('mirror', 'horizontal');"""
    
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.13.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.13.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")