import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_21_0.html"
    output_filename = "svg_component_editor_v6_22_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.21.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.21.0</div>"""
    replace1 = r"""<div class="footer-right">v6.22.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.22.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_21_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_21_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_22_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_22_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_21_0_tests.js"
    output_filename = "svg_component_editor_v6_22_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.21.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.22.0)"""
    content = content.replace(search1, replace1)

    # 2. Reformat console.table to use objects, avoiding Chrome's primitive string single quotes
    search2 = r"""        // Execution Summary
        const passedStr = passed > 0 ? `${passed} ✅` : passed;
        const failedStr = failed > 0 ? `${failed} ❌` : `${failed} ✅`;
        console.table({ 'Passed': passedStr, 'Failed': failedStr, 'Total': passed + failed });"""
    
    replace2 = r"""        // Execution Summary
        console.table({
            'Passed': { 'Count': passed, 'Status': passed > 0 ? '✅' : '⚠️' },
            'Failed': { 'Count': failed, 'Status': failed > 0 ? '❌' : '✅' },
            'Total':  { 'Count': passed + failed, 'Status': failed === 0 ? '✅' : '❌' }
        });"""
    
    if search2 not in content:
        print("⚠️ Error: Could not find the JS Test insertion point.")
        return False

    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.22.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.22.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")