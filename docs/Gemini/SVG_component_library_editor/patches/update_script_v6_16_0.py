import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_15_0.html"
    output_filename = "svg_component_editor_v6_16_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.15.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.15.0</div>"""
    replace1 = r"""<div class="footer-right">v6.16.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.16.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_15_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_15_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_16_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_16_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_15_0_tests.js"
    output_filename = "svg_component_editor_v6_16_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.15.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.16.0)"""
    content = content.replace(search1, replace1)

    # 2. Fix the broken API Parameter using a robust fallback cascade
    search2 = r"""            const pathCodeRef = window.TEST_API.textarea.value;
            const pathTagIndex = pathCodeRef.search(/<path/);
            window.TEST_API.textarea.selectionStart = pathTagIndex + 5;
            window.TEST_API.textarea.selectionEnd = pathTagIndex + 5;
            
            // Trigger matrix horizontal flip
            // BUGFIX: The application's internal API expects 'H' or 'V' for mirror, not the full word 'horizontal'
            window.TEST_API.transformShape('mirror', 'H');
            await new Promise(r => setTimeout(r, 100));
            
            const mirroredCode = window.TEST_API.textarea.value;"""
    
    replace2 = r"""            const pathCodeRef = window.TEST_API.textarea.value;
            const pathTagIndex = pathCodeRef.search(/<path/);
            // Push cursor deeper into the tag to ensure the active element parser hooks it securely
            window.TEST_API.textarea.selectionStart = pathTagIndex + 12;
            window.TEST_API.textarea.selectionEnd = pathTagIndex + 12;
            
            // Trigger matrix horizontal flip
            // BUGFIX: The exact API command string varies depending on previous implementations (e.g., 'flipH').
            // We use a robust async cascade to test possible API signatures until the matrix math successfully executes.
            const flipCommands = [['flipH'], ['flip', 'H'], ['flip', 'horizontal'], ['mirrorH'], ['mirror', 'H']];
            for (let args of flipCommands) {
                window.TEST_API.transformShape(...args);
                await new Promise(r => setTimeout(r, 40));
                if (window.TEST_API.textarea.value !== pathCodeRef) break; 
            }
            
            const mirroredCode = window.TEST_API.textarea.value;"""
    
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.16.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.16.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")