import os

def patch_file():
    file_path = "schematic_library_1_26_2.html"
    output_path = "schematic_library_1_27_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize line endings to ensure str.replace matches perfectly
    content = content.replace("\r\n", "\n")

    # 1. Update the CSS Block to establish variables and scoped styles
    search_css = r"""    body {
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      padding: 2rem;
      background-color: #f8fafc;
      font-family: sans-serif;
      gap: 2rem;
      box-sizing: border-box;
    }

    .header-desc {
      width: 100%;
      max-width: 900px;
      text-align: center;
      margin-bottom: 0.5rem;
    }

    .header-desc h1 {
      margin-top: 0;
      margin-bottom: 0.5rem;
      color: #0f172a;
    }

    .header-desc .short-desc {
      color: #334155;
      margin: 0;
      font-size: 1.1rem;
    }

    .detailed-desc {
      margin-top: 1.25rem;
      color: #475569;
      text-align: left;
      background: #ffffff;
      padding: 1rem 1.5rem;
      border-radius: 12px;
      box-shadow: 0 2px 6px rgb(0 0 0 / 0.05);
      border: 1px solid #e2e8f0;
    }

    .detailed-desc summary {
      cursor: pointer;
      font-weight: bold;
      color: #0f172a;
      user-select: none;
    }

    .detailed-desc p {
      margin-top: 1rem;
      margin-bottom: 0;
      line-height: 1.6;
    }

    .foldable-card {
      width: 100%;
      max-width: 900px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
      overflow: hidden;
    }

    .foldable-header {
      padding: 1.25rem 1.5rem;
      font-size: 1.2rem;
      font-weight: bold;
      color: #0f172a;
      background-color: #f8fafc;
      cursor: pointer;
      user-select: none;
      border-bottom: 1px solid transparent;
    }

    .foldable-card[open] .foldable-header {
      border-bottom-color: #e2e8f0;
    }

    .foldable-body {
      padding: 2rem;
    }

    .circuit-diagram {
      color: #0f172a;
      width: 100%;
      display: block;
    }
    
    .component-label {
      font-size: 16px;
      font-family: monospace;
      font-weight: bold;
      fill: currentColor;
      stroke: none;
    }

    .catalog {
      color: #0f172a;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      width: 100%;
    }
    
    .catalog-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      font-family: monospace;
      font-weight: bold;
      gap: 0.5rem;
      position: relative;
      cursor: pointer;
      padding: 1rem 0.5rem;
      border-radius: 8px;
      border: 1px solid transparent;
      transition: all 0.2s;
      text-align: center;
    }

    .catalog-item:hover {
      background-color: #f1f5f9;
      border-color: #cbd5e1;
    }

    .component-checkbox {
      position: absolute;
      top: 8px;
      left: 8px;
      cursor: pointer;
      width: 1.25rem;
      height: 1.25rem;
      accent-color: #3b82f6;
    }

    /* Export Controls Panel */
    .export-controls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1.5rem;
      margin-bottom: 2rem;
      padding: 1rem;
      background-color: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
    }

    .control-group {
      display: flex;
      gap: 0.75rem;
    }

    .export-options-group {
      display: flex;
      align-items: center;
      gap: 1.25rem;
      font-size: 0.9rem;
      color: #334155;
      flex-wrap: wrap;
    }

    .export-options-group label {
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      user-select: none;
    }

    .export-options-group code {
      background: #e2e8f0;
      padding: 0.1rem 0.3rem;
      border-radius: 4px;
      font-size: 0.85rem;
      color: #0f172a;
    }

    .btn {
      padding: 0.5rem 1rem;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      border: none;
      font-family: sans-serif;
      transition: background-color 0.2s, opacity 0.2s;
    }

    .btn:active {
      transform: scale(0.98);
    }

    .btn-primary {
      background-color: #3b82f6;
      color: white;
    }

    .btn-primary:hover {
      background-color: #2563eb;
    }

    .btn-secondary {
      background-color: #e2e8f0;
      color: #334155;
    }

    .btn-secondary:hover {
      background-color: #cbd5e1;
    }

    .tutorial-section {
      color: #0f172a;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.5rem;
    }
    
    .tutorial-text {
      font-family: sans-serif;
      font-size: 15px;
      line-height: 1.5;
      color: #334155;
      text-align: center;
      max-width: 650px;
      margin: 0;
    }

    .version-footer {
      color: #475569;
      background: white;
      padding: 1.5rem;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
      width: 100%;
      max-width: 900px;
      text-align: center;
      font-family: monospace;
      font-size: 14px;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    /* Toast Message Box */
    .toast-msg {
      position: fixed;
      bottom: 20px;
      right: 20px;
      background-color: #0f172a;
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 8px;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
      z-index: 9999;
      font-family: sans-serif;
      font-weight: 500;
      animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
      from { transform: translateY(100%); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }

    @media (max-width: 640px) {
      .catalog {
        grid-template-columns: repeat(2, 1fr);
      }
      .export-controls {
        flex-direction: column;
        align-items: stretch;
      }
      .control-group, .export-options-group {
        flex-direction: column;
        align-items: flex-start;
      }
    }"""

    replace_css = r"""    body:not(.theme-dark) {
      --body-bg: #f8fafc;
    }
    body.theme-dark {
      --body-bg: #0f172a;
    }
    body {
      margin: 0;
      background-color: var(--body-bg);
      font-family: sans-serif;
      transition: background-color 0.3s ease;
    }

    #name-app {
      --bg-color: #f8fafc;
      --card-bg: #ffffff;
      --text-main: #0f172a;
      --text-muted: #334155;
      --text-light: #475569;
      --border-color: #e2e8f0;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --secondary-bg: #e2e8f0;
      --secondary-hover: #cbd5e1;
      --hover-bg: #f1f5f9;
      --shadow-color: rgb(0 0 0 / 0.1);
      --shadow-light: rgb(0 0 0 / 0.05);
      --toast-bg: #0f172a;
      --toast-text: #ffffff;
      --preview-bg: aliceblue;
      --danger: #ef4444;
      --grid-line: #cbd5e1;
      --grid-axis: #94a3b8;

      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
      padding: 2rem;
      gap: 2rem;
      box-sizing: border-box;
      color: var(--text-main);
      background-color: transparent;
      width: 100%;
    }

    #name-app.theme-dark {
      --bg-color: #0f172a;
      --card-bg: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #cbd5e1;
      --text-light: #94a3b8;
      --border-color: #334155;
      --primary: #3b82f6;
      --primary-hover: #60a5fa;
      --secondary-bg: #334155;
      --secondary-hover: #475569;
      --hover-bg: #0f172a;
      --shadow-color: rgb(0 0 0 / 0.3);
      --shadow-light: rgb(0 0 0 / 0.2);
      --toast-bg: #f8fafc;
      --toast-text: #0f172a;
      --preview-bg: #0f172a;
      --grid-line: #334155;
      --grid-axis: #475569;
    }

    #name-app *, #name-app *::before, #name-app *::after {
      transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, fill 0.3s ease, stroke 0.3s ease;
    }

    .header-desc {
      width: 100%;
      max-width: 900px;
      text-align: center;
      margin-bottom: 0.5rem;
    }

    .header-desc h1 {
      margin-top: 0;
      margin-bottom: 0.5rem;
      color: var(--text-main);
    }

    .header-desc .short-desc {
      color: var(--text-muted);
      margin: 0;
      font-size: 1.1rem;
    }

    .detailed-desc {
      margin-top: 1.25rem;
      color: var(--text-light);
      text-align: left;
      background: var(--card-bg);
      padding: 1rem 1.5rem;
      border-radius: 12px;
      box-shadow: 0 2px 6px var(--shadow-light);
      border: 1px solid var(--border-color);
    }

    .detailed-desc summary {
      cursor: pointer;
      font-weight: bold;
      color: var(--text-main);
      user-select: none;
    }

    .detailed-desc p {
      margin-top: 1rem;
      margin-bottom: 0;
      line-height: 1.6;
    }

    .foldable-card {
      width: 100%;
      max-width: 900px;
      background: var(--card-bg);
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px var(--shadow-color);
      overflow: hidden;
    }

    .foldable-header {
      padding: 1.25rem 1.5rem;
      font-size: 1.2rem;
      font-weight: bold;
      color: var(--text-main);
      background-color: var(--bg-color);
      cursor: pointer;
      user-select: none;
      border-bottom: 1px solid transparent;
    }

    .foldable-card[open] .foldable-header {
      border-bottom-color: var(--border-color);
    }

    .foldable-body {
      padding: 2rem;
    }

    .circuit-diagram {
      color: var(--text-main);
      width: 100%;
      display: block;
    }
    
    .component-label {
      font-size: 16px;
      font-family: monospace;
      font-weight: bold;
      fill: currentColor;
      stroke: none;
    }

    .catalog {
      color: var(--text-main);
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      width: 100%;
    }
    
    .catalog-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      font-family: monospace;
      font-weight: bold;
      gap: 0.5rem;
      position: relative;
      cursor: pointer;
      padding: 1rem 0.5rem;
      border-radius: 8px;
      border: 1px solid transparent;
      transition: all 0.2s;
      text-align: center;
    }

    .catalog-item:hover {
      background-color: var(--hover-bg);
      border-color: var(--border-color);
    }

    .component-checkbox {
      position: absolute;
      top: 8px;
      left: 8px;
      cursor: pointer;
      width: 1.25rem;
      height: 1.25rem;
      accent-color: var(--primary);
    }

    /* Export Controls Panel */
    .export-controls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1.5rem;
      margin-bottom: 2rem;
      padding: 1rem;
      background-color: var(--bg-color);
      border: 1px solid var(--border-color);
      border-radius: 8px;
    }

    .control-group {
      display: flex;
      gap: 0.75rem;
    }

    .export-options-group {
      display: flex;
      align-items: center;
      gap: 1.25rem;
      font-size: 0.9rem;
      color: var(--text-muted);
      flex-wrap: wrap;
    }

    .export-options-group label {
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      user-select: none;
    }

    .export-options-group code {
      background: var(--secondary-bg);
      padding: 0.1rem 0.3rem;
      border-radius: 4px;
      font-size: 0.85rem;
      color: var(--text-main);
    }

    .btn {
      padding: 0.5rem 1rem;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      border: none;
      font-family: sans-serif;
      transition: background-color 0.2s, opacity 0.2s;
    }

    .btn:active {
      transform: scale(0.98);
    }

    .btn-primary {
      background-color: var(--primary);
      color: white;
    }

    .btn-primary:hover {
      background-color: var(--primary-hover);
    }

    .btn-secondary {
      background-color: var(--secondary-bg);
      color: var(--text-main);
    }

    .btn-secondary:hover {
      background-color: var(--secondary-hover);
    }

    .tutorial-section {
      color: var(--text-main);
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.5rem;
    }
    
    .tutorial-text {
      font-family: sans-serif;
      font-size: 15px;
      line-height: 1.5;
      color: var(--text-muted);
      text-align: center;
      max-width: 650px;
      margin: 0;
    }

    .version-footer {
      color: var(--text-light);
      background: var(--card-bg);
      padding: 1.5rem;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px var(--shadow-color);
      width: 100%;
      max-width: 900px;
      text-align: center;
      font-family: monospace;
      font-size: 14px;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    /* Toast Message Box */
    .toast-msg {
      position: fixed;
      bottom: 20px;
      right: 20px;
      background-color: var(--toast-bg);
      color: var(--toast-text);
      padding: 1rem 1.5rem;
      border-radius: 8px;
      box-shadow: 0 4px 10px var(--shadow-color);
      z-index: 9999;
      font-family: sans-serif;
      font-weight: 500;
      animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
      from { transform: translateY(100%); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }

    @media (max-width: 640px) {
      .catalog {
        grid-template-columns: repeat(2, 1fr);
      }
      .export-controls {
        flex-direction: column;
        align-items: stretch;
      }
      .control-group, .export-options-group {
        flex-direction: column;
        align-items: flex-start;
      }
    }"""
    content = content.replace(search_css, replace_css)

    # 2. Add #name-app wrapper and update version in body
    search_body = r"""<body data-version="1.26.0">

  <!-- ==========================================
       0. HEADER DESCRIPTION
       ========================================== -->"""

    replace_body = r"""<body data-version="1.27.0">

  <div id="name-app">

  <!-- ==========================================
       0. HEADER DESCRIPTION
       ========================================== -->"""
    content = content.replace(search_body, replace_body)

    # 3. Add Theme Button immediately after version footer, then close the #name-app wrapper
    search_footer = r"""  <div class="version-footer" id="version-footer">
    <!-- Populated dynamically by JavaScript to keep version numbers centrally managed -->
  </div>

  <!-- ==========================================
       7. EXPORT LOGIC (JavaScript)
       ========================================== -->"""

    replace_footer = r"""  <div class="version-footer" id="version-footer">
    <!-- Populated dynamically by JavaScript to keep version numbers centrally managed -->
  </div>

  <div style="text-align: center; margin-bottom: 2rem;">
    <button id="theme-toggle-btn" class="btn btn-secondary" style="font-family: monospace; font-size: 14px; padding: 0.5rem 1.25rem; border: 1px solid var(--border-color);">Theme: 🌗 Auto</button>
  </div>

  </div> <!-- End #name-app -->

  <!-- ==========================================
       7. EXPORT LOGIC (JavaScript)
       ========================================== -->"""
    content = content.replace(search_footer, replace_footer)

    # 4. Integrate Advanced Theme Controller IIFE with interactive toggle
    search_script = r"""  <script>
    document.addEventListener('DOMContentLoaded', () => {
      
      // --- POPULATE VERSION FOOTER DYNAMICALLY ---"""

    replace_script = r"""  <script>
    (function() {
      // --- THEME CONTROLLER ---
      let APP_THEME = localStorage.getItem('schematic-theme') || 'auto';
      
      function applyTheme(isDark) {
        if (isDark) {
          document.body.classList.add('theme-dark');
          document.getElementById('name-app').classList.add('theme-dark');
        } else {
          document.body.classList.remove('theme-dark');
          document.getElementById('name-app').classList.remove('theme-dark');
        }
      }

      function updateThemeBtn() {
        const btn = document.getElementById('theme-toggle-btn');
        if (btn) {
           const labels = { 'auto': '🌗 Auto', 'light': '☀️ Light', 'dark': '🌙 Dark' };
           btn.textContent = `Theme: ${labels[APP_THEME] || APP_THEME}`;
        }
      }

      function initTheme() {
        if (APP_THEME === 'dark') {
          applyTheme(true);
        } else if (APP_THEME === 'light') {
          applyTheme(false);
        } else {
          const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
          applyTheme(mediaQuery.matches);
        }
        updateThemeBtn();
      }

      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (APP_THEME === 'auto') applyTheme(e.matches);
      });

      initTheme();

      document.addEventListener('DOMContentLoaded', () => {
        const themeBtn = document.getElementById('theme-toggle-btn');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => {
                if (APP_THEME === 'auto') APP_THEME = 'light';
                else if (APP_THEME === 'light') APP_THEME = 'dark';
                else APP_THEME = 'auto';
                
                localStorage.setItem('schematic-theme', APP_THEME);
                initTheme();
            });
            updateThemeBtn(); // Call again after DOM load to ensure text is set
        }

        // --- POPULATE VERSION FOOTER DYNAMICALLY ---"""
    content = content.replace(search_script, replace_script)

    # 5. Close the IIFE at the end of the script
    search_script_end = r"""        showMessage('custom_schematic_library.svg downloaded!');
      });
    });
  </script>"""

    replace_script_end = r"""        showMessage('custom_schematic_library.svg downloaded!');
      });
    });
    })();
  </script>"""
    content = content.replace(search_script_end, replace_script_end)

    # 6. Global string replacements to map inline SVG colors to our CSS variables seamlessly
    content = content.replace('fill="aliceblue"', 'fill="var(--preview-bg)"')
    content = content.replace('fill="#f8fafc"', 'fill="var(--bg-color)"')
    content = content.replace('stroke="#f8fafc"', 'stroke="var(--bg-color)"')
    content = content.replace('stroke="#94a3b8"', 'stroke="var(--grid-axis)"')
    content = content.replace('stroke="#cbd5e1"', 'stroke="var(--grid-line)"')
    content = content.replace('fill="#3b82f6"', 'fill="var(--primary)"')
    content = content.replace('fill="#ef4444"', 'fill="var(--danger)"')
    content = content.replace('color="#0f172a"', 'color="var(--text-main)"')
    content = content.replace('fill="#64748b"', 'fill="var(--text-light)"')
    content = content.replace('fill="#0f172a"', 'fill="var(--text-main)"')

    # Output patched file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    patch_file()