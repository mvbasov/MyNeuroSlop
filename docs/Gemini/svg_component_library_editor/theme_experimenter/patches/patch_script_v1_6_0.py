import os

file_name = "svg_theme_experimenter_v1_5_0.html"
new_file_name = "svg_theme_experimenter_v1_6_0.html"

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

# 1. Update the Theme Dropdown to include Pastel themes
search_1 = norm(r"""                        <option value="cyberpunk">Cyberpunk</option>
                        <option value="ocean">Deep Ocean</option>
                    </select>""")

replace_1 = norm(r"""                        <option value="cyberpunk">Cyberpunk</option>
                        <option value="ocean">Deep Ocean</option>
                        <option value="pastelLight">Soft Pastel Light</option>
                        <option value="pastelDark">Soft Pastel Dark</option>
                    </select>""")

# 2. Inject the Pastel Theme configurations into the PRESETS object
search_2 = norm(r"""                ocean: {
                    '--bg-color': '#0F111A',
                    '--panel-bg': '#171B24',
                    '--text-color': '#8F93A2',
                    '--text-muted': '#4B5263',
                    '--border': '#1F2430',
                    '--toolbar-bg': '#090B10',
                    '--preview-bg': '#0F111A',
                    '--primary': '#82AAFF',
                    '--primary-hover': '#89DDFF',
                    '--grid-line': '#1F2430',
                    '--danger': '#F07178',
                    '--success': '#C3E88D'
                }
            };""")

replace_2 = norm(r"""                ocean: {
                    '--bg-color': '#0F111A',
                    '--panel-bg': '#171B24',
                    '--text-color': '#8F93A2',
                    '--text-muted': '#4B5263',
                    '--border': '#1F2430',
                    '--toolbar-bg': '#090B10',
                    '--preview-bg': '#0F111A',
                    '--primary': '#82AAFF',
                    '--primary-hover': '#89DDFF',
                    '--grid-line': '#1F2430',
                    '--danger': '#F07178',
                    '--success': '#C3E88D'
                },
                pastelLight: {
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
                }
            };""")

# 3. Bump version to 1.6.0
search_3 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.5.0</div>""")

replace_3 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.6.0</div>""")

# Apply replacements
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)
content = content.replace(search_3, replace_3)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")