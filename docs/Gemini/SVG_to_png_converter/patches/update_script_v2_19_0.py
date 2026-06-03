import os

# Target the previous v2.18.0 file
file_path = "svg_to_png_converter_v2_18_0.html"
output_filename = "svg_to_png_converter_v2_19_0.html"

with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# 1. Update formatXML to prevent collapsing structural SVG tags
search_format = r"""                        const hasChildElements = Array.from(node.childNodes).some(n => n.nodeType === Node.ELEMENT_NODE);
                        if (hasChildElements) {
                            str += '>\n';
                            indentLevel++;
                            for (let i = 0; i < node.childNodes.length; i++) str += serializeNode(node.childNodes[i]);
                            indentLevel--;
                            str += indent + '</' + node.tagName + '>\n';
                        } else if (node.textContent.trim()) {
                            str += '>' + node.textContent.trim() + '</' + node.tagName + '>\n';
                        } else {
                            str += '/>\n';
                        }"""

replace_format = r"""                        const hasChildElements = Array.from(node.childNodes).some(n => n.nodeType === Node.ELEMENT_NODE);
                        const keepExpanded = ['svg', 'g', 'defs', 'style', 'text', 'clipPath', 'mask'];
                        if (hasChildElements) {
                            str += '>\n';
                            indentLevel++;
                            for (let i = 0; i < node.childNodes.length; i++) str += serializeNode(node.childNodes[i]);
                            indentLevel--;
                            str += indent + '</' + node.tagName + '>\n';
                        } else if (node.textContent.trim() || keepExpanded.includes(node.tagName.toLowerCase())) {
                            str += '>' + node.textContent.trim() + '</' + node.tagName + '>\n';
                        } else {
                            str += '/>\n';
                        }"""

# 2. Bump the Version
search_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.18.0</span>"""
replace_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.19.0</span>"""

# Apply Replacements
updated_content = html_content.replace(search_format, replace_format)
updated_content = updated_content.replace(search_version, replace_version)

with open(output_filename, "w", encoding="utf-8") as file:
    file.write(updated_content)

print(f"Patch successfully applied! Saved as {output_filename}")