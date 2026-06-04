import os

html_file = 'svg_component_editor_v7_4_0.html'
new_html_file = 'svg_component_editor_v7_5_0.html'

test_file = 'svg_component_editor_v7_4_0_tests.js'
new_test_file = 'svg_component_editor_v7_5_0_tests.js'

# HTML Patching
if os.path.exists(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_replacements = [
        (
            r"""<div class="toolbar-divider"></div>
                    <button class="danger" id="tool-delete" title="Delete">🗑️</button>
                </div>""",
            r"""<div class="toolbar-divider"></div>
                    <button id="tool-uncomment" title="Uncomment" style="display: none;">🔓</button>
                    <button class="danger" id="tool-delete" title="Delete">🗑️</button>
                </div>"""
        ),
        (
            r"""document.getElementById('tool-delete').addEventListener('click', deleteActiveShape);""",
            r"""document.getElementById('tool-delete').addEventListener('click', deleteActiveShape);
                const uncommentBtn = document.getElementById('tool-uncomment');
                if (uncommentBtn) uncommentBtn.addEventListener('click', uncommentActiveShape);"""
        ),
        (
            r"""function deleteActiveShape() {
                if (!activeTagInfo) return;""",
            r"""function uncommentActiveShape() {
                if (!activeTagInfo || activeTagInfo.tagName !== '!--') return;
                const code = textarea.value;
                let start = activeTagInfo.start;
                let end = activeTagInfo.fullEnd;
                let commentStr = code.substring(start, end);
                
                let uncommented = commentStr.replace(/^<!--/, '').replace(/-->$/, '');
                const newCode = code.substring(0, start) + uncommented + code.substring(end);
                
                const savedScrollTop = textarea.scrollTop;
                const savedScrollLeft = textarea.scrollLeft;
                
                updateCode(newCode, true);
                textarea.focus();
                textarea.setSelectionRange(start, start + uncommented.length);
                textarea.scrollTop = savedScrollTop;
                textarea.scrollLeft = savedScrollLeft;
                
                if (selectionRafId) cancelAnimationFrame(selectionRafId);
                selectionRafId = requestAnimationFrame(updateSelection);
            }

            function deleteActiveShape() {
                if (!activeTagInfo) return;"""
        ),
        (
            r"""if (activeNode && activeSub) {
                    overlayTimeoutId = setTimeout(() => {
                        renderVisualOverlay(activeNode, activeSub);
                    }, 50);
                }
            }""",
            r"""if (activeNode && activeSub) {
                    overlayTimeoutId = setTimeout(() => {
                        renderVisualOverlay(activeNode, activeSub);
                    }, 50);
                }
                
                const uncommentBtn = document.getElementById('tool-uncomment');
                if (uncommentBtn) {
                    uncommentBtn.style.display = (activeTagInfo && activeTagInfo.tagName === '!--') ? 'flex' : 'none';
                }
            }"""
        ),
        (
            r"""deleteActiveShape,
                    SVGUtils,""",
            r"""deleteActiveShape,
                    uncommentActiveShape,
                    SVGUtils,"""
        ),
        (
            r"""<div class="footer-right">v7.4.0</div>""",
            r"""<div class="footer-right">v7.5.0</div>"""
        ),
        (
            r"""script.src = 'svg_component_editor_v7_4_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_4_0_tests.js");""",
            r"""script.src = 'svg_component_editor_v7_5_0_tests.js';
                script.onerror = () => console.error("Test suite not found: svg_component_editor_v7_5_0_tests.js");"""
        )
    ]

    for search_str, replace_str in html_replacements:
        html_content = html_content.replace(search_str, replace_str)

    with open(new_html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ Successfully patched and created {new_html_file}")
else:
    print(f"⚠️ HTML file {html_file} not found.")

# Test File Patching (To keep file names safely in sync)
if os.path.exists(test_file):
    with open(test_file, 'r', encoding='utf-8') as f:
        test_content = f.read()

    test_content = test_content.replace(
        r"""* SVG Component Editor - Micro Unit Test Suite (v7.4.0)""",
        r"""* SVG Component Editor - Micro Unit Test Suite (v7.5.0)"""
    )

    with open(new_test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    print(f"✅ Successfully patched and created {new_test_file}")
else:
    print(f"⚠️ Test file {test_file} not found. Skipping test file update.")