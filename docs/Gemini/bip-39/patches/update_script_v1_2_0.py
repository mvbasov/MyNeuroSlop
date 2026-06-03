import sys

def patch_file():
    input_file = "bip39_converter_v1_1_0.html"
    output_file = "bip39_converter_v1_2_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # 1. Bump the application version gracefully
    content = content.replace("v1.1.0", "v1.2.0")

    # 2. Extract the massive embedded unit test block
    search_str = r"""    // ============================================================================
    // 4. MICRO UNIT TEST SYSTEM (Embedded)
    // ============================================================================
    if (window.location.search.includes('test=')) {
        window.__TEST_API__ = {
            isTesting: true,
            encodeMnemonic,
            decodeMnemonic,
            hexToBin,
            binToHex,
            hexInput,
            mnemonicInput,
            hexError,
            mnemonicError,
            setWordlist: (arr) => { WORDLIST = arr; }
        };
        
        // Execute suite slightly asynchronously to allow DOM parsing completion
        setTimeout(async () => {
            const API = window.__TEST_API__;
            console.log("=== BEGINNING BIP-39 CORE TESTS ===");
            let passed = 0;
            let failed = 0;

            function assert(condition, testName) {
                if (condition) {
                    console.log(`✅ PASS: ${testName}`);
                    passed++;
                } else {
                    console.error(`❌ FAIL: ${testName}`);
                    failed++;
                }
            }

            async function wait(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

            try {
                // --- TEST 1: Binary / Hex Transcoding Math ---
                assert(API.hexToBin("f") === "1111", "hexToBin correctly converts 'f' and preserves 4-bit padding");
                assert(API.hexToBin("0") === "0000", "hexToBin correctly converts '0' and preserves 4-bit padding");
                assert(API.binToHex("11110000") === "f0", "binToHex correctly reconstructs hexadecimal chunks");

                // --- TEST 2: BIP-39 Dictionary Mathematical Encoding ---
                const testWords = Array(2048).fill("").map((_, i) => "word" + i);
                API.setWordlist(testWords);
                
                // 128 zeros + 0110 checksum = 132 bits = 12 words (Last word is `word6`)
                const encodedZeros = await API.encodeMnemonic("00000000000000000000000000000000");
                assert(encodedZeros === "word0 word0 word0 word0 word0 word0 word0 word0 word0 word0 word0 word6", 
                    "encodeMnemonic properly evaluates 128 bits of entropy and appends correct 4-bit checksum");

                // --- TEST 3: Validation and Checksum Rejection ---
                let threwError = false;
                try {
                    await API.decodeMnemonic("word0 word0 word0 word0 word0 word0 word0 word0 word0 word0 word0 word5");
                } catch (e) { threwError = e.message.includes("Checksum mismatch"); }
                assert(threwError, "decodeMnemonic aggressively catches and rejects invalid checksum modifications");

                let lengthError = false;
                try { await API.decodeMnemonic("word0 word0 word0"); } 
                catch(e) { lengthError = e.message.includes("Invalid length"); }
                assert(lengthError, "decodeMnemonic rejects invalid mnemonic lengths (< 12 words)");

                // --- TEST 4: DOM Input Debounce & Sync Pipeline ---
                API.hexInput.value = "ffffffffffffffffffffffffffffffff"; 
                API.hexInput.dispatchEvent(new Event('input'));
                await wait(350); // Wait for the 300ms UI debounce
                
                assert(API.mnemonicInput.value.includes("word2040"), "DOM seamlessly auto-generates mnemonic on hex input after debounce");

                document.getElementById('btn-clear-hex').click();
                assert(API.mnemonicInput.value === "", "DOM clearing safely resets both input buffers instantly");

            } catch (err) {
                console.error("Test execution aborted:", err);
                failed++;
            }

            // --- UI ENFORCER TOAST ---
            const t = document.getElementById('app-toast');
            const total = passed + failed;
            console.table({"Total Tests": total, "Passed": passed, "Failed": failed});
            
            t.textContent = `Tests Complete! Passed: ${passed}/${total}`;
            t.className = 'toast show test-toast' + (failed > 0 ? ' failed' : '');
            
            let enforcementTicks = 0;
            const enforcer = setInterval(() => {
                t.className = 'toast show test-toast' + (failed > 0 ? ' failed' : '');
                t.style.opacity = '1';
                t.style.transform = 'translateX(-50%) translateY(0)';
                enforcementTicks++;
                if (enforcementTicks > 14) { // 14 ticks * 500ms = 7 seconds
                    clearInterval(enforcer);
                    t.classList.remove('show');
                    API.isTesting = false; // Release the internal toast blocker
                }
            }, 500);
        }, 100);
    }"""

    # 3. Replace with a dynamic external script loader
    replace_str = r"""    // ============================================================================
    // 4. MICRO UNIT TEST SYSTEM (Dynamic Loader)
    // ============================================================================
    if (window.location.search.includes('test=')) {
        window.__TEST_API__ = {
            isTesting: true,
            encodeMnemonic,
            decodeMnemonic,
            hexToBin,
            binToHex,
            hexInput,
            mnemonicInput,
            hexError,
            mnemonicError,
            setWordlist: (arr) => { WORDLIST = arr; }
        };
        
        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_2_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_2_0_tests.js");
        document.body.appendChild(script);
    }"""

    if search_str not in content:
        print("Error: Target string not found. Ensure you are running this against the clean v1.1.0 file.")
    else:
        content = content.replace(search_str, replace_str)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_file}")

if __name__ == "__main__":
    patch_file()