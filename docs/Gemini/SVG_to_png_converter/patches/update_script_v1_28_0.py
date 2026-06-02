import sys
import os
import re

def patch_file():
    # Target the v1.27.0 file
    file_path = "svg_to_png_converter_v1_27_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Extract the current SVG content safely so we don't wipe your workspace
    main_content_start = content.find('<div class="main-content">')
    script_start = content.find('<script>', main_content_start)
    
    if main_content_start == -1 or script_start == -1:
        print("Error: Could not locate the main-content wrapper or script tag.")
        return
        
    workspace_chunk = content[main_content_start:script_start]
    
    svg_match = re.search(r'<textarea id="svg-input"[^>]*>(.*?)</textarea>', workspace_chunk, re.DOTALL)
    svg_content = svg_match.group(1) if svg_match else ""

    # Hunk 1: Completely replace the main-content HTML block with the new flat architectural layout
    # (Using string replacement instead of f-strings to protect inline SVG curly braces {})
    html_replacement = """        <div class="main-content">
            <div class="input-section">
                <textarea id="svg-input" placeholder="Paste or edit raw SVG code here...">__SVG_CONTENT__</textarea>
            </div>

            <div class="data-url-strip">
                <label class="toggle-label" title="Wrap generated data URL in an HTML link tag">
                    <input type="checkbox" id="chk-wrap-link">
                    <span>Wrap &lt;link&gt;</span>
                </label>
                <div class="data-url-inputs">
                    <input type="text" id="live-data-url" placeholder="Paste Data URL here or edit SVG...">
                    <button id="btn-copy-live-data">Copy Data URL</button>
                    <button id="btn-clear-live-data" class="btn-clear">Clear</button>
                </div>
            </div>

            <div class="preview-section">
                <div class="preview-container">
                    <canvas id="canvas"></canvas>
                    <div id="svg-error" class="error-msg" style="display: none;"></div>
                </div>
            </div>

            <div class="controls">
                <label class="toggle-label" title="Wrap canvas preview in 80x80 box">
                    <input type="checkbox" id="chk-wrap-80" checked>
                    <span>Wrap 80x80</span>
                </label>
                <label class="toggle-label" id="lbl-prepend-prefix" title="When checked, prepends 'data:image/png;base64,' to copied string">
                    <input type="checkbox" id="chk-prepend-prefix" checked>
                    <span>Prefix</span>
                </label>
                <select id="sel-format">
                    <option value="image/png">PNG</option>
                    <option value="image/bmp">BMP</option>
                    <option value="image/svg+xml">SVG Data URL</option>
                </select>
                <button id="btn-download">Save PNG</button>
                <button id="btn-copy-base64">Copy Base64</button>
                <button id="btn-clear" class="btn-clear">Clear</button>
            </div>
        </div>
    </div> <!-- End app container -->

    """
    
    html_replacement = html_replacement.replace("__SVG_CONTENT__", svg_content)
    
    # Safely splice the new DOM in
    content = content[:main_content_start] + html_replacement + content[script_start:]

    # Hunk 2: Append grid layout CSS override just before </style> to seamlessly control Desktop/Mobile
    css_injection = r"""
        /* --- v1.28.0 Layout Overrides --- */
        #svg-to-png-app .main-content {
            display: flex; flex-direction: column; gap: 24px;
        }
        #svg-to-png-app .input-section { order: 1; display: flex; flex-direction: column; }
        #svg-to-png-app .data-url-strip { 
            order: 2; display: flex; flex-direction: column; gap: 12px; align-items: flex-start; 
        }
        #svg-to-png-app .data-url-inputs {
            display: flex; gap: 8px; width: 100%; flex-wrap: wrap;
        }
        #svg-to-png-app .data-url-inputs input {
            flex-grow: 1; min-width: 150px; padding: 10px; border: 1px solid var(--border-color); 
            border-radius: 6px; background: var(--bg-input); color: var(--text-main); 
            font-family: monospace; font-size: 0.85rem; outline: none; 
            transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
        }
        #svg-to-png-app .data-url-inputs button {
            min-height: 40px; padding: 0 16px; white-space: nowrap;
        }
        #svg-to-png-app .preview-section { order: 3; display: flex; flex-direction: column; }
        #svg-to-png-app .controls { 
            order: 4; display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: flex-start; 
        }

        @media (min-width: 700px) {
            #svg-to-png-app .main-content {
                display: grid !important;
                grid-template-columns: 6fr 4fr;
                grid-template-rows: 1fr auto;
                align-items: stretch;
                gap: 24px;
            }
            #svg-to-png-app .input-section { grid-column: 1; grid-row: 1; }
            #svg-to-png-app .preview-section { grid-column: 2; grid-row: 1; }
            
            #svg-to-png-app .data-url-strip {
                grid-column: 1; grid-row: 2;
                flex-direction: row; align-items: center;
            }
            
            #svg-to-png-app .controls {
                grid-column: 2; grid-row: 2;
                justify-content: flex-end;
            }
            
            #svg-to-png-app #svg-input {
                min-height: 450px; height: 100%;
            }
        }
    </style>"""
    
    if '/* --- v1.28.0 Layout Overrides --- */' not in content:
        content = content.replace("</style>", css_injection)

    # Hunk 3: Version Bump
    if '<span class="version">v1.27.0</span>' in content:
        content = content.replace('<span class="version">v1.27.0</span>', '<span class="version">v1.28.0</span>')

    # Output to new version
    output_filename = "svg_to_png_converter_v1_28_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v1.28.0)!")

if __name__ == "__main__":
    patch_file()