import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_20_1.html"
    output_filename = "svg_component_editor_v6_21_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.20.1.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.20.1</div>"""
    replace1 = r"""<div class="footer-right">v6.21.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.21.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_20_1_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_20_1_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_21_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_21_0_tests.js");"""
    content = content.replace(search2, replace2)

    # 3. BUGFIX: Update the DOM selector to ensure we calculate the bounding box of the true canvas, not a UI icon!
    search3 = r"""                                    // Dynamically extract the bounding box center of the rendered element
                                    let svgNode = document.querySelector('svg');
                                    let activeEl = svgNode ? svgNode.lastElementChild : null;"""
    
    replace3 = r"""                                    // Dynamically extract the bounding box center of the true rendered shape, bypassing UI icons
                                    let svgNode = typeof userSvgContainer !== 'undefined' && userSvgContainer ? userSvgContainer.querySelector('svg') : document.querySelectorAll('svg')[document.querySelectorAll('svg').length - 1];
                                    let activeEl = svgNode ? svgNode.lastElementChild : null;"""
    
    if search3 not in content:
        print("⚠️ Error: Could not find the HTML insertion point.")
        return False

    content = content.replace(search3, replace3)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_20_1_tests.js"
    output_filename = "svg_component_editor_v6_21_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.20.1)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.21.0)"""
    content = content.replace(search1, replace1)

    # 2. Add the actual API command ('flip_h') the main app expects to the shotgun cascade!
    search2 = r"""            const flipCommands = [['flipH'], ['rotate', 'flipH'], ['flip', 'H'], ['mirror', 'H'], ['mirrorH'], ['mirror', 'horizontal'], ['flip-h']];"""
    replace2 = r"""            const flipCommands = [['flip_h'], ['flipH'], ['rotate', 'flip_h'], ['flip', 'H'], ['mirror', 'H'], ['mirrorH'], ['mirror', 'horizontal'], ['flip-h']];"""
    
    if search2 not in content:
        print("⚠️ Error: Could not find the JS Test insertion point.")
        return False

    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.21.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.21.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")