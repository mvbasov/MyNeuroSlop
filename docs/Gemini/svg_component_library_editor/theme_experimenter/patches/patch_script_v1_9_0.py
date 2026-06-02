import os

file_name = "svg_theme_experimenter_v1_8_0.html"
new_file_name = "svg_theme_experimenter_v1_9_0.html"

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

# 1. Darken the editor background to be very similar to the preview background
search_1 = norm(r"""                pastelLight: {
                    '--bg-color': '#F2EFE9',
                    '--panel-bg': '#E8E4DB',
                    '--text-color': '#5C5651',
                    '--text-muted': '#A49D94',
                    '--border': '#D6D0C4',
                    '--toolbar-bg': '#DFD9CD',
                    '--preview-bg': '#DFD9CD',
                    '--primary': '#A3BACC',
                    '--primary-hover': '#92A9BB',
                    '--grid-line': '#DFD9CD',
                    '--danger': '#EAA4A4',
                    '--success': '#A8D5A8'
                },""")

replace_1 = norm(r"""                pastelLight: {
                    '--bg-color': '#F2EFE9',
                    '--panel-bg': '#E2DDD2',
                    '--text-color': '#5C5651',
                    '--text-muted': '#A49D94',
                    '--border': '#D6D0C4',
                    '--toolbar-bg': '#DFD9CD',
                    '--preview-bg': '#DDD8CE',
                    '--primary': '#A3BACC',
                    '--primary-hover': '#92A9BB',
                    '--grid-line': '#DFD9CD',
                    '--danger': '#EAA4A4',
                    '--success': '#A8D5A8'
                },""")

# 2. Bump version to 1.9.0
search_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.8.0</div>""")

replace_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.9.0</div>""")

# Apply replacements
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")