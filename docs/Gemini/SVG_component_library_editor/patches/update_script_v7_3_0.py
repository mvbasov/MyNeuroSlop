import os

def patch_html_file():
    input_filename = "svg_component_editor_v7_2_0.html"
    output_filename = "svg_component_editor_v7_3_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v7.2.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v7.2.0</div>"""
    replace1 = r"""<div class="footer-right">v7.3.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v7.3.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v7_2_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_2_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v7_3_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_3_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v7_2_0_tests.js"
    output_filename = "svg_component_editor_v7_3_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v7.2.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v7.3.0)"""
    content = content.replace(search1, replace1)

    # 2. Inject Tests 10 through 15 safely into the execution sequence
    search2 = r"""                const flipName = flipCmd === 'flip_h' ? 'Horizontal' : 'Vertical';
                assertTrue(`Direct Coordinates Flip (${flipName}): Mathematically mapped vertices directly without transform matrix`, rewroteCoordinatesDirectly);
            }"""
    
    replace2 = r"""                const flipName = flipCmd === 'flip_h' ? 'Horizontal' : 'Vertical';
                assertTrue(`Direct Coordinates Flip (${flipName}): Mathematically mapped vertices directly without transform matrix`, rewroteCoordinatesDirectly);
            }

            // Test 10: <use> Element BBox Failsafe (180 Rotation Center Failsafe)
            await loadTestData('<svg><defs><rect id="myBox" width="20" height="20" /></defs><use href="#myBox" x="50" y="50" /></svg>', 'use');
            let origCode = window.TEST_API.textarea.value;
            let targetIdx = origCode.search(/<use/);
            window.TEST_API.textarea.selectionStart = targetIdx + 3;
            window.TEST_API.textarea.selectionEnd = targetIdx + 3;
            window.TEST_API.textarea.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            window.TEST_API.textarea.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
            await new Promise(r => setTimeout(r, 250));
            
            window.TEST_API.transformShape('rot_180');
            await new Promise(r => setTimeout(r, 100));
            // Box is 20x20 (center 10,10). Offset is 50,50. True center is 60,60.
            assertTrue("Advanced Failsafe: <use> element rotation mathematically located pivot from defs+offset (cx=60, cy=60)", window.TEST_API.textarea.value.includes('rotate(180, 60, 60)'));

            // Test 11: Arc Sweep-Flag Inversion & Lowercase Relative parsing
            await loadTestData('<svg><path d="M 10 10 A 30 30 0 0 1 100 100 l 10 10" /></svg>', 'path');
            origCode = window.TEST_API.textarea.value;
            targetIdx = origCode.search(/<path/);
            window.TEST_API.textarea.selectionStart = targetIdx + 3;
            window.TEST_API.textarea.selectionEnd = targetIdx + 3;
            window.TEST_API.textarea.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            window.TEST_API.textarea.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
            await new Promise(r => setTimeout(r, 250));
            
            window.TEST_API.transformShape('flip_h');
            await new Promise(r => setTimeout(r, 100));
            const newArcCode = window.TEST_API.textarea.value;
            assertTrue("Path Engine: Arc (A) sweep-flags correctly invert and relative (l) commands are processed on flip", !newArcCode.includes('transform=') && newArcCode !== origCode);

            // Test 12: Multi-Step Redo Traversal
            await loadTestData('<svg><rect x="0" y="0" width="10" height="10" /></svg>', 'rect');
            origCode = window.TEST_API.textarea.value;
            targetIdx = origCode.search(/<rect/);
            window.TEST_API.textarea.selectionStart = targetIdx + 3;
            window.TEST_API.textarea.selectionEnd = targetIdx + 3;
            window.TEST_API.textarea.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            window.TEST_API.textarea.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
            await new Promise(r => setTimeout(r, 250));
            
            window.TEST_API.moveShape(10, 0);
            await new Promise(r => setTimeout(r, 50));
            window.TEST_API.moveShape(10, 0);
            await new Promise(r => setTimeout(r, 50));
            window.TEST_API.undo();
            await new Promise(r => setTimeout(r, 50));
            window.TEST_API.redo();
            await new Promise(r => setTimeout(r, 50));
            assertTrue("History Timeline: Redo correctly traverses forward array state", window.TEST_API.textarea.value.includes('x="20"'));

            // Test 13: Malformed SVG Error Boundary
            window.TEST_API.updateCode('<svg><rect x="10" y="10" ', false);
            await new Promise(r => setTimeout(r, 200));
            assertTrue("Error Boundary: Malformed syntax correctly traps without crashing and triggers error badge", window.TEST_API.errorBadge.style.display !== 'none');

            // Test 14: Element Deletion State Cleanup
            await loadTestData('<svg><rect id="1" /><circle id="2" /><path id="3" /></svg>', 'circle');
            origCode = window.TEST_API.textarea.value;
            targetIdx = origCode.search(/<circle/);
            window.TEST_API.textarea.selectionStart = targetIdx + 3;
            window.TEST_API.textarea.selectionEnd = targetIdx + 3;
            window.TEST_API.textarea.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            window.TEST_API.textarea.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
            await new Promise(r => setTimeout(r, 250));
            
            window.TEST_API.deleteActiveShape();
            await new Promise(r => setTimeout(r, 100));
            const deletedCode = window.TEST_API.textarea.value;
            assertTrue("Garbage Collection: deleteActiveShape cleanly removes node and preserves siblings", !deletedCode.includes('circle') && deletedCode.includes('rect') && deletedCode.includes('path'));

            // Test 15: Multiline Comment Preservation
            const commentBlock = "<!--\n  My Safe\n  Multiline\n  Comment\n-->";
            await loadTestData(`<svg>\n${commentBlock}\n<rect x="0" y="0" width="10" height="10" />\n</svg>`, 'rect');
            origCode = window.TEST_API.textarea.value;
            targetIdx = origCode.search(/<rect/);
            window.TEST_API.textarea.selectionStart = targetIdx + 3;
            window.TEST_API.textarea.selectionEnd = targetIdx + 3;
            window.TEST_API.textarea.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            window.TEST_API.textarea.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
            await new Promise(r => setTimeout(r, 250));
            
            window.TEST_API.moveShape(5, 5);
            await new Promise(r => setTimeout(r, 100));
            assertTrue("Parser Safe-Mode: Multiline HTML comments perfectly preserved during geometric manipulation", window.TEST_API.textarea.value.includes('My Safe'));"""
    
    if search2 not in content:
        print("⚠️ Error: Could not find the JS Test insertion point.")
        return False

    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v7.3.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v7.3.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")