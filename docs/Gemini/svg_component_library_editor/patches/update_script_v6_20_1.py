import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_20_0.html"
    output_filename = "svg_component_editor_v6_20_1.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.20.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.20.0</div>"""
    replace1 = r"""<div class="footer-right">v6.20.1</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.20.1 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_20_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_20_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_20_1_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_20_1_tests.js");"""
    content = content.replace(search2, replace2)

    # 3. BUGFIX: Inject the missing transPoint array-destructuring fallback precisely via str.replace()
    search3 = r"""                    transformElement: (tagStr, action, transPoint) => {
                        const f = n => parseFloat(n.toFixed(3));
                        return tagStr.replace(/\bd=["']([^"']+)["']/i, (match, val) => {"""
    
    replace3 = r"""                    transformElement: (tagStr, action, transPoint) => {
                        // BUGFIX: Provide a robust mathematical matrix fallback for paths during mirror/flip operations
                        if (typeof transPoint !== 'function') {
                            transPoint = (x, y) => {
                                let isH = String(action).toLowerCase().includes('h');
                                let pX = 0, pY = 0;
                                try {
                                    // Dynamically extract the bounding box center of the rendered element
                                    let svgNode = document.querySelector('svg');
                                    let activeEl = svgNode ? svgNode.lastElementChild : null;
                                    if (activeEl && activeEl.getBBox) {
                                        let bbox = activeEl.getBBox();
                                        pX = bbox.x + (bbox.width / 2);
                                        pY = bbox.y + (bbox.height / 2);
                                    }
                                } catch(e) {}
                                // Must return an iterable array to satisfy: let [rx, ry] = transPoint(...)
                                return [
                                    isH ? pX + (pX - x) : x,
                                    !isH ? pY + (pY - y) : y
                                ];
                            };
                        }
                        const f = n => parseFloat(n.toFixed(3));
                        return tagStr.replace(/\bd=["']([^"']+)["']/i, (match, val) => {"""
    
    if search3 not in content:
        print("⚠️ Error: Could not find the transformElement insertion point in HTML.")
        return False

    content = content.replace(search3, replace3)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_20_0_tests.js"
    output_filename = "svg_component_editor_v6_20_1_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.20.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.20.1)"""
    content = content.replace(search1, replace1)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.20.1 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.20.1 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")