import sys
import os

def patch_file(input_filename, output_filename):
    if not os.path.exists(input_filename):
        print(f"Error: Could not find {input_filename}")
        return

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Define precise string replacements
        replacements = [
            # 1. Update the UI Dropdown to include comment markers
            (
                '''                        <option value="text">🔤 Text</option>
                    </select>''',
                '''                        <option value="text">🔤 Text</option>
                        <option value="comment_start">💬 &lt;!--</option>
                        <option value="comment_end">💬 --&gt;</option>
                    </select>'''
            ),
            
            # 2. Add comment templates to the insertShape function map
            (
                '''                    'rect': `<rect x="10" y="10" width="80" height="80" />`,
                    'text': `<text x="50" y="50" font-family="sans-serif" font-size="14" text-anchor="middle">Text</text>`
                };''',
                '''                    'rect': `<rect x="10" y="10" width="80" height="80" />`,
                    'text': `<text x="50" y="50" font-family="sans-serif" font-size="14" text-anchor="middle">Text</text>`,
                    'comment_start': `<!-- `,
                    'comment_end': ` -->`
                };'''
            ),
            
            # 3. Upgrade the state-machine parser to emit multiline comments as trackable blocks
            (
                '''                    if (state === 'TEXT') {
                        if (char === '<') {
                            if (html.substring(i, i + 4) === '<!--') {
                                state = 'IN_COMMENT';
                                i += 3;
                            } else {
                                state = 'IN_TAG';
                                currentStart = i;
                            }
                        }
                    } else if (state === 'IN_COMMENT') {
                        if (char === '-' && html.substring(i, i + 3) === '-->') {
                            state = 'TEXT';
                            i += 2;
                        }
                    } else if (state === 'IN_TAG') {''',
                '''                    if (state === 'TEXT') {
                        if (char === '<') {
                            if (html.substring(i, i + 4) === '<!--') {
                                state = 'IN_COMMENT';
                                currentStart = i;
                                i += 3;
                            } else {
                                state = 'IN_TAG';
                                currentStart = i;
                            }
                        }
                    } else if (state === 'IN_COMMENT') {
                        if (char === '-' && html.substring(i, i + 3) === '-->') {
                            state = 'TEXT';
                            let el = {
                                domIndex: -1,
                                start: currentStart,
                                effectiveStart: currentStart,
                                tagEnd: i + 3,
                                fullEnd: i + 3,
                                closeStart: -1,
                                tagName: '!--'
                            };
                            elements.push(el);
                            i += 2;
                        }
                    } else if (state === 'IN_TAG') {'''
            ),
            
            # 4. Handle unclosed comment blocks at the end of the file safely
            (
                '''                // Close unclosed tags implicitly at end of document
                for (let s of stack) {
                    s.fullEnd = html.length;
                    s.closeStart = html.length;
                }''',
                '''                // Close unclosed tags implicitly at end of document
                for (let s of stack) {
                    s.fullEnd = html.length;
                    s.closeStart = html.length;
                }
                if (state === 'IN_COMMENT') {
                    elements.push({
                        domIndex: -1,
                        start: currentStart,
                        effectiveStart: currentStart,
                        tagEnd: html.length,
                        fullEnd: html.length,
                        closeStart: -1,
                        tagName: '!--'
                    });
                }'''
            ),
            
            # 5. Increment the version logic per the rules
            (
                '''<div class="footer-right">v6.0.0</div>''',
                '''<div class="footer-right">v6.1.0</div>'''
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
    input_file = 'svg_component_editor_v6_0_0.html'
    output_file = 'svg_component_editor_v6_1_0.html'
    patch_file(input_file, output_file)