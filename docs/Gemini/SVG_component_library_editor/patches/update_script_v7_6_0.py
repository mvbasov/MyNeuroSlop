import os

html_file = 'svg_component_editor_v7_5_0.html'
new_html_file = 'svg_component_editor_v7_6_0.html'

test_file = 'svg_component_editor_v7_5_0_tests.js'
new_test_file = 'svg_component_editor_v7_6_0_tests.js'

# HTML Patching
if os.path.exists(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    html_replacements = [
        (
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
            }""",
            r"""function uncommentActiveShape() {
                if (!activeTagInfo || activeTagInfo.tagName !== '!--') return;
                const code = textarea.value;
                let start = activeTagInfo.start;
                let end = activeTagInfo.fullEnd;
                
                let tempStart = start;
                while (tempStart > 0 && (code[tempStart - 1] === ' ' || code[tempStart - 1] === '\t')) tempStart--;
                let startIsOnEmptyLine = (tempStart === 0 || code[tempStart - 1] === '\n');
                
                let tempEnd = end;
                while (tempEnd < code.length && (code[tempEnd] === ' ' || code[tempEnd] === '\t')) tempEnd++;
                let endIsOnEmptyLine = (tempEnd === code.length || code[tempEnd] === '\n' || code[tempEnd] === '\r');

                let innerContent = code.substring(start, end).replace(/^<!--/, '').replace(/-->$/, '');
                
                let trimStart = startIsOnEmptyLine && /^[ \t]*\r?\n/.test(innerContent);
                let trimEnd = endIsOnEmptyLine && /\r?\n[ \t]*$/.test(innerContent);
                
                // Eradicate the block entirely if it was an empty comment spanning lines
                if (trimStart && trimEnd && /^[ \t]*\r?\n[ \t]*$/.test(innerContent)) {
                    innerContent = '';
                    start = tempStart;
                    end = tempEnd;
                } else {
                    if (trimStart) {
                        innerContent = innerContent.replace(/^[ \t]*\r?\n/, '');
                        start = tempStart; 
                    }
                    if (trimEnd) {
                        innerContent = innerContent.replace(/\r?\n[ \t]*$/, '');
                        end = tempEnd;
                    }
                }
                
                const newCode = code.substring(0, start) + innerContent + code.substring(end);
                
                const savedScrollTop = textarea.scrollTop;
                const savedScrollLeft = textarea.scrollLeft;
                
                updateCode(newCode, true);
                textarea.focus();
                textarea.setSelectionRange(start, start + innerContent.length);
                textarea.scrollTop = savedScrollTop;
                textarea.scrollLeft = savedScrollLeft;
                
                if (selectionRafId) cancelAnimationFrame(selectionRafId);
                selectionRafId = requestAnimationFrame(updateSelection);
            }"""
        ),
        (
            r"""<div class="footer-right">v7.5.0</div>""",
            r"""<div class="footer-right">v7.6.0</div>"""
        )
    ]

    for search_str, replace_str in html_replacements:
        html_content = html_content.replace(search_str, replace_str)

    with open(new_html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ Successfully patched and created {new_html_file}")
else:
    print(f"⚠️ HTML file {html_file} not found. Ensure you generated v7.5.0 first.")

# Test File Patching
if os.path.exists(test_file):
    with open(test_file, 'r', encoding='utf-8') as f:
        test_content = f.read()

    test_content = test_content.replace(
        r"""* SVG Component Editor - Micro Unit Test Suite (v7.5.0)""",
        r"""* SVG Component Editor - Micro Unit Test Suite (v7.6.0)"""
    )

    with open(new_test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    print(f"✅ Successfully patched and created {new_test_file}")
else:
    print(f"⚠️ Test file {test_file} not found. Skipping test file update.")