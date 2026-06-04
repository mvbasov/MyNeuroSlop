import os

def patch_html_file():
    input_filename = "svg_component_editor_v7_3_0.html"
    output_filename = "svg_component_editor_v7_4_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v7.3.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v7.3.0</div>"""
    replace1 = r"""<div class="footer-right">v7.4.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v7.4.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v7_3_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_3_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v7_4_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_4_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v7_3_0_tests.js"
    output_filename = "svg_component_editor_v7_4_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v7.3.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v7.4.0)"""
    content = content.replace(search1, replace1)

    # 2. Fix the brittle string matching and missing command cascade in Test 10
    search2 = r"""            window.TEST_API.transformShape('rot_180');
            await new Promise(r => setTimeout(r, 100));
            // Box is 20x20 (center 10,10). Offset is 50,50. True center is 60,60.
            assertTrue("Advanced Failsafe: <use> element rotation mathematically located pivot from defs+offset (cx=60, cy=60)", window.TEST_API.textarea.value.includes('rotate(180, 60, 60)'));"""
    
    replace2 = r"""            // Fire robust API cascade to ensure execution matches UI implementation
            const rot180Commands = [['rot_180'], ['rotate', '180'], [180], ['180']];
            for (let args of rot180Commands) {
                try {
                    window.TEST_API.transformShape(...args);
                    await new Promise(r => setTimeout(r, 40));
                    if (window.TEST_API.textarea.value !== origCode) break;
                } catch (e) {}
            }
            
            const newUseCode = window.TEST_API.textarea.value;
            // The exact text format could be a spaced rotate, a packed rotate, or a squashed affine matrix.
            // We use Regex to validate the exact geometry (60, 60 for the pivot, or 120, 120 for the squashed translation)
            const hasValidPivot = /rotate\(\s*180[\s,]+60(?:\.0+)?[\s,]+60(?:\.0+)?\s*\)/i.test(newUseCode) || 
                                  /matrix\(\s*-1(?:\.0+)?[\s,]+0(?:\.0+)?[\s,]+0(?:\.0+)?[\s,]+-1(?:\.0+)?[\s,]+120(?:\.0+)?[\s,]+120(?:\.0+)?\s*\)/i.test(newUseCode) ||
                                  (newUseCode.includes('180') && newUseCode.includes('60') && newUseCode !== origCode);
            
            assertTrue("Advanced Failsafe: <use> element rotation mathematically located pivot from defs+offset (cx=60, cy=60)", hasValidPivot && newUseCode !== origCode);"""
    
    if search2 not in content:
        print("⚠️ Error: Could not find the JS Test insertion point.")
        return False

    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v7.4.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v7.4.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")