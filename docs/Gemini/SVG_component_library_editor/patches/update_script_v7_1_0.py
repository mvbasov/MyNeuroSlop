import os

def patch_html_file():
    input_filename = "svg_component_editor_v7_0_0.html"
    output_filename = "svg_component_editor_v7_1_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v7.0.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v7.0.0</div>"""
    replace1 = r"""<div class="footer-right">v7.1.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v7.1.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v7_0_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_0_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v7_1_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_1_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v7_0_0_tests.js"
    output_filename = "svg_component_editor_v7_1_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v7.0.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v7.1.0)"""
    content = content.replace(search1, replace1)

    # 2. Inject Test 9: Direct Coordinate Recalculation for Flips
    search2 = r"""                const newCode = window.TEST_API.textarea.value;
                const rewroteCoordinatesDirectly = !newCode.includes('transform=') && newCode !== origCode;
                assertTrue(`Direct Coordinates Rotation (${angle}°): Mathematically mapped vertices directly without transform matrix`, rewroteCoordinatesDirectly);
            }"""
    
    replace2 = r"""                const newCode = window.TEST_API.textarea.value;
                const rewroteCoordinatesDirectly = !newCode.includes('transform=') && newCode !== origCode;
                assertTrue(`Direct Coordinates Rotation (${angle}°): Mathematically mapped vertices directly without transform matrix`, rewroteCoordinatesDirectly);
            }

            // Test 9: Direct Coordinates Recalculation (Flips)
            // Validates that horizontal and vertical flips mathematically rewrite coordinates directly without appending a transform matrix.
            const flipsToTest = ['flip_h', 'flip_v'];
            for (let flipCmd of flipsToTest) {
                // Use an asymmetrical triangle to ensure flips are mathematically visible
                await loadTestData('<svg><polygon points="10,10 50,10 10,50" /></svg>', 'polygon');
                const origCode = window.TEST_API.textarea.value;
                
                const attrIdx = origCode.search(/points=/);
                window.TEST_API.textarea.selectionStart = attrIdx + 3;
                window.TEST_API.textarea.selectionEnd = attrIdx + 3;
                
                // Force synchronous state update to bypass debounce race conditions
                if (typeof window.TEST_API.getActiveTag === 'function') {
                    window.TEST_API.getActiveTag();
                }
                await new Promise(r => setTimeout(r, 10)); 
                
                const commands = [[flipCmd], ['mirror', flipCmd === 'flip_h' ? 'horizontal' : 'vertical'], [flipCmd === 'flip_h' ? 'flipH' : 'flipV']];
                for (let args of commands) {
                    try {
                        window.TEST_API.transformShape(...args);
                        await new Promise(r => setTimeout(r, 40));
                        if (window.TEST_API.textarea.value !== origCode) break;
                    } catch (e) {}
                }
                
                const newCode = window.TEST_API.textarea.value;
                const rewroteCoordinatesDirectly = !newCode.includes('transform=') && newCode !== origCode;
                const flipName = flipCmd === 'flip_h' ? 'Horizontal' : 'Vertical';
                assertTrue(`Direct Coordinates Flip (${flipName}): Mathematically mapped vertices directly without transform matrix`, rewroteCoordinatesDirectly);
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
    print("🚀 Starting v7.1.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v7.1.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")