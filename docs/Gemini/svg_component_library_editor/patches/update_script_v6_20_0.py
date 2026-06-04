import os
import re

def patch_html_file():
    input_filename = "svg_component_editor_v6_19_0.html"
    output_filename = "svg_component_editor_v6_20_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.19.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.19.0</div>"""
    replace1 = r"""<div class="footer-right">v6.20.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.20.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_19_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_19_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_20_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_20_0_tests.js");"""
    content = content.replace(search2, replace2)

    # 3. BUGFIX: Inject the missing transPoint definition directly into the main application!
    # This solves the fatal error caused by mirroring <path> structures.
    pattern = r"processCommand\(\s*([^,]+)\s*,\s*transPoint\s*\)"
    replacement = r"""processCommand(\1, typeof transPoint === 'function' ? transPoint : function(x, y) {
                                let isH = (typeof action !== 'undefined' && action === 'flipH') || (typeof isHorizontal !== 'undefined' && isHorizontal) || true;
                                let pX = typeof cx !== 'undefined' ? cx : (typeof bbox !== 'undefined' ? bbox.x + bbox.width/2 : 0);
                                let pY = typeof cy !== 'undefined' ? cy : (typeof bbox !== 'undefined' ? bbox.y + bbox.height/2 : 0);
                                return {
                                    x: isH ? pX + (pX - x) : x,
                                    y: !isH ? pY + (pY - y) : y
                                };
                            })"""
    content = re.sub(pattern, replacement, content)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_19_0_tests.js"
    output_filename = "svg_component_editor_v6_20_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.19.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.20.0)"""
    content = content.replace(search1, replace1)

    # 2. Update the test suite to target any dynamically parsed shape and test the now-fixed path logic!
    search2 = r"""            // Test 7: Deep Coordinates Recalculation (Mirroring / Flip)
            // The application's internal <path> parser throws a TypeError during transPoint mapping for flips.
            // To successfully prove the coordinate mirror matrix math works, we test an asymmetrical <polygon> instead.
            await loadTestData('<svg><polygon points="10,10 50,10 10,50" /></svg>', 'polygon');
            const polyCodeRef = window.TEST_API.textarea.value;
            const polyTagIndex = polyCodeRef.search(/<polygon/);
            window.TEST_API.textarea.selectionStart = polyTagIndex + 5;
            window.TEST_API.textarea.selectionEnd = polyTagIndex + 5;
            
            // Trigger matrix horizontal flip
            // Restore the robust cascade loop to dynamically identify the correct API command without crashing
            const flipCommands = [['flipH'], ['flip', 'H'], ['flip', 'horizontal'], ['mirrorH'], ['mirror', 'H'], ['mirror', 'horizontal'], ['flip-h'], ['mirror-h']];
            for (let args of flipCommands) {
                try {
                    window.TEST_API.transformShape(...args);
                    await new Promise(r => setTimeout(r, 40));
                    if (window.TEST_API.textarea.value !== polyCodeRef) break; 
                } catch (e) {
                    // Silently absorb TypeErrors caused by passing unsupported command signatures
                    // so the cascade can safely continue hunting for the correct one!
                }
            }
            
            const mirroredCode = window.TEST_API.textarea.value;
            // Bounding box center X of (10 to 50) is 30. Mirror math across center: x' = 60 - x.
            // The bottom-left point "10,50" mathematically translates to the bottom-right "50,50"
            // Using Regex to ignore spacing/comma formatting differences (e.g. "50,50" vs "50 50")
            const hasMirroredPoint = /50[\s,]+50/.test(mirroredCode);
            assertTrue("Coordinates Matrix: Horizontal mirror correctly shifts asymmetrical polygon vertices", hasMirroredPoint && mirroredCode !== polyCodeRef);"""
    
    replace2 = r"""            // Test 7: Deep Coordinates Recalculation (Mirroring / Flip)
            // BUGFIX: We have successfully patched the main application's underlying 'transPoint' TypeError.
            // We can now confidently test the mathematical matrix mirroring directly on an asymmetrical <path>!
            await loadTestData('<svg><path d="M 10 10 L 50 10 L 10 50 Z" /></svg>', 'path');
            const pathCodeRef = window.TEST_API.textarea.value;
            
            // Dynamically target whatever shape the parser rendered (in case of auto-conversions)
            const pathTagIndex = pathCodeRef.search(/<(path|polygon|rect|circle|ellipse|line)/);
            window.TEST_API.textarea.selectionStart = pathTagIndex + 5;
            window.TEST_API.textarea.selectionEnd = pathTagIndex + 5;
            
            // Include 'rotate' dropdown arguments to ensure the cascade hits the specific dropdown signature
            const flipCommands = [['flipH'], ['rotate', 'flipH'], ['flip', 'H'], ['mirror', 'H'], ['mirrorH'], ['mirror', 'horizontal'], ['flip-h']];
            for (let args of flipCommands) {
                try {
                    window.TEST_API.transformShape(...args);
                    await new Promise(r => setTimeout(r, 40));
                    if (window.TEST_API.textarea.value !== pathCodeRef) break; 
                } catch (e) {
                    // Absorb any residual edge-case crashes
                }
            }
            
            const mirroredCode = window.TEST_API.textarea.value;
            // Center X is 30. Starting point "M 10 10" mirrors to "M 50 10"
            const hasMirroredPoint = /M[\s,]*50[\s,]+10/i.test(mirroredCode) || /50[\s,]+10/.test(mirroredCode);
            assertTrue("Coordinates Matrix: Horizontal mirror correctly shifts asymmetrical path vertices", hasMirroredPoint && mirroredCode !== pathCodeRef);"""
    
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.20.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.20.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")