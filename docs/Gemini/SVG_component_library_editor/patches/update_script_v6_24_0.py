import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_23_0.html"
    output_filename = "svg_component_editor_v6_24_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.23.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.23.0</div>"""
    replace1 = r"""<div class="footer-right">v6.24.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.24.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_23_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_23_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_24_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_24_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_23_0_tests.js"
    output_filename = "svg_component_editor_v6_24_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.23.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.24.0)"""
    content = content.replace(search1, replace1)

    # 2. Inject Test 8: Direct Coordinate Recalculation (-45, 45, 180)
    search2 = r"""            const hasMirroredPoint = /50[\s,]+50/.test(mirroredCode);
            assertTrue("Coordinates Matrix: Horizontal mirror correctly shifts asymmetrical polygon vertices", hasMirroredPoint && mirroredCode !== polyCodeRef);"""
    
    replace2 = r"""            const hasMirroredPoint = /50[\s,]+50/.test(mirroredCode);
            assertTrue("Coordinates Matrix: Horizontal mirror correctly shifts asymmetrical polygon vertices", hasMirroredPoint && mirroredCode !== polyCodeRef);

            // Test 8: Direct Coordinates Recalculation (Rotations 45, -45, 180)
            // Validates that rotating geometric shapes by specific angles recalculates points mathematically instead of appending a lazy 'transform="..."' attribute.
            const anglesToTest = ['45', '-45', '180'];
            for (let angle of anglesToTest) {
                await loadTestData('<svg><polygon points="40,40 60,40 60,60 40,60" /></svg>', 'polygon');
                const origCode = window.TEST_API.textarea.value;
                
                // Target parser exactly into the polygon tag payload
                const pIdx = origCode.search(/<polygon/);
                window.TEST_API.textarea.selectionStart = pIdx + 8;
                window.TEST_API.textarea.selectionEnd = pIdx + 8;
                
                // Fire shotgun API cascade for the rotation command
                const commands = [[`rot_${angle}`], ['rotate', angle], [angle], [Number(angle)], [`rotate_${angle}`]];
                for (let args of commands) {
                    try {
                        window.TEST_API.transformShape(...args);
                        await new Promise(r => setTimeout(r, 40));
                        if (window.TEST_API.textarea.value !== origCode) break;
                    } catch (e) {}
                }
                
                const newCode = window.TEST_API.textarea.value;
                const rewroteCoordinatesDirectly = !newCode.includes('transform=') && newCode !== origCode;
                assertTrue(`Direct Coordinates Rotation (${angle}°): Mathematically mapped vertices directly without transform matrix`, rewroteCoordinatesDirectly);
            }"""
    
    if search2 not in content:
        print("⚠️ Error: Could not find the JS Test insertion point.")
        return False

    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.24.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.24.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")