import os

file_name = "svg_theme_experimenter_v1_10_0.html"
new_file_name = "svg_theme_experimenter_v1_11_0.html"

try:
    with open(file_name, "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print(f"Error: Could not find {file_name}. Ensure you run this script in the same directory as the file.")
    exit(1)

# Normalize line endings to avoid cross-platform whitespace issues
def norm(s):
    return s.replace("\r\n", "\n")

content = norm(content)

# 1. Update the Inspector Logic to map editor marks and background correctly
search_1 = norm(r"""                    if (className.includes('preview-panel')) varsToHighlight.add('--border');
                    if (className.includes('editor-wrapper')) varsToHighlight.add('--panel-bg');
                    
                    if (className.includes('backdrop') || tagName === 'button' || tagName === 'select' || className.includes('toolbar-select') || tagName === 'path') {
                        if (!varsToHighlight.has('--primary') && !varsToHighlight.has('--danger')) {
                            varsToHighlight.add('--text-color');
                        }
                    }""")

replace_1 = norm(r"""                    if (className.includes('preview-panel')) varsToHighlight.add('--border');
                    if (className.includes('editor-wrapper')) varsToHighlight.add('--panel-bg');
                    
                    // 3. Editor Panel specific mapping
                    if (tagName === 'mark') {
                        if (className.includes('point-mark')) {
                            varsToHighlight.add('--danger');
                        } else {
                            varsToHighlight.add('--primary');
                        }
                    }
                    
                    if (className.includes('backdrop')) {
                        varsToHighlight.add('--text-color');
                        varsToHighlight.add('--panel-bg');
                    } else if (tagName === 'button' || tagName === 'select' || className.includes('toolbar-select') || tagName === 'path') {
                        if (!varsToHighlight.has('--primary') && !varsToHighlight.has('--danger')) {
                            varsToHighlight.add('--text-color');
                        }
                    }""")

# 2. Bump version to 1.11.0
search_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.10.0</div>""")

replace_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.11.0</div>""")

# Apply all patches
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")