import sys
import os

def patch_html():
    input_file = "bip39_converter_v1_7_0.html"
    output_file = "bip39_converter_v1_8_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # 1. Bump the application version dynamically
    content = content.replace("v1.7.0", "v1.8.0")

    # 2. Update the dynamic test script loader reference
    search_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_7_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_7_0_tests.js");
        document.body.appendChild(script);"""

    replace_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_8_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_8_0_tests.js");
        document.body.appendChild(script);"""

    if search_html_script not in content:
        print(f"Error: Target HTML string not found in {input_file}.")
        return False
        
    content = content.replace(search_html_script, replace_html_script)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_file}")
    return True

def patch_js():
    input_file = "bip39_converter_v1_7_0_tests.js"
    output_file = "bip39_converter_v1_8_0_tests.js"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # Target the UI Enforcer Toast block to inject a structured text console summary
    search_js = r"""    // --- UI ENFORCER TOAST ---
    const t = document.getElementById('app-toast');
    const total = passed + failed;
    console.table({"Total Tests": total, "Passed": passed, "Failed": failed});
    
    t.textContent = `Tests Complete! Passed: ${passed}/${total}`;
    t.className = 'toast show test-toast' + (failed > 0 ? ' failed' : '');"""

    replace_js = r"""    // --- UI ENFORCER TOAST ---
    const t = document.getElementById('app-toast');
    const total = passed + failed;
    
    // --- CONSOLE SUMMARY ---
    console.log("\n=======================================");
    console.log("          BIP-39 TEST SUMMARY          ");
    console.log("=======================================");
    console.log(`  Total Tests : ${total}`);
    console.log(`  Passed      : ${passed} ✅`);
    console.log(`  Failed      : ${failed} ${failed > 0 ? '❌' : ' '}`);
    console.log("=======================================\n");
    
    console.table({"Total Tests": total, "Passed": passed, "Failed": failed});
    
    t.textContent = `Tests Complete! Passed: ${passed}/${total}`;
    t.className = 'toast show test-toast' + (failed > 0 ? ' failed' : '');"""

    if search_js not in content:
        print(f"Error: Target JS string not found in {input_file}.")
        return False

    content = content.replace(search_js, replace_js)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_file}")
    return True

if __name__ == "__main__":
    html_success = patch_html()
    js_success = patch_js()
    if html_success and js_success:
        print("v1.8.0 Upgrade Complete. Console summary added.")