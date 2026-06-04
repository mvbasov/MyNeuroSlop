import os

def patch_html_file():
    # Detect which HTML version is currently in the folder
    is_from_661 = False
    if os.path.exists("svg_component_editor_v6_7_0.html"):
        input_filename = "svg_component_editor_v6_7_0.html"
    elif os.path.exists("svg_component_editor_v6_6_1.html"):
        input_filename = "svg_component_editor_v6_6_1.html"
        is_from_661 = True
    else:
        print("⚠️ Error: Neither v6.6.1 nor v6.7.0 HTML files found.")
        return False

    output_filename = "svg_component_editor_v6_8_0.html"

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    if is_from_661:
        # 1. Bump the application version in the footer (from 6.6.0 display)
        search1 = r"""<div class="footer-right">v6.6.0</div>"""
        replace1 = r"""<div class="footer-right">v6.8.0</div>"""
        content = content.replace(search1, replace1)

        # 2. Inject the TEST_API Bridge for the first time
        search2 = r"""                reader.readAsText(file);
                event.target.value = ''; 
            }
        })();
    </script>"""
        
        replace2 = r"""                reader.readAsText(file);
                event.target.value = ''; 
            }

            // --- Micro Unit Test System Bridge ---
            // Only activates if ?test= is present in the URL
            if (window.location.search.includes('test=')) {
                window.TEST_API = {
                    textarea,
                    userSvgContainer,
                    errorBadge,
                    updateCode,
                    undo,
                    redo,
                    insertShape,
                    moveShape,
                    transformShape,
                    deleteActiveShape,
                    SVGUtils,
                    getActiveTag,
                    backdrop
                };
                
                const script = document.createElement('script');
                script.src = 'svg_component_editor_v6_8_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_8_0_tests.js");
                document.body.appendChild(script);
            }
        })();
    </script>"""
        content = content.replace(search2, replace2)
    else:
        # Upgrade safely from 6.7.0
        search1 = r"""<div class="footer-right">v6.7.0</div>"""
        replace1 = r"""<div class="footer-right">v6.8.0</div>"""
        content = content.replace(search1, replace1)

        search2 = r"""                script.src = 'svg_component_editor_v6_7_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_7_0_tests.js");"""
        
        replace2 = r"""                script.src = 'svg_component_editor_v6_8_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_8_0_tests.js");"""
        content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated HTML: {output_filename}")
    return True


def patch_js_file():
    input_filename = "svg_component_editor_v6_7_0_tests.js"
    output_filename = "svg_component_editor_v6_8_0_tests.js"

    if not os.path.exists(input_filename):
        print(f"⚠️ Error: {input_filename} not found.")
        return False

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the version in the header comment
    search1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.7.0)"""
    replace1 = r""" * SVG Component Editor - Micro Unit Test Suite (v6.8.0)"""
    content = content.replace(search1, replace1)

    # 2. Update the console.table output to include symbols
    search2 = r"""        // Execution Summary
        console.table({ Passed: passed, Failed: failed, Total: passed + failed });"""
    
    replace2 = r"""        // Execution Summary
        console.table({ '✅ Passed': passed, '❌ Failed': failed, '📊 Total': passed + failed });"""
    
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Successfully generated JS Test Suite: {output_filename}")
    return True


if __name__ == "__main__":
    print("🚀 Starting v6.8.0 Full Fileset Patch Process...\n")
    html_success = patch_html_file()
    js_success = patch_js_file()
    
    if html_success and js_success:
        print("\n🎉 Full v6.8.0 fileset upgraded successfully!")
    else:
        print("\n⚠️ Process finished, but some files were missing. Check the errors above.")