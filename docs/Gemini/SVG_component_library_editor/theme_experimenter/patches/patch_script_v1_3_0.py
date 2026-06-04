import os

file_name = "svg_theme_experimenter_v1_2_0.html"
new_file_name = "svg_theme_experimenter_v1_3_0.html"

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

# 1. Replace the buttons with a select dropdown
search_1 = norm(r"""                <div class="preset-buttons">
                    <button class="preset-btn" id="btn-light">Light</button>
                    <button class="preset-btn" id="btn-dark">Dark</button>
                    <button class="preset-btn" id="btn-dracula">Dracula</button>
                    <button class="preset-btn" id="btn-solar">Solarized</button>
                    <button class="preset-btn" id="btn-retro">Retro</button>
                </div>""")

replace_1 = norm(r"""                <div class="preset-buttons">
                    <select id="theme-selector" style="width: 100%; padding: 8px; background: #333; color: #fff; border: 1px solid #555; border-radius: 4px; outline: none; cursor: pointer; font-size: 0.85rem;">
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="dracula">Dracula</option>
                        <option value="solar">Solarized Light</option>
                        <option value="retro">Retro</option>
                        <option value="hacker">Dark Hacker Terminal</option>
                    </select>
                </div>""")

# 2. Inject the Hacker theme into the PRESETS object
search_2 = norm(r"""                retro: {
                    '--bg-color': '#2A211C',
                    '--panel-bg': '#3A2E25',
                    '--text-color': '#FFB000',
                    '--text-muted': '#B07D00',
                    '--border': '#5C4A3D',
                    '--toolbar-bg': '#1E1612',
                    '--preview-bg': '#2A211C',
                    '--primary': '#00FF41',
                    '--primary-hover': '#008F11',
                    '--grid-line': '#4A3B31',
                    '--danger': '#FF003C',
                    '--success': '#00FF41'
                }
            };""")

replace_2 = norm(r"""                retro: {
                    '--bg-color': '#2A211C',
                    '--panel-bg': '#3A2E25',
                    '--text-color': '#FFB000',
                    '--text-muted': '#B07D00',
                    '--border': '#5C4A3D',
                    '--toolbar-bg': '#1E1612',
                    '--preview-bg': '#2A211C',
                    '--primary': '#00FF41',
                    '--primary-hover': '#008F11',
                    '--grid-line': '#4A3B31',
                    '--danger': '#FF003C',
                    '--success': '#00FF41'
                },
                hacker: {
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
                }
            };""")

# 3. Update the event listeners to watch the select dropdown instead of the buttons
search_3 = norm(r"""            // Event Bindings
            document.getElementById('btn-light').addEventListener('click', () => loadPreset('light'));
            document.getElementById('btn-dark').addEventListener('click', () => loadPreset('dark'));
            document.getElementById('btn-dracula').addEventListener('click', () => loadPreset('dracula'));
            document.getElementById('btn-solar').addEventListener('click', () => loadPreset('solar'));
            document.getElementById('btn-retro').addEventListener('click', () => loadPreset('retro'));
            
            document.getElementById('btn-copy').addEventListener('click', () => {""")

replace_3 = norm(r"""            // Event Bindings
            document.getElementById('theme-selector').addEventListener('change', (e) => loadPreset(e.target.value));
            
            document.getElementById('btn-copy').addEventListener('click', () => {""")

# 4. Bump version to 1.3.0
search_4 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.2.0</div>""")

replace_4 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.3.0</div>""")

# Apply replacements
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)
content = content.replace(search_3, replace_3)
content = content.replace(search_4, replace_4)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")