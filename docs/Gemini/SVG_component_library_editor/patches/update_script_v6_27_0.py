import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_26_0.html"
    output_filename = "svg_component_editor_v6_27_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.26.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.26.0</div>"""
    replace1 = r"""<div class="footer-right">v6.27.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.27.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_26_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_26_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_27_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_27_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_26_0_tests.js"
    output_filename = "svg_component_editor_v6_27_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.26.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.27.0)"""
    content = content.replace(search1, replace1)

    # 2. Inject a synchronous DOM state delay to allow the app's internal cursor polling loop to catch up!
    search2 = r"""                // Target parser deep into the polygon tag payload to guarantee context lock
                // Bypassing edge-spacing issues by targeting the 'points' attribute directly
                const attrIdx = origCode.search(/points=/);
                window.TEST_API.textarea.selectionStart = attrIdx + 3;
                window.TEST_API.textarea.selectionEnd = attrIdx + 3;
                
                // Fire shotgun API cascade for the rotation command"""
    
    replace2 = r"""                // Target parser deep into the polygon tag payload to guarantee context lock
                // Bypassing edge-spacing issues by targeting the 'points' attribute directly
                const attrIdx = origCode.search(/points=/);
                window.TEST_API.textarea.selectionStart = attrIdx + 3;
                window.TEST_API.textarea.selectionEnd = attrIdx + 3;
                
                // BUGFIX: The application uses an asynchronous polling loop to update 'activeTagInfo'.
                // We MUST wait 50ms for it to sync with the new cursor position, otherwise the first command executes on stale tag data!
                await new Promise(r => setTimeout(r, 50));
                
                // Fire shotgun API cascade for the rotation command"""
    
    if search2 not in content:
        print("⚠️ Error: Could not find the JS Test insertion point.")
        return False

    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.27.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.27.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")