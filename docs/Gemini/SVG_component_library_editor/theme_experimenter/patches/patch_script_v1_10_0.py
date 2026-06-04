import os

file_name = "svg_theme_experimenter_v1_9_0.html"
new_file_name = "svg_theme_experimenter_v1_10_0.html"

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

# 1. Upscale Toolbar Buttons and Inputs
search_1 = norm(r"""        #mock-editor-app button {
            background: transparent;
            color: var(--text-color);
            border: 1px solid transparent;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        #mock-editor-app button:hover { background: var(--border); }
        #mock-editor-app button.primary { background: var(--primary); color: #ffffff; font-weight: 600; }
        #mock-editor-app button.primary:hover { background: var(--primary-hover); }
        #mock-editor-app button.danger { color: var(--danger); }
        #mock-editor-app button.danger:hover { background: rgba(255, 85, 85, 0.1); }

        #mock-editor-app .toolbar-select {
            background: transparent;
            color: var(--text-color);
            border: 1px solid transparent;
            padding: 4px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            outline: none;
            width: 32px;
            text-align: center;
            text-align-last: center;
        }""")

replace_1 = norm(r"""        #mock-editor-app button {
            background: transparent;
            color: var(--text-color);
            border: 1px solid transparent;
            padding: 10px 15px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        #mock-editor-app button:hover { background: var(--border); }
        #mock-editor-app button.primary { background: var(--primary); color: #ffffff; font-weight: 600; }
        #mock-editor-app button.primary:hover { background: var(--primary-hover); }
        #mock-editor-app button.danger { color: var(--danger); }
        #mock-editor-app button.danger:hover { background: rgba(255, 85, 85, 0.1); }

        #mock-editor-app .toolbar-select {
            background: transparent;
            color: var(--text-color);
            border: 1px solid transparent;
            padding: 8px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.2rem;
            outline: none;
            width: 45px;
            text-align: center;
            text-align-last: center;
        }""")

# 2. Update Badge CSS for Separation
search_2 = norm(r"""        #mock-editor-app .badge {
            background-color: var(--danger);
            color: white;
            font-size: 0.75rem;
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: bold;
        }""")

replace_2 = norm(r"""        #mock-editor-app .badge {
            color: #ffffff;
            font-size: 0.95rem;
            padding: 6px 12px;
            border-radius: 14px;
            font-weight: bold;
        }
        #mock-editor-app .badge.danger { background-color: var(--danger); }
        #mock-editor-app .badge.success { background-color: var(--success); color: #111; }""")

# 3. Upscale Footer Layout
search_3 = norm(r"""        #mock-editor-app footer {
            grid-area: footer;
            background-color: var(--toolbar-bg);
            border-top: 1px solid var(--border);
            padding: 4px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        #mock-editor-app .footer-left { display: flex; align-items: center; gap: 10px; flex: 1; }
        #mock-editor-app .footer-center { display: flex; align-items: center; justify-content: center; gap: 5px; flex: 1; white-space: nowrap; }
        #mock-editor-app .footer-right { flex: 1; text-align: right; white-space: nowrap; }""")

replace_3 = norm(r"""        #mock-editor-app footer {
            grid-area: footer;
            background-color: var(--toolbar-bg);
            border-top: 1px solid var(--border);
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1rem;
            color: var(--text-muted);
        }

        #mock-editor-app .footer-left { display: flex; align-items: center; gap: 15px; flex: 1; }
        #mock-editor-app .footer-center { display: flex; align-items: center; justify-content: center; gap: 10px; flex: 1; white-space: nowrap; }
        #mock-editor-app .footer-right { flex: 1; text-align: right; white-space: nowrap; }""")

# 4. Upscale Textarea Typography
search_4 = norm(r"""        #mock-editor-app .mock-textarea, #mock-editor-app .backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding: 15px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
            line-height: 1.5;
            box-sizing: border-box;
            white-space: pre;
        }""")

replace_4 = norm(r"""        #mock-editor-app .mock-textarea, #mock-editor-app .backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            padding: 20px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 1.2rem;
            line-height: 1.6;
            box-sizing: border-box;
            white-space: pre;
        }""")

# 5. Remove --success from Canvas
search_5 = norm(r"""                                    <!-- Sample Element colored by variables -->
                                    <circle cx="50" cy="50" r="30" fill="var(--success)" stroke="var(--primary)" stroke-width="4"/>
                                    <path d="M 30,50 L 70,50 M 50,30 L 50,70" stroke="var(--text-color)" stroke-width="4" stroke-linecap="round"/>""")

replace_5 = norm(r"""                                    <!-- Sample Element colored by variables -->
                                    <circle cx="50" cy="50" r="30" fill="var(--bg-color)" stroke="var(--primary)" stroke-width="4"/>
                                    <path d="M 30,50 L 70,50 M 50,30 L 50,70" stroke="var(--text-color)" stroke-width="4" stroke-linecap="round"/>""")

# 6. Update HTML Footer Badges & Inputs
search_6 = norm(r"""                        <footer>
                            <div class="footer-left">
                                <span class="badge" style="display:inline-block">Syntax Error</span>
                                <label class="toggle"><input type="checkbox" checked> Grid</label>
                                <span style="margin-left: 5px;">⌨️</span>
                                <span style="margin-left: 10px;">🌗</span>
                            </div>
                            <div class="footer-center">
                                <label>Step:</label>
                                <input type="number" class="toolbar-select" value="1" style="font-size: 0.75rem; padding: 2px 4px; width: 50px;">
                            </div>
                            <div class="footer-right">v6.6.0 (Mock)</div>
                        </footer>""")

replace_6 = norm(r"""                        <footer>
                            <div class="footer-left">
                                <span class="badge danger" style="display:inline-block">Error</span>
                                <span class="badge success" style="display:inline-block">Saved</span>
                                <label class="toggle"><input type="checkbox" checked> Grid</label>
                                <span style="margin-left: 5px;">⌨️</span>
                                <span style="margin-left: 10px;">🌗</span>
                            </div>
                            <div class="footer-center">
                                <label>Step:</label>
                                <input type="number" class="toolbar-select" value="1" style="font-size: 1rem; padding: 4px 8px; width: 60px;">
                            </div>
                            <div class="footer-right">v6.6.0 (Mock)</div>
                        </footer>""")

# 7. Update JS Event Walker logic to differentiate Success and Danger badges
search_7 = norm(r"""                    if (className.includes('danger') || className.includes('badge')) {
                        varsToHighlight.add('--danger');
                    }""")

replace_7 = norm(r"""                    if (className.includes('danger')) {
                        varsToHighlight.add('--danger');
                    }
                    if (className.includes('success')) {
                        varsToHighlight.add('--success');
                    }
                    if (className.includes('badge') && !className.includes('danger') && !className.includes('success')) {
                        varsToHighlight.add('--danger');
                    }""")

# 8. Version Bump
search_8 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.9.0</div>""")

replace_8 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.10.0</div>""")

# Apply all patches
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)
content = content.replace(search_3, replace_3)
content = content.replace(search_4, replace_4)
content = content.replace(search_5, replace_5)
content = content.replace(search_6, replace_6)
content = content.replace(search_7, replace_7)
content = content.replace(search_8, replace_8)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")