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
            # 1. Update comment insertion to gracefully handle unclosed comment blocks (which swallow the rest of the file)
            (
                r'''                if (type === 'comment_start' && activeTagInfo) {
                    const lineStart = code.lastIndexOf('\n', activeTagInfo.start - 1);
                    insertPos = lineStart === -1 ? 0 : lineStart + 1;
                    template = "<!--\n";
                    indent = "";
                } else if (type === 'comment_end' && activeTagInfo) {
                    insertPos = activeTagInfo.fullEnd;
                    template = "\n-->";
                    indent = "";
                } else {''',
                r'''                if (type === 'comment_start') {
                    let refPos = textarea.selectionStart;
                    if (activeTagInfo && activeTagInfo.tagName !== '!--') refPos = activeTagInfo.start;
                    const lineStart = code.lastIndexOf('\n', refPos - 1);
                    insertPos = lineStart === -1 ? 0 : lineStart + 1;
                    template = "<!--\n";
                    indent = "";
                } else if (type === 'comment_end') {
                    if (activeTagInfo && activeTagInfo.tagName !== '!--') {
                        insertPos = activeTagInfo.fullEnd;
                    } else {
                        const lineEnd = code.indexOf('\n', textarea.selectionStart);
                        insertPos = lineEnd === -1 ? code.length : lineEnd;
                    }
                    template = "\n-->";
                    indent = "";
                } else {'''
            ),
            
            # 2. Increment the version logic per the rules
            (
                r'''<div class="footer-right">v6.3.0</div>''',
                r'''<div class="footer-right">v6.4.0</div>'''
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
    input_file = 'svg_component_editor_v6_3_0.html'
    output_file = 'svg_component_editor_v6_4_0.html'
    patch_file(input_file, output_file)