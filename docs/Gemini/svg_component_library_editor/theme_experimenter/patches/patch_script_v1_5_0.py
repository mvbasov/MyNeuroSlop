import os

file_name = "svg_theme_experimenter_v1_4_0.html"
new_file_name = "svg_theme_experimenter_v1_5_0.html"

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

# 1. Update the Theme Dropdown to include more presets
search_1 = norm(r"""                <div class="preset-buttons">
                    <select id="theme-selector" style="width: 100%; padding: 8px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; outline: none; cursor: pointer; font-size: 0.85rem;">
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="dracula">Dracula</option>
                        <option value="solar">Solarized Light</option>
                        <option value="retro">Retro</option>
                        <option value="hacker">Dark Hacker Terminal</option>
                    </select>
                </div>""")

replace_1 = norm(r"""                <div class="preset-buttons">
                    <select id="theme-selector" style="width: 100%; padding: 8px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; outline: none; cursor: pointer; font-size: 0.85rem;">
                        <option value="light">Light Default</option>
                        <option value="dark">Dark Default</option>
                        <option value="dracula">Dracula</option>
                        <option value="solar">Solarized Light</option>
                        <option value="retro">Retro</option>
                        <option value="hacker">Amber Terminal</option>
                        <option value="monokai">Monokai</option>
                        <option value="nord">Nord</option>
                        <option value="synthwave">Synthwave '84</option>
                        <option value="cyberpunk">Cyberpunk</option>
                        <option value="ocean">Deep Ocean</option>
                    </select>
                </div>""")

# 2. Inject the new theme configurations into the PRESETS object
search_2 = norm(r"""                hacker: {
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
                }
            };""")

replace_2 = norm(r"""                hacker: {
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
                },
                monokai: {
                    '--bg-color': '#272822',
                    '--panel-bg': '#2E2E2E',
                    '--text-color': '#F8F8F2',
                    '--text-muted': '#75715E',
                    '--border': '#3E3D32',
                    '--toolbar-bg': '#1E1F1C',
                    '--preview-bg': '#272822',
                    '--primary': '#FD971F',
                    '--primary-hover': '#E6DB74',
                    '--grid-line': '#3E3D32',
                    '--danger': '#F92672',
                    '--success': '#A6E22E'
                },
                nord: {
                    '--bg-color': '#2E3440',
                    '--panel-bg': '#3B4252',
                    '--text-color': '#ECEFF4',
                    '--text-muted': '#4C566A',
                    '--border': '#434C5E',
                    '--toolbar-bg': '#2E3440',
                    '--preview-bg': '#3B4252',
                    '--primary': '#88C0D0',
                    '--primary-hover': '#81A1C1',
                    '--grid-line': '#434C5E',
                    '--danger': '#BF616A',
                    '--success': '#A3BE8C'
                },
                synthwave: {
                    '--bg-color': '#262335',
                    '--panel-bg': '#2a2139',
                    '--text-color': '#ffffff',
                    '--text-muted': '#848bbd',
                    '--border': '#34294f',
                    '--toolbar-bg': '#1b1924',
                    '--preview-bg': '#262335',
                    '--primary': '#f92aad',
                    '--primary-hover': '#ff7edb',
                    '--grid-line': '#34294f',
                    '--danger': '#fe4450',
                    '--success': '#72f1b8'
                },
                cyberpunk: {
                    '--bg-color': '#111019',
                    '--panel-bg': '#1f1e29',
                    '--text-color': '#0dfdff',
                    '--text-muted': '#5c5a77',
                    '--border': '#ff003c',
                    '--toolbar-bg': '#09080c',
                    '--preview-bg': '#111019',
                    '--primary': '#fcee0a',
                    '--primary-hover': '#fff87f',
                    '--grid-line': '#2d2b3d',
                    '--danger': '#ff003c',
                    '--success': '#00ff73'
                },
                ocean: {
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

# 3. Bump version to 1.5.0
search_3 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.4.0</div>""")

replace_3 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.5.0</div>""")

# Apply replacements
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)
content = content.replace(search_3, replace_3)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")