import sys
import os

def patch_file(input_filename, output_filename):
    if not os.path.exists(input_filename):
        print(f"Error: Could not find {input_filename}")
        return

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Define precise string replacements using raw strings (r''') to handle JS escapes safely
        replacements = [
            # 1. Add the Theme Toggle Button to the footer HTML
            (
                r'''                    <button id="toggle-keyboard" title="Toggle Virtual Keyboard" style="background: none; border: none; padding: 0; margin-left: 5px; color: inherit; cursor: pointer; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; transition: opacity 0.2s;">⌨️</button>
                </div>''',
                r'''                    <button id="toggle-keyboard" title="Toggle Virtual Keyboard" style="background: none; border: none; padding: 0; margin-left: 5px; color: inherit; cursor: pointer; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; transition: opacity 0.2s;">⌨️</button>
                    <button id="toggle-theme" title="Theme: Auto" style="background: none; border: none; padding: 0; margin-left: 10px; color: inherit; cursor: pointer; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; transition: opacity 0.2s;">🌗</button>
                </div>'''
            ),
            
            # 2. Upgrade the Theme Controller to allow state mutation and update the UI button
            (
                r'''            // Theme Controller Implementation
            const APP_THEME = 'auto'; // Supports 'auto', 'dark', 'light'

            function applyTheme() {
                const body = document.body;
                const app = document.getElementById('svg-editor-app');
                
                let isDark = false;
                if (APP_THEME === 'dark') {
                    isDark = true;
                } else if (APP_THEME === 'light') {
                    isDark = false;
                } else {
                    // 'auto' - system media preference
                    isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                }
                
                if (isDark) {
                    body.classList.add('theme-dark');
                    if (app) app.classList.add('theme-dark');
                } else {
                    body.classList.remove('theme-dark');
                    if (app) app.classList.remove('theme-dark');
                }
            }''',
                r'''            // Theme Controller Implementation
            let APP_THEME = 'auto'; // Supports 'auto', 'dark', 'light'

            function applyTheme() {
                const body = document.body;
                const app = document.getElementById('svg-editor-app');
                const themeBtn = document.getElementById('toggle-theme');
                
                let isDark = false;
                if (APP_THEME === 'dark') {
                    isDark = true;
                } else if (APP_THEME === 'light') {
                    isDark = false;
                } else {
                    // 'auto' - system media preference
                    isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                }
                
                if (isDark) {
                    body.classList.add('theme-dark');
                    if (app) app.classList.add('theme-dark');
                } else {
                    body.classList.remove('theme-dark');
                    if (app) app.classList.remove('theme-dark');
                }

                if (themeBtn) {
                    const themeIcons = { 'auto': '🌗', 'dark': '🌙', 'light': '☀️' };
                    themeBtn.innerHTML = themeIcons[APP_THEME] || '🌗';
                    themeBtn.title = `Theme: ${APP_THEME.charAt(0).toUpperCase() + APP_THEME.slice(1)}`;
                }
            }'''
            ),
            
            # 3. Bind the cyclic click event logic for the new button
            (
                r'''                toggleKeyboardBtn.addEventListener('click', () => {
                    keyboardDisabled = !keyboardDisabled;
                    if (keyboardDisabled) {
                        textarea.setAttribute('inputmode', 'none');
                        toggleKeyboardBtn.style.opacity = '0.5';
                    } else {
                        textarea.removeAttribute('inputmode');
                        toggleKeyboardBtn.style.opacity = '1';
                    }
                });''',
                r'''                toggleKeyboardBtn.addEventListener('click', () => {
                    keyboardDisabled = !keyboardDisabled;
                    if (keyboardDisabled) {
                        textarea.setAttribute('inputmode', 'none');
                        toggleKeyboardBtn.style.opacity = '0.5';
                    } else {
                        textarea.removeAttribute('inputmode');
                        toggleKeyboardBtn.style.opacity = '1';
                    }
                });

                const toggleThemeBtn = document.getElementById('toggle-theme');
                if (toggleThemeBtn) {
                    toggleThemeBtn.addEventListener('click', () => {
                        if (APP_THEME === 'auto') APP_THEME = 'dark';
                        else if (APP_THEME === 'dark') APP_THEME = 'light';
                        else APP_THEME = 'auto';
                        applyTheme();
                    });
                }'''
            ),
            
            # 4. Increment the version logic per the rules (Assuming patching from 6.4.0)
            (
                r'''<div class="footer-right">v6.4.0</div>''',
                r'''<div class="footer-right">v6.5.0</div>'''
            )
        ]
        
        # Apply Replacements
        for old_str, new_str in replacements:
            if old_str in content:
                content = content.replace(old_str, new_str)
            else:
                print(f"Warning: Could not find block starting with: {old_str[:40]}...")

        # Write output file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Successfully generated: {output_filename}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Run against the most up-to-date generated file
    input_file = 'svg_component_editor_v6_4_0.html'
    output_file = 'svg_component_editor_v6_5_0.html'
    patch_file(input_file, output_file)