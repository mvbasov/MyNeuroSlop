import os

def patch_file():
    input_filename = "svg_component_editor_v6_6_1.html"
    output_filename = "svg_component_editor_v6_7_0.html"

    if not os.path.exists(input_filename):
        print(f"Error: {input_filename} not found.")
        return

    with open(input_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Bump the application version
    search1 = r"""<div class="footer-right">v6.6.0</div>"""
    replace1 = r"""<div class="footer-right">v6.7.0</div>"""
    content = content.replace(search1, replace1)

    # 2. Inject the TEST_API Bridge and URL-Triggered Injector
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
                script.src = 'svg_component_editor_v6_7_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v6_7_0_tests.js");
                document.body.appendChild(script);
            }
        })();
    </script>"""
    
    content = content.replace(search2, replace2)

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully generated {output_filename}")

if __name__ == "__main__":
    patch_file()