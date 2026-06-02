import os

file_name = "svg_theme_experimenter_v1_1_0.html"
new_file_name = "svg_theme_experimenter_v1_2_0.html"

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

# 1. Update CSS for preset buttons to allow wrapping
search_1 = norm(r"""        #color-schema-app .preset-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }""")

replace_1 = norm(r"""        #color-schema-app .preset-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }""")

# 2. Add new buttons to the HTML sidebar
search_2 = norm(r"""                <div class="preset-buttons">
                    <button class="preset-btn" id="btn-light">Load Light</button>
                    <button class="preset-btn" id="btn-dark">Load Dark</button>
                </div>""")

replace_2 = norm(r"""                <div class="preset-buttons">
                    <button class="preset-btn" id="btn-light">Light</button>
                    <button class="preset-btn" id="btn-dark">Dark</button>
                    <button class="preset-btn" id="btn-dracula">Dracula</button>
                    <button class="preset-btn" id="btn-solar">Solarized</button>
                    <button class="preset-btn" id="btn-retro">Retro</button>
                </div>""")

# 3. Inject new color palettes into the JS PRESETS object
search_3 = norm(r"""            const PRESETS = {
                light: {
                    '--bg-color': '#E2DCD2',
                    '--panel-bg': '#C9C0B2',
                    '--text-color': '#2C2A28',
                    '--text-muted': '#6E665C',
                    '--border': '#B7AC9C',
                    '--toolbar-bg': '#DCD4C8',
                    '--preview-bg': '#DDD5C9',
                    '--primary': '#6B7F8E',
                    '--primary-hover': '#7E92A2',
                    '--grid-line': '#C9BEAD',
                    '--danger': '#C98686',
                    '--success': '#8FAA8A'
                },
                dark: {
                    '--bg-color': '#1e1e2e',
                    '--panel-bg': '#282a36',
                    '--text-color': '#b8b8b0',
                    '--text-muted': '#6e6e7a',
                    '--border': '#3d3f4f',
                    '--toolbar-bg': '#252530',
                    '--preview-bg': '#1a1a24',
                    '--primary': '#6b8a9e',
                    '--primary-hover': '#7e9aae',
                    '--grid-line': '#3a3a45',
                    '--danger': '#cc8888',
                    '--success': '#88aa88'
                }
            };""")

replace_3 = norm(r"""            const PRESETS = {
                light: {
                    '--bg-color': '#E2DCD2',
                    '--panel-bg': '#C9C0B2',
                    '--text-color': '#2C2A28',
                    '--text-muted': '#6E665C',
                    '--border': '#B7AC9C',
                    '--toolbar-bg': '#DCD4C8',
                    '--preview-bg': '#DDD5C9',
                    '--primary': '#6B7F8E',
                    '--primary-hover': '#7E92A2',
                    '--grid-line': '#C9BEAD',
                    '--danger': '#C98686',
                    '--success': '#8FAA8A'
                },
                dark: {
                    '--bg-color': '#1e1e2e',
                    '--panel-bg': '#282a36',
                    '--text-color': '#b8b8b0',
                    '--text-muted': '#6e6e7a',
                    '--border': '#3d3f4f',
                    '--toolbar-bg': '#252530',
                    '--preview-bg': '#1a1a24',
                    '--primary': '#6b8a9e',
                    '--primary-hover': '#7e9aae',
                    '--grid-line': '#3a3a45',
                    '--danger': '#cc8888',
                    '--success': '#88aa88'
                },
                dracula: {
                    '--bg-color': '#282a36',
                    '--panel-bg': '#44475a',
                    '--text-color': '#f8f8f2',
                    '--text-muted': '#6272a4',
                    '--border': '#6272a4',
                    '--toolbar-bg': '#21222c',
                    '--preview-bg': '#282a36',
                    '--primary': '#bd93f9',
                    '--primary-hover': '#ff79c6',
                    '--grid-line': '#44475a',
                    '--danger': '#ff5555',
                    '--success': '#50fa7b'
                },
                solar: {
                    '--bg-color': '#fdf6e3',
                    '--panel-bg': '#eee8d5',
                    '--text-color': '#657b83',
                    '--text-muted': '#93a1a1',
                    '--border': '#ccc8b6',
                    '--toolbar-bg': '#fdf6e3',
                    '--preview-bg': '#eee8d5',
                    '--primary': '#268bd2',
                    '--primary-hover': '#2aa198',
                    '--grid-line': '#eaddc5',
                    '--danger': '#dc322f',
                    '--success': '#859900'
                },
                retro: {
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

# 4. Bind new buttons and add the clear-highlight logic to the click listener
search_4 = norm(r"""            // Event Bindings
            document.getElementById('btn-light').addEventListener('click', () => loadPreset('light'));
            document.getElementById('btn-dark').addEventListener('click', () => loadPreset('dark'));
            
            document.getElementById('btn-copy').addEventListener('click', () => {
                cssExport.select();
                document.execCommand('copy');
                const btn = document.getElementById('btn-copy');
                const orig = btn.innerHTML;
                btn.innerHTML = '✅ Copied!';
                setTimeout(() => btn.innerHTML = orig, 1500);
            });

            // --- Interactive Color Inspector ---
            mockApp.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                let target = e.target;
                let varsToHighlight = new Set();""")

replace_4 = norm(r"""            // Event Bindings
            document.getElementById('btn-light').addEventListener('click', () => loadPreset('light'));
            document.getElementById('btn-dark').addEventListener('click', () => loadPreset('dark'));
            document.getElementById('btn-dracula').addEventListener('click', () => loadPreset('dracula'));
            document.getElementById('btn-solar').addEventListener('click', () => loadPreset('solar'));
            document.getElementById('btn-retro').addEventListener('click', () => loadPreset('retro'));
            
            document.getElementById('btn-copy').addEventListener('click', () => {
                cssExport.select();
                document.execCommand('copy');
                const btn = document.getElementById('btn-copy');
                const orig = btn.innerHTML;
                btn.innerHTML = '✅ Copied!';
                setTimeout(() => btn.innerHTML = orig, 1500);
            });

            // --- Interactive Color Inspector ---
            mockApp.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                // Clear previous highlights
                document.querySelectorAll('.highlight-pulse').forEach(el => {
                    el.classList.remove('highlight-pulse');
                });

                let target = e.target;
                let varsToHighlight = new Set();""")

# 5. Bump version to 1.2.0
search_5 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.1.0</div>""")

replace_5 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.2.0</div>""")

# Apply replacements
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)
content = content.replace(search_3, replace_3)
content = content.replace(search_4, replace_4)
content = content.replace(search_5, replace_5)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")