import sys
import os

def patch_file(input_filename, output_filename):
    if not os.path.exists(input_filename):
        print(f"Error: Could not find {input_filename}")
        return

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Define precise string replacements using raw strings (r''') to handle JS escapes safely
        replacements = [
            # 1. Update the insertShape function logic to precisely place <!-- and --> blocks
            (
                r'''                let template = shapeMap[type] || '';
                const code = textarea.value;
                let insertPos = textarea.selectionStart;
                
                if (activeTagInfo) {
                    const nonContainers = ['circle', 'line', 'path', 'polygon', 'polyline', 'rect', 'text', 'tspan', 'ellipse', 'image', 'use'];
                    if (nonContainers.includes(activeTagInfo.tagName.toLowerCase())) {
                        if (insertPos > activeTagInfo.start && insertPos < activeTagInfo.fullEnd) insertPos = activeTagInfo.fullEnd;
                    } else {
                        if (insertPos > activeTagInfo.start && insertPos < activeTagInfo.tagEnd) {
                            insertPos = activeTagInfo.tagEnd;
                        } else if (activeTagInfo.closeStart !== undefined && activeTagInfo.closeStart !== -1 && insertPos > activeTagInfo.closeStart && insertPos < activeTagInfo.fullEnd) {
                            insertPos = activeTagInfo.fullEnd;
                        }
                    }
                }
                
                const lineStart = code.lastIndexOf('\n', insertPos - 1);
                let indent = "\n  ";
                if (lineStart !== -1) {
                    const spaces = code.substring(lineStart + 1).match(/^\s*/);
                    if (spaces) indent = "\n" + spaces[0];
                }''',
                r'''                let template = shapeMap[type] || '';
                const code = textarea.value;
                let insertPos = textarea.selectionStart;
                let indent = "\n  ";
                
                if (type === 'comment_start' && activeTagInfo) {
                    const lineStart = code.lastIndexOf('\n', activeTagInfo.start - 1);
                    insertPos = lineStart === -1 ? 0 : lineStart + 1;
                    template = insertPos === 0 ? "<!--\n\n" : "\n<!--\n";
                    indent = "";
                } else if (type === 'comment_end' && activeTagInfo) {
                    insertPos = activeTagInfo.fullEnd;
                    template = "\n-->\n";
                    indent = "";
                } else {
                    if (activeTagInfo) {
                        const nonContainers = ['circle', 'line', 'path', 'polygon', 'polyline', 'rect', 'text', 'tspan', 'ellipse', 'image', 'use'];
                        if (nonContainers.includes(activeTagInfo.tagName.toLowerCase())) {
                            if (insertPos > activeTagInfo.start && insertPos < activeTagInfo.fullEnd) insertPos = activeTagInfo.fullEnd;
                        } else {
                            if (insertPos > activeTagInfo.start && insertPos < activeTagInfo.tagEnd) {
                                insertPos = activeTagInfo.tagEnd;
                            } else if (activeTagInfo.closeStart !== undefined && activeTagInfo.closeStart !== -1 && insertPos > activeTagInfo.closeStart && insertPos < activeTagInfo.fullEnd) {
                                insertPos = activeTagInfo.fullEnd;
                            }
                        }
                    }
                    
                    const lineStart = code.lastIndexOf('\n', insertPos - 1);
                    if (lineStart !== -1) {
                        const spaces = code.substring(lineStart + 1).match(/^\s*/);
                        if (spaces) indent = "\n" + spaces[0];
                    }
                }'''
            ),
            
            # 2. Increment the version logic per the rules
            (
                r'''<div class="footer-right">v6.1.0</div>''',
                r'''<div class="footer-right">v6.2.0</div>'''
            )
        ]
        
        # Apply Replacements
        for old_str, new_str in replacements:
            if old_str in content:
                content = content.replace(old_str, new_str)
            else:
                print(f"Warning: Could not find block starting with: {old_str[:40]}...")

        # Write output file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Successfully generated: {output_filename}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    input_file = 'svg_component_editor_v6_1_0.html'
    output_file = 'svg_component_editor_v6_2_0.html'
    patch_file(input_file, output_file)