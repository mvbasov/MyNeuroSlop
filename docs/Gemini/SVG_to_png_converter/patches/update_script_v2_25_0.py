import os

def update_files():
    html_file = "svg_to_png_converter_v2_24_0.html"
    js_file = "svg_to_png_converter_v2_24_0_tests.js"
    
    html_out = "svg_to_png_converter_v2_25_0.html"
    js_out = "svg_to_png_converter_v2_25_0_tests.js"

    # ---------------------------------------------------------
    # 1. Update the HTML File
    # ---------------------------------------------------------
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        html_search_1 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.24.0</span>"""
        html_replace_1 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.25.0</span>"""
        html_content = html_content.replace(html_search_1, html_replace_1)

        html_search_2 = r"""script.src = 'svg_to_png_converter_v2_24_0_tests.js';"""
        html_replace_2 = r"""script.src = 'svg_to_png_converter_v2_25_0_tests.js';"""
        html_content = html_content.replace(html_search_2, html_replace_2)

        html_search_3 = r"""script.onerror = () => console.error("❌ Failed to load test_suite_v2_24_0.js. Ensure it is in the same directory.");"""
        html_replace_3 = r"""script.onerror = () => console.error("❌ Failed to load test_suite_v2_25_0.js. Ensure it is in the same directory.");"""
        html_content = html_content.replace(html_search_3, html_replace_3)

        with open(html_out, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Successfully updated {html_out}")
    else:
        print(f"❌ Could not find {html_file}")


    # ---------------------------------------------------------
    # 2. Update the JS Test File
    # ---------------------------------------------------------
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # Inject the Enforcer mechanism to overpower the internal app toast timeouts
        js_search_1 = r"""    // Show enlarged, centered final toast
    setTimeout(() => {
        const toast = document.querySelector('#status-toast');
        if (toast) {
            if (window._toastTimer) clearTimeout(window._toastTimer);
            
            // Store original styles to restore later
            const originalStyles = {
                position: toast.style.position,
                top: toast.style.top,
                left: toast.style.left,
                transform: toast.style.transform,
                bottom: toast.style.bottom,
                right: toast.style.right,
                padding: toast.style.padding,
                fontSize: toast.style.fontSize,
                borderRadius: toast.style.borderRadius,
                boxShadow: toast.style.boxShadow
            };
            
            // Center and enlarge (2x original size)
            toast.style.position = 'fixed';
            toast.style.top = '50%';
            toast.style.left = '50%';
            toast.style.transform = 'translate(-50%, -50%)';
            toast.style.bottom = 'auto';
            toast.style.right = 'auto';
            
            // Double the original toast dimensions
            toast.style.padding = '24px 48px';     // original: 12px 24px
            toast.style.fontSize = '1.8rem';       // original: 0.9rem
            toast.style.borderRadius = '16px';     // original: 8px
            toast.style.boxShadow = '0 8px 24px rgba(0,0,0,0.25)'; // deeper shadow
            
            toast.textContent = `🧪 Tests: ${passed} passed, ${failed} failed. App reset.`;
            toast.classList.add('show');
            
            window._toastTimer = setTimeout(() => {
                toast.classList.remove('show');
                // Restore original styles
                toast.style.position = originalStyles.position || '';
                toast.style.top = originalStyles.top || '';
                toast.style.left = originalStyles.left || '';
                toast.style.transform = originalStyles.transform || '';
                toast.style.bottom = originalStyles.bottom || '';
                toast.style.right = originalStyles.right || '';
                toast.style.padding = originalStyles.padding || '';
                toast.style.fontSize = originalStyles.fontSize || '';
                toast.style.borderRadius = originalStyles.borderRadius || '';
                toast.style.boxShadow = originalStyles.boxShadow || '';
            }, 7000);
        }
    }, 800);"""

        js_replace_1 = r"""    // Show enlarged, centered final toast (with forced persistence)
    setTimeout(() => {
        const toast = document.querySelector('#status-toast');
        if (toast) {
            if (window._toastTimer) clearTimeout(window._toastTimer);
            if (window._toastEnforcer) clearInterval(window._toastEnforcer);
            
            // Store original styles to restore later
            const originalStyles = {
                position: toast.style.position,
                top: toast.style.top,
                left: toast.style.left,
                transform: toast.style.transform,
                bottom: toast.style.bottom,
                right: toast.style.right,
                padding: toast.style.padding,
                fontSize: toast.style.fontSize,
                borderRadius: toast.style.borderRadius,
                boxShadow: toast.style.boxShadow,
                opacity: toast.style.opacity
            };
            
            const enforceToast = () => {
                toast.style.position = 'fixed';
                toast.style.top = '50%';
                toast.style.left = '50%';
                toast.style.transform = 'translate(-50%, -50%)';
                toast.style.bottom = 'auto';
                toast.style.right = 'auto';
                toast.style.padding = '24px 48px';
                toast.style.fontSize = '1.8rem';
                toast.style.borderRadius = '16px';
                toast.style.boxShadow = '0 8px 24px rgba(0,0,0,0.25)';
                toast.style.opacity = '1';
                
                const expectedText = `🧪 Tests: ${passed} passed, ${failed} failed. App reset.`;
                if (toast.textContent !== expectedText) {
                    toast.textContent = expectedText;
                    toast.classList.add('show');
                }
            };

            enforceToast();
            // Forcefully maintain the toast against internal app timeouts and injections
            window._toastEnforcer = setInterval(enforceToast, 100);
            
            window._toastTimer = setTimeout(() => {
                clearInterval(window._toastEnforcer);
                toast.classList.remove('show');
                // Restore original styles
                toast.style.position = originalStyles.position || '';
                toast.style.top = originalStyles.top || '';
                toast.style.left = originalStyles.left || '';
                toast.style.transform = originalStyles.transform || '';
                toast.style.bottom = originalStyles.bottom || '';
                toast.style.right = originalStyles.right || '';
                toast.style.padding = originalStyles.padding || '';
                toast.style.fontSize = originalStyles.fontSize || '';
                toast.style.borderRadius = originalStyles.borderRadius || '';
                toast.style.boxShadow = originalStyles.boxShadow || '';
                toast.style.opacity = originalStyles.opacity || '';
            }, 7000);
        }
    }, 800);"""
        js_content = js_content.replace(js_search_1, js_replace_1)

        # Bump internal script version string
        js_search_2 = r"""console.log("%c💡 test_suite_v2_24_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_replace_2 = r"""console.log("%c💡 test_suite_v2_25_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");"""
        js_content = js_content.replace(js_search_2, js_replace_2)

        with open(js_out, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Successfully updated {js_out}")
    else:
        print(f"❌ Could not find {js_file}")

if __name__ == "__main__":
    update_files()