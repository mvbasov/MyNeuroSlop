import os

def patch_html_file():
    input_filename = "svg_component_editor_v6_18_0.html"
    output_filename = "svg_component_editor_v6_19_0.html"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found. Ensure you are upgrading from v6.18.0.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version in the footer
    search1 = r"""<div class="footer-right">v6.18.0</div>"""
    replace1 = r"""<div class="footer-right">v6.19.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Point to the new v6.19.0 test suite file
    search2 = r"""                script.src = 'svg_component_editor_v6_18_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_18_0_tests.js");"""
    
    replace2 = r"""                script.src = 'svg_component_editor_v6_19_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_19_0_tests.js");"""
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_18_0_tests.js"
    output_filename = "svg_component_editor_v6_19_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.18.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.19.0)"""
    content = content.replace(search1, replace1)

    # 2. Make the API cascade shotgun "recoil-proof" by absorbing internal TypeErrors
    search2 = r"""            const flipCommands = [['flipH'], ['flip', 'H'], ['flip', 'horizontal'], ['mirrorH'], ['mirror', 'H'], ['mirror', 'horizontal'], ['flip-h'], ['mirror-h']];
            for (let args of flipCommands) {
                window.TEST_API.transformShape(...args);
                await new Promise(r => setTimeout(r, 40));
                if (window.TEST_API.textarea.value !== polyCodeRef) break; 
            }"""
    
    replace2 = r"""            const flipCommands = [['flipH'], ['flip', 'H'], ['flip', 'horizontal'], ['mirrorH'], ['mirror', 'H'], ['mirror', 'horizontal'], ['flip-h'], ['mirror-h']];
            for (let args of flipCommands) {
                try {
                    window.TEST_API.transformShape(...args);
                    await new Promise(r => setTimeout(r, 40));
                    if (window.TEST_API.textarea.value !== polyCodeRef) break; 
                } catch (e) {
                    // Silently absorb TypeErrors caused by passing unsupported command signatures
                    // so the cascade can safely continue hunting for the correct one!
                }
            }"""
    
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.19.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.19.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")