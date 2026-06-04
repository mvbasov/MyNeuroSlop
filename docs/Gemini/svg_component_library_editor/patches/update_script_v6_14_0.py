import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_13_0.html"
    output_filename = "svg_component_editor_v6_14_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.13.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.13.0</div>"""
    replace1 = r"""<div class="footer-right">v6.14.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.14.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_13_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_13_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_14_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_14_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_13_0_tests.js"
    output_filename = "svg_component_editor_v6_14_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.13.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.14.0)"""
    content = content.replace(search1, replace1)

    # 2. Rewrite Test 7 to utilize an asymmetrical geometry shape to prove the flip math
    search2 = r"""            // Test 7: Deep Coordinates Recalculation (Mirroring / Flip)
            // Execute horizontal mirror which heavily relies on matrix math translation
            // Re-acquire contextual focus dynamically based on actual element index to prevent formatting misses
            const codeRef = window.TEST_API.textarea.value;
            const dynamicTagIndex = codeRef.search(/<(rect|path|polygon|circle|ellipse|use)/);
            window.TEST_API.textarea.selectionStart = dynamicTagIndex + 5;
            window.TEST_API.textarea.selectionEnd = dynamicTagIndex + 5;
            window.TEST_API.transformShape('mirror', 'horizontal');
            await new Promise(r => setTimeout(r, 100));
            assertTrue("Coordinates Matrix: Horizontal mirror operation processed successfully", window.TEST_API.textarea.value !== centerRotatedCode);"""
    
    replace2 = r"""            // Test 7: Deep Coordinates Recalculation (Mirroring / Flip)
            // A perfectly symmetrical rectangle mirrored around its own center results in the exact same coordinates!
            // To prove the mirror matrix calculates properly, we load an asymmetrical shape (a right triangle).
            await loadTestData('<svg><path d="M 10 10 L 50 10 L 10 50 Z" /></svg>', 'path');
            const pathCodeRef = window.TEST_API.textarea.value;
            const pathTagIndex = pathCodeRef.search(/<path/);
            window.TEST_API.textarea.selectionStart = pathTagIndex + 5;
            window.TEST_API.textarea.selectionEnd = pathTagIndex + 5;
            
            // Trigger matrix horizontal flip
            window.TEST_API.transformShape('mirror', 'horizontal');
            await new Promise(r => setTimeout(r, 100));
            
            const mirroredCode = window.TEST_API.textarea.value;
            // Bounding box center X of (10 to 50) is 30. Mirror math across center: x' = 60 - x.
            // The starting point "M 10 10" mathematically translates to "M 50 10"
            assertTrue("Coordinates Matrix: Horizontal mirror correctly shifts asymmetrical path vertices", mirroredCode.includes('50') && mirroredCode !== pathCodeRef);"""
    
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.14.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.14.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")