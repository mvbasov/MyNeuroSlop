import os

def patch_html_file():
    input_filename = "svg_component_editor_v7_1_0.html"
    output_filename = "svg_component_editor_v7_2_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v7.1.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v7.1.0</div>"""
    replace1 = r"""<div class="footer-right">v7.2.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v7.2.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v7_1_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_1_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v7_2_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_2_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v7_1_0_tests.js"
    output_filename = "svg_component_editor_v7_2_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v7.1.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v7.2.0)"""
    content = content.replace(search1, replace1)

    # 2. Fix Test 9 by applying the native event dispatch bypass from v6.29.0
    search2 = r"""                // Force synchronous state update to bypass debounce race conditions
                if (typeof window.TEST_API.getActiveTag === 'function') {
                    window.TEST_API.getActiveTag();
                }
                await new Promise(r => setTimeout(r, 10));"""
    
    replace2 = r"""                // BUGFIX: Direct calls to getActiveTag() threw a TypeError because the internal function 
                // expects a native DOM Event object. We securely bypass this by dispatching natural browser 
                // events to trigger the app's listener natively, applying a 250ms delay to outwait the debounce timer!
                window.TEST_API.textarea.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                window.TEST_API.textarea.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
                await new Promise(r => setTimeout(r, 250));"""
    
    if search2 not in content:
        print("⚠️ Error: Could not find the JS Test insertion point.")
        return False

    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v7.2.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v7.2.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")