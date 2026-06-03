import sys
import os

def patch_html():
    input_file = "bip39_converter_v1_11_0.html"
    output_file = "bip39_converter_v1_12_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # 1. Bump the application version dynamically
    content = content.replace("v1.11.0", "v1.12.0")

    # 2. Update the dynamic test script loader reference
    search_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_11_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_11_0_tests.js");
        document.body.appendChild(script);"""

    replace_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_12_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_12_0_tests.js");
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
    input_file = "bip39_converter_v1_11_0_tests.js"
    output_file = "bip39_converter_v1_12_0_tests.js"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # Target the end of TEST 2 to inject the standard test vector
    search_js = r"""        const expectedZerosMnemonic = `${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w3}`;
        const encodedZeros = await API.encodeMnemonic("00000000000000000000000000000000");
        assert(encodedZeros === expectedZerosMnemonic, 
            "encodeMnemonic properly evaluates 128 bits of entropy and appends correct 4-bit checksum using real words");"""

    replace_js = r"""        const expectedZerosMnemonic = `${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w3}`;
        const encodedZeros = await API.encodeMnemonic("00000000000000000000000000000000");
        assert(encodedZeros === expectedZerosMnemonic, 
            "encodeMnemonic properly evaluates 128 bits of entropy and appends correct 4-bit checksum using real words");

        // Validate specific exact vector (Safe check: only run if the actual English dictionary is loaded)
        if (realDict.includes("shell") && realDict.includes("hungry")) {
            const specificHex = "c56de84beafca421bc44284c89580321";
            const expectedSpecific = "shell hungry base sting ski awkward valve lunar erode enlist absorb drive";
            
            const encodedSpecific = await API.encodeMnemonic(specificHex);
            assert(encodedSpecific === expectedSpecific, "encodeMnemonic correctly translates specific standard entropy vector to exact expected phrase");
            
            const decodedSpecific = await API.decodeMnemonic(expectedSpecific);
            assert(decodedSpecific === specificHex, "decodeMnemonic correctly recovers exact standard hex vector from specific phrase");
        }"""

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
        print("v1.12.0 Upgrade Complete. Specific test vector added.")