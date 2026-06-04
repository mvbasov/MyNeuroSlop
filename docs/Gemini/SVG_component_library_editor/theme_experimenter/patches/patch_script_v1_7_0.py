import os

file_name = "svg_theme_experimenter_v1_6_0.html"
new_file_name = "svg_theme_experimenter_v1_7_0.html"

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

# 1. Update the Pastel Themes (More blue for Dark, less bright for Light)
search_1 = norm(r"""                pastelLight: {
                    '--bg-color': '#FDFBF7',
                    '--panel-bg': '#F4EFE6',
                    '--text-color': '#5C5651',
                    '--text-muted': '#A49D94',
                    '--border': '#E0D9D0',
                    '--toolbar-bg': '#EBE5D9',
                    '--preview-bg': '#FAFAF5',
                    '--primary': '#AEC6CF',
                    '--primary-hover': '#9EB6BF',
                    '--grid-line': '#EAE3D9',
                    '--danger': '#F1B6B6',
                    '--success': '#B8E0B8'
                },
                pastelDark: {
                    '--bg-color': '#2A2B32',
                    '--panel-bg': '#34353E',
                    '--text-color': '#E2E0D8',
                    '--text-muted': '#9596A4',
                    '--border': '#464855',
                    '--toolbar-bg': '#2D2E37',
                    '--preview-bg': '#25262D',
                    '--primary': '#9FA8DA',
                    '--primary-hover': '#B3BCEE',
                    '--grid-line': '#3B3D4A',
                    '--danger': '#E5989B',
                    '--success': '#A5C4A3'
                }""")

replace_1 = norm(r"""                pastelLight: {
                    '--bg-color': '#F2EFE9',
                    '--panel-bg': '#E8E4DB',
                    '--text-color': '#5C5651',
                    '--text-muted': '#A49D94',
                    '--border': '#D6D0C4',
                    '--toolbar-bg': '#DFD9CD',
                    '--preview-bg': '#EFECE5',
                    '--primary': '#A3BACC',
                    '--primary-hover': '#92A9BB',
                    '--grid-line': '#DFD9CD',
                    '--danger': '#EAA4A4',
                    '--success': '#A8D5A8'
                },
                pastelDark: {
                    '--bg-color': '#2A2B32',
                    '--panel-bg': '#34353E',
                    '--text-color': '#E2E0D8',
                    '--text-muted': '#9596A4',
                    '--border': '#464855',
                    '--toolbar-bg': '#2D2E37',
                    '--preview-bg': '#25262D',
                    '--primary': '#8DA3C4',
                    '--primary-hover': '#A2B5D3',
                    '--grid-line': '#3B3D4A',
                    '--danger': '#E5989B',
                    '--success': '#A5C4A3'
                }""")

# 2. Bump version to 1.7.0
search_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.6.0</div>""")

replace_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.7.0</div>""")

# Apply replacements
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")