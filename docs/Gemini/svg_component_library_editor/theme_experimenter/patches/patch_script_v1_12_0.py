import os

file_name = "svg_theme_experimenter_v1_11_0.html"
new_file_name = "svg_theme_experimenter_v1_12_0.html"

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

# 1. Update the Inspector Logic to map the footer background color alongside the text
search_1 = norm(r"""                    if (className.includes('footer-left') || className.includes('footer-center') || className.includes('footer-right')) {
                        varsToHighlight.add('--text-muted');
                    }""")

replace_1 = norm(r"""                    if (className.includes('footer-left') || className.includes('footer-center') || className.includes('footer-right')) {
                        varsToHighlight.add('--text-muted');
                        varsToHighlight.add('--toolbar-bg');
                    }""")

# 2. Bump version to 1.12.0
search_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.11.0</div>""")

replace_2 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.12.0</div>""")

# Apply all patches
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")