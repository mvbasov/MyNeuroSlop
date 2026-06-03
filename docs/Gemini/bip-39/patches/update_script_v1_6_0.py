import sys

def patch_html():
    input_file = "bip39_converter_v1_5_0.html"
    output_file = "bip39_converter_v1_6_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # 1. Bump the application version gracefully
    content = content.replace("v1.5.0", "v1.6.0")

    # 2. Expose getWordlist() to the secure test API bridge
    search_html_api = r"""            hexError,
            mnemonicError,
            setWordlist: (arr) => { WORDLIST = arr; }
        };"""

    replace_html_api = r"""            hexError,
            mnemonicError,
            setWordlist: (arr) => { WORDLIST = arr; },
            getWordlist: () => WORDLIST
        };"""

    # 3. Update the dynamic test script loader reference
    search_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_5_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_5_0_tests.js");
        document.body.appendChild(script);"""

    replace_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_6_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_6_0_tests.js");
        document.body.appendChild(script);"""

    if search_html_api not in content:
        print(f"Error: Target API string not found in {input_file}.")
        return False
        
    content = content.replace(search_html_api, replace_html_api)
    content = content.replace(search_html_script, replace_html_script)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_file}")
    return True


def patch_js():
    input_file = "bip39_converter_v1_5_0_tests.js"
    output_file = "bip39_converter_v1_6_0_tests.js"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # Inject "TEST 0: Dictionary Integrity" at the very start of the testing block,
    # mapping your 1-based decimal inputs into 0-based array indexes.
    search_js = r"""    try {
        // --- TEST 1: Binary / Hex Transcoding Math ---"""

    replace_js = r"""    try {
        // --- TEST 0: BIP-39 Dictionary Integrity ---
        // Validating user-requested words by their 1-based decimal index (array is 0-based, so minus 1)
        if (typeof API.getWordlist === 'function') {
            const dict = API.getWordlist();
            assert(dict[1150] === "more", `Dictionary check: 1151st word is 'more' (Found: ${dict[1150]})`);
            assert(dict[652] === "face", `Dictionary check: 653rd word is 'face' (Found: ${dict[652]})`);
            assert(dict[453] === "december", `Dictionary check: 454th word is 'december' (Found: ${dict[453]})`);
            assert(dict[1326] === "place", `Dictionary check: 1327th word is 'place' (Found: ${dict[1326]})`);
        } else {
            console.error("❌ FAIL: API.getWordlist is not defined. Ensure HTML is updated.");
            failed++;
        }

        // --- TEST 1: Binary / Hex Transcoding Math ---"""

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
        print("v1.6.0 Upgrade Complete. Dictionary Validation Applied.")