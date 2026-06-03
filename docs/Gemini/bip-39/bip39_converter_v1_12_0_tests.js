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

        // --- TEST 1: Binary / Hex Transcoding Math ---
        assert(API.hexToBin("f") === "1111", "hexToBin correctly converts 'f' and preserves 4-bit padding");
        assert(API.hexToBin("0") === "0000", "hexToBin correctly converts '0' and preserves 4-bit padding");
        assert(API.binToHex("11110000") === "f0", "binToHex correctly reconstructs hexadecimal chunks");

        // --- TEST 2: BIP-39 Dictionary Mathematical Encoding ---
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

        // Validate specific exact vector (Safe check: only run if the actual English dictionary is loaded)
        if (realDict.includes("shell") && realDict.includes("hungry")) {
            const specificHex = "c56de84beafca421bc44284c89580321";
            const expectedSpecific = "shell hungry base sting ski awkward valve lunar erode enlist absorb drive";
            
            const encodedSpecific = await API.encodeMnemonic(specificHex);
            assert(encodedSpecific === expectedSpecific, "encodeMnemonic correctly translates specific standard entropy vector to exact expected phrase");
            
            const decodedSpecific = await API.decodeMnemonic(expectedSpecific);
            assert(decodedSpecific === specificHex, "decodeMnemonic correctly recovers exact standard hex vector from specific phrase");
        }

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

        // --- TEST 6: DOM Input Debounce & Sync Pipeline ---
        API.hexInput.value = "ffffffffffffffffffffffffffffffff"; 
        API.hexInput.dispatchEvent(new Event('input'));
        
        // Increased from 350 to 600ms. Allows 300ms for UI debounce, plus ample time for async crypto.subtle.digest!
        await wait(600); 
        
        // Dynamically ask the internal cryptographic engine what the phrase SHOULD be, 
        // completely eliminating the need to hardcode index guesses or dictionary words.
        const expectedPhrase = await API.encodeMnemonic("ffffffffffffffffffffffffffffffff");
        
        assert(API.mnemonicInput.value === expectedPhrase, "DOM seamlessly auto-generates mnemonic on hex input after debounce");

        document.getElementById('btn-clear-hex').click();
        assert(API.mnemonicInput.value === "", "DOM clearing safely resets both input buffers instantly");

    } catch (err) {
        console.error("Test execution aborted:", err);
        failed++;
    }

    // --- UI ENFORCER TOAST ---
    const t = document.getElementById('app-toast');
    const total = passed + failed;
    console.table({"Total Tests": total, "Passed": `${passed} ✅`, "Failed": `${failed}${failed > 0 ? ' ❌' : ' ✅'}`});
    
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
            t.style.opacity = ''; // Clean up inline opacity so CSS fade can execute
            t.style.transform = ''; // Clean up inline transform
            API.isTesting = false; // Release the internal toast blocker
        }
    }, 500);
})();
