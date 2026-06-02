import os

file_name = "svg_theme_experimenter_v1_0_0.html"
new_file_name = "svg_theme_experimenter_v1_1_0.html"

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

# 1. Add CSS animations and interactive crosshair cursor
search_1 = norm(r"""        #color-schema-app .mock-app-container {
            width: 100%;
            height: 100%;
            max-width: 1200px;
            border: 1px dashed #555;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border-radius: 8px;
            overflow: hidden;
            container-type: inline-size; /* Ensure mobile query works within workspace */
        }""")

replace_1 = norm(r"""        #color-schema-app .mock-app-container {
            width: 100%;
            height: 100%;
            max-width: 1200px;
            border: 1px dashed #555;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border-radius: 8px;
            overflow: hidden;
            container-type: inline-size; /* Ensure mobile query works within workspace */
        }

        @keyframes pulseGlow {
            0% { box-shadow: 0 0 0 0px rgba(59, 130, 246, 0.8); border-color: #3b82f6; background-color: #2a3a4a; }
            50% { box-shadow: 0 0 0 6px rgba(59, 130, 246, 0); border-color: #3b82f6; background-color: #2a3a4a; }
            100% { box-shadow: 0 0 0 0px rgba(59, 130, 246, 0); border-color: #333; background-color: #252526; }
        }

        #color-schema-app .color-control.highlight-pulse {
            animation: pulseGlow 1.2s ease-out;
            border-color: #3b82f6;
        }

        /* Interactive Element Inspector Cursor */
        #mock-editor-app * {
            cursor: crosshair !important;
        }""")

# 2. Add the JS Color Inspector Logic
search_2 = norm(r"""            // Event Bindings
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

            // Boot
            initControls();
            applyToMock();
            updateExport();
        })();""")

replace_2 = norm(r"""            // Event Bindings
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
                let varsToHighlight = new Set();

                // Walk up the DOM tree from the clicked target
                while (target && target !== mockApp.parentElement) {
                    const fill = target.getAttribute('fill') || '';
                    const stroke = target.getAttribute('stroke') || '';
                    const className = (typeof target.className === 'string') ? target.className : (target.className && target.className.baseVal) || '';
                    const tagName = target.tagName ? target.tagName.toLowerCase() : '';
                    const id = target.id || '';

                    // 1. Detect Explicit Inline SVG Variables
                    if (fill.includes('var(')) {
                        let m = fill.match(/var\((--[^)]+)\)/);
                        if (m) varsToHighlight.add(m[1]);
                    }
                    if (stroke.includes('var(')) {
                        let m = stroke.match(/var\((--[^)]+)\)/);
                        if (m) varsToHighlight.add(m[1]);
                    }
                    if (fill.includes('url(#gridPattern)')) varsToHighlight.add('--grid-line');

                    // 2. Detect Component/Class based mappings
                    if (tagName === 'header' || tagName === 'footer') {
                        varsToHighlight.add('--toolbar-bg');
                        varsToHighlight.add('--border');
                    }
                    if (className.includes('toolbar-group')) {
                        varsToHighlight.add('--panel-bg');
                        varsToHighlight.add('--border');
                    }
                    if (className.includes('primary')) {
                        varsToHighlight.add('--primary');
                        varsToHighlight.add('--primary-hover');
                    }
                    if (className.includes('danger') || className.includes('badge')) {
                        varsToHighlight.add('--danger');
                    }
                    if (className.includes('preview-panel')) varsToHighlight.add('--border');
                    if (className.includes('editor-wrapper')) varsToHighlight.add('--panel-bg');
                    
                    if (className.includes('backdrop') || tagName === 'button' || tagName === 'select' || className.includes('toolbar-select') || tagName === 'path') {
                        if (!varsToHighlight.has('--primary') && !varsToHighlight.has('--danger')) {
                            varsToHighlight.add('--text-color');
                        }
                    }
                    if (className.includes('footer-left') || className.includes('footer-center') || className.includes('footer-right')) {
                        varsToHighlight.add('--text-muted');
                    }
                    if (id === 'preview-container') varsToHighlight.add('--preview-bg');
                    if (id === 'mock-editor-app') varsToHighlight.add('--bg-color');

                    // If we found variables matching this target layer, stop bubbling
                    if (varsToHighlight.size > 0) break; 
                    
                    target = target.parentElement;
                }

                // Ultimate fallback
                if (varsToHighlight.size === 0) varsToHighlight.add('--bg-color');

                // Trigger Highlight and Scroll on Sidebar Controls
                varsToHighlight.forEach(varName => {
                    const input = inputsMap[varName];
                    if (input) {
                        const controlDiv = input.closest('.color-control');
                        controlDiv.classList.remove('highlight-pulse');
                        void controlDiv.offsetWidth; // Force CSS reflow
                        controlDiv.classList.add('highlight-pulse');
                        controlDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                });
            });

            // Boot
            initControls();
            applyToMock();
            updateExport();
        })();""")

# 3. Bump version to 1.1.0
search_3 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.0.0</div>""")

replace_3 = norm(r"""                <textarea id="css-export" readonly></textarea>
                <div class="app-version">v1.1.0</div>""")

# Execute Patches
content = content.replace(search_1, replace_1)
content = content.replace(search_2, replace_2)
content = content.replace(search_3, replace_3)

with open(new_file_name, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched! Output written to {new_file_name}")