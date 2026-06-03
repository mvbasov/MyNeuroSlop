import sys

def patch_html():
    input_file = "bip39_converter_v1_4_1.html"
    output_file = "bip39_converter_v1_5_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    content = content.replace("v1.4.1", "v1.5.0")

    search_str = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_4_1_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_4_1_tests.js");
        document.body.appendChild(script);"""

    replace_str = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_5_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_5_0_tests.js");
        document.body.appendChild(script);"""

    if search_str not in content:
        print(f"Error: Target HTML string not found in {input_file}.")
        return False
        
    content = content.replace(search_str, replace_str)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_file}")
    return True

def patch_js():
    input_file = "bip39_converter_v1_4_1_tests.js"
    output_file = "bip39_converter_v1_5_0_tests.js"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    search_str = r"""        // The SHA256 of 32 'f's dictates the last word index will ALWAYS be mathematically 2040.
        const expectedWord = window.WORDLIST ? window.WORDLIST[2040] : "youth";
        const generatedPhrase = API.mnemonicInput.value.trim().split(/\s+/);
        const lastWord = generatedPhrase[generatedPhrase.length - 1];
        
        assert(lastWord === expectedWord || API.mnemonicInput.value.includes("word2040"), "DOM seamlessly auto-generates mnemonic on hex input after debounce");"""

    replace_str = r"""        // Dynamically ask the internal cryptographic engine what the phrase SHOULD be, 
        // completely eliminating the need to hardcode index guesses or dictionary words.
        const expectedPhrase = await API.encodeMnemonic("ffffffffffffffffffffffffffffffff");
        
        assert(API.mnemonicInput.value === expectedPhrase, "DOM seamlessly auto-generates mnemonic on hex input after debounce");"""

    if search_str not in content:
        print(f"Error: Target JS string not found in {input_file}.")
        return False

    content = content.replace(search_str, replace_str)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_file}")
    return True

if __name__ == "__main__":
    html_success = patch_html()
    js_success = patch_js()
    if html_success and js_success:
        print("v1.5.0 Upgrade Complete.")