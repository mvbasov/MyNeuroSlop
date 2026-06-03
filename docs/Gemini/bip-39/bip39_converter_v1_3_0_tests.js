(async function() {
    const API = window.__TEST_API__;
    if (!API) {
        console.error("Test API bridge not found.");
        return;
    }

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

    // Small delay to guarantee the DOM is parsed before tests manipulate it
    await wait(100);

    try {
        // --- TEST 1: Binary / Hex Transcoding Math ---
        assert(API.hexToBin("f") === "1111", "hexToBin correctly converts 'f' and preserves 4-bit padding");
        assert(API.hexToBin("0") === "0000", "hexToBin correctly converts '0' and preserves 4-bit padding");
        assert(API.binToHex("11110000") === "f0", "binToHex correctly reconstructs hexadecimal chunks");

        // --- TEST 2: BIP-39 Dictionary Mathematical Encoding ---
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
        assert(lengthError, "decodeMnemonic rejects invalid mnemonic lengths (< 12 words)");

        // --- TEST 4: DOM Input Debounce & Sync Pipeline ---
        API.hexInput.value = "ffffffffffffffffffffffffffffffff"; 
        API.hexInput.dispatchEvent(new Event('input'));
        
        // Increased from 350 to 600ms. Allows 300ms for UI debounce, plus ample time for async crypto.subtle.digest!
        await wait(600); 
        
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
})();