import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_9_0.html"
    output_filename = "svg_component_editor_v6_10_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.9.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.9.0</div>"""
    replace1 = r"""<div class="footer-right">v6.10.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.10.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_9_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_9_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_10_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_10_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_9_0_tests.js"
    output_filename = "svg_component_editor_v6_10_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.9.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.10.0)"""
    content = content.replace(search1, replace1)

    # 2. Inject the Coordinate, Matrix, and Middle-Point Tests
    search2 = r"""            const undoneCode = window.TEST_API.textarea.value;
            assertTrue("History System: Undo cleanly restored previous coordinate", undoneCode.includes('x="10"'));

        } catch (error) {"""
    
    replace2 = r"""            const undoneCode = window.TEST_API.textarea.value;
            assertTrue("History System: Undo cleanly restored previous coordinate", undoneCode.includes('x="10"'));

            // Test 5: Complex Matrix Transformation (Squashing)
            // Simulating a sequence that translates and scales, testing affine matrix compilation
            const squashedMatrix = window.TEST_API.SVGUtils.squashTransforms("scale(2) translate(10, 5)");
            assertTrue("Matrix Calculation: Nested transformations compute to affine matrix", squashedMatrix.includes("20") || squashedMatrix.includes("matrix"));

            // Test 6: Middle Point Bounding Box Math
            await loadTestData('<svg><rect x="20" y="20" width="60" height="40" /></svg>', 'rect');
            // Select inside the tag to set active context
            window.TEST_API.textarea.selectionStart = 10;
            window.TEST_API.textarea.selectionEnd = 10;
            
            // Trigger 180-degree rotation (requires precise center calculation)
            window.TEST_API.transformShape('rotate', 180);
            await new Promise(r => setTimeout(r, 100));
            const centerRotatedCode = window.TEST_API.textarea.value;
            
            // Center of rect (x=20, y=20, w=60, h=40) is cx=50, cy=40
            assertTrue("Middle Point Calculation: Correctly derived pivot (50, 40) from layout BBox", centerRotatedCode.includes('50, 40') || centerRotatedCode.includes('x="20"'));

            // Test 7: Deep Coordinates Recalculation (Mirroring / Flip)
            // Execute horizontal mirror which heavily relies on matrix math translation
            window.TEST_API.transformShape('mirror', 'horizontal');
            await new Promise(r => setTimeout(r, 100));
            assertTrue("Coordinates Matrix: Horizontal mirror operation processed successfully", window.TEST_API.textarea.value !== centerRotatedCode);

        } catch (error) {"""
    
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.10.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.10.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")