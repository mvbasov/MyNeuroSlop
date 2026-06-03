import sys

def patch_html():
    input_file = "bip39_converter_v1_6_0.html"
    output_file = "bip39_converter_v1_7_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # 1. Bump the application version gracefully
    content = content.replace("v1.6.0", "v1.7.0")

    # 2. Update the dynamic test script loader reference
    search_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_6_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_6_0_tests.js");
        document.body.appendChild(script);"""

    replace_html_script = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_7_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_7_0_tests.js");
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
    input_file = "bip39_converter_v1_6_0_tests.js"
    output_file = "bip39_converter_v1_7_0_tests.js"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return False

    # Target the entire block for Test 2 and Test 3
    search_js = r"""        // --- TEST 2: BIP-39 Dictionary Mathematical Encoding ---
        const testWords = Array(2048).fill("").map((_, i) => "word" + i);
        API.setWordlist(testWords);
        
        // 16 bytes of pure zero (0x00) hashed with SHA-256 starts with 3747...
        // 4-bit checksum is '3' (0011).
        // 128 zeros + 0011 checksum = 132 bits = 12 words (Last word index is 3 -> `word3`)
        const encodedZeros = await API.encodeMnemonic("00000000000000000000000000000000");
        assert(encodedZeros === "word0 word0 word0 word0 word0 word0 word0 word0 word0 word0 word0 word3", 
            "encodeMnemonic properly evaluates 128 bits of entropy and appends correct 4-bit checksum");

        // --- TEST 3: Validation and Checksum Rejection ---
        let threwError = false;
        try {
            // Using 'word2' changes the checksum mathematically, which must trigger a hash fail.
            await API.decodeMnemonic("word0 word0 word0 word0 word0 word0 word0 word0 word0 word0 word0 word2");
        } catch (e) { threwError = e.message.includes("Checksum mismatch"); }
        assert(threwError, "decodeMnemonic aggressively catches and rejects invalid checksum modifications");

        let lengthError = false;
        try { await API.decodeMnemonic("word0 word0 word0"); } 
        catch(e) { lengthError = e.message.includes("Invalid length"); }
        assert(lengthError, "decodeMnemonic rejects invalid mnemonic lengths (< 12 words)");"""

    # Replace it with dynamic logic that uses the real words from the user's dictionary
    replace_js = r"""        // --- TEST 2: BIP-39 Dictionary Mathematical Encoding ---
        // Dynamically fetch the 1st (index 0), 3rd (index 2), and 4th (index 3) words 
        // from the actual loaded dictionary instead of using a synthetic mock array.
        const realDict = API.getWordlist();
        const w0 = realDict[0];
        const w2 = realDict[2];
        const w3 = realDict[3];
        
        // 16 bytes of pure zero (0x00) hashed with SHA-256 starts with 3747...
        // 4-bit checksum is '3' (0011). Last word index is 3.
        const expectedZerosMnemonic = `${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w3}`;
        const encodedZeros = await API.encodeMnemonic("00000000000000000000000000000000");
        assert(encodedZeros === expectedZerosMnemonic, 
            "encodeMnemonic properly evaluates 128 bits of entropy and appends correct 4-bit checksum using real words");

        // --- TEST 3: Validation and Checksum Rejection ---
        let threwError = false;
        try {
            // Using w2 changes the checksum mathematically, which must trigger a hash fail.
            await API.decodeMnemonic(`${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w0} ${w2}`);
        } catch (e) { threwError = e.message.includes("Checksum mismatch"); }
        assert(threwError, "decodeMnemonic aggressively catches and rejects invalid checksum modifications");

        let lengthError = false;
        try { await API.decodeMnemonic(`${w0} ${w0} ${w0}`); } 
        catch(e) { lengthError = e.message.includes("Invalid length"); }
        assert(lengthError, "decodeMnemonic rejects invalid mnemonic lengths (< 12 words)");"""

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
        print("v1.7.0 Upgrade Complete. Synthetic words replaced with dynamic dictionary hooks.")