import sys
import os

def patch_html():
    input_file = "bip39_converter_v1_9_0.html"
    output_file = "bip39_converter_v1_10_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # 1. Bump the application version dynamically
    content = content.replace("v1.9.0", "v1.10.0")

    # 2. Update the dynamic test script loader reference
    search_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_9_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_9_0_tests.js");
        document.body.appendChild(script);"""

    replace_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_10_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_10_0_tests.js");
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
    input_file = "bip39_converter_v1_9_0_tests.js"
    output_file = "bip39_converter_v1_10_0_tests.js"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # Target the verbose console summary block and revert it back to just the table
    search_js = r"""    // --- UI ENFORCER TOAST ---
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
    
    console.table({"Total Tests": total, "Passed": passed, "Failed": failed});"""

    replace_js = r"""    // --- UI ENFORCER TOAST ---
    const t = document.getElementById('app-toast');
    const total = passed + failed;
    console.table({"Total Tests": total, "Passed": `${passed} ✅`, "Failed": `${failed}${failed > 0 ? ' ❌' : ' ✅'}`});"""

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
        print("v1.10.0 Upgrade Complete. Reverted to clean console table.")