import os

file_name = "svg_theme_experimenter_v1_3_0.html"
new_file_name = "svg_theme_experimenter_v1_4_0.html"

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

# 1. Update the Hacker Theme colors from Neon Green to Retro Dark Orange / Amber
search_1 = norm(r"""                hacker: {
                    '--bg-color': '#050505',
                    '--panel-bg': '#0a0a0a',
                    '--text-color': '#00ff00',
                    '--text-muted': '#005500',
                    '--border': '#004400',
                    '--toolbar-bg': '#000000',
                    '--preview-bg': '#000000',
                    '--primary': '#00cc00',
                    '--primary-hover': '#00ff00',
                    '--grid-line': '#002200',
                    '--danger': '#ff0000',
                    '--success': '#00ff00'
                }""")

replace_1 = norm(r"""                hacker: {
                    '--bg-color': '#050505',
                    '--panel-bg': '#0a0a0a',
                    '--text-color': '#ff9900',
                    '--text-muted': '#663300',
                    '--border': '#442200',
                    '--toolbar-bg': '#000000',
                    '--preview-bg': '#000000',
                    '--primary': '#cc7700',
                    '--primary-hover': '#ff9900',
                    '--grid-line': '#221100',
                    '--danger': '#ff0000',
                    '--success': '#ff9900'
                }""")

# 2. Bump version to 1.4.0
search_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.3.0</div>""")

replace_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.4.0</div>""")

# Apply replacements
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")