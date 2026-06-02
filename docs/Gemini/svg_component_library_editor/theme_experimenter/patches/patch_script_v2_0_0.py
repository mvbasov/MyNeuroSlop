import os

file_name = "svg_theme_experimenter_v1_12_0.html"
new_file_name = "svg_theme_experimenter_v2_0_0.html"

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

# 1. Bump major version to 2.0.0
search_1 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.12.0</div>""")

replace_1 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v2.0.0</div>""")

# Apply patches
content = content.replace(search_1, replace_1)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")