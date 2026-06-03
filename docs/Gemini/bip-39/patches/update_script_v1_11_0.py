import sys
import os

def patch_html():
    input_file = "bip39_converter_v1_10_0.html"
    output_file = "bip39_converter_v1_11_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # 1. Bump the application version dynamically
    content = content.replace("v1.10.0", "v1.11.0")

    # 2. Update the dynamic test script loader reference
    search_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_10_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_10_0_tests.js");
        document.body.appendChild(script);"""

    replace_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_11_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_11_0_tests.js");
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
    input_file = "bip39_converter_v1_10_0_tests.js"
    output_file = "bip39_converter_v1_11_0_tests.js"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # Target the end of TEST 3 to inject TEST 4 (Limits) and TEST 5 (Normalization),
    # pushing the DOM tests to TEST 6.
    search_js = r"""        let lengthError = false;
        try { await API.decodeMnemonic(`${w0} ${w0} ${w0}`); } 
        catch(e) { lengthError = e.message.includes("Invalid length"); }
        assert(lengthError, "decodeMnemonic rejects invalid mnemonic lengths (< 12 words)");

        // --- TEST 4: DOM Input Debounce & Sync Pipeline ---"""

    replace_js = r"""        let lengthError = false;
        try { await API.decodeMnemonic(`${w0} ${w0} ${w0}`); } 
        catch(e) { lengthError = e.message.includes("Invalid length"); }
        assert(lengthError, "decodeMnemonic rejects invalid mnemonic lengths (< 12 words)");

        // --- TEST 4: Entropy Length Validation ---
        let tooShortError = false;
        try { await API.encodeMnemonic("ff"); }
        catch(e) { tooShortError = e.message.includes("Invalid entropy"); }
        assert(tooShortError, "encodeMnemonic rejects entropy shorter than 32 hex chars (128 bits)");
        
        let tooLongError = false;
        try { await API.encodeMnemonic("f".repeat(66)); }
        catch(e) { tooLongError = e.message.includes("Invalid entropy"); }
        assert(tooLongError, "encodeMnemonic rejects entropy longer than 64 hex chars (256 bits)");

        let nonHexError = false;
        try { await API.encodeMnemonic("invalidhexstring0000000000000000"); }
        catch(e) { nonHexError = e.message.includes("Invalid hex"); }
        assert(nonHexError, "encodeMnemonic rejects non-hexadecimal characters immediately");

        // --- TEST 5: Parser Case & Whitespace Normalization ---
        // Ensure decodeMnemonic handles mixed case, extra spaces, and newlines correctly without failing
        const messyPhrase = `  ${w0.toUpperCase()}   \n  ${w0} \t ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w2}  `;
        let normalizedError = false;
        try { await API.decodeMnemonic(messyPhrase); }
        catch(e) { normalizedError = e.message.includes("Checksum mismatch"); }
        assert(normalizedError, "decodeMnemonic normalizes extreme whitespace and mixed-case inputs before processing");

        // --- TEST 6: DOM Input Debounce & Sync Pipeline ---"""

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
        print("v1.11.0 Upgrade Complete. Edge case and normalization tests added.")