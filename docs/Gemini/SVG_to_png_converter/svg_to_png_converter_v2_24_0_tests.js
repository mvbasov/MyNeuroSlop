// test_suite_v2_22_0.js - Final version with enlarged final toast (2x size)

window.__runTests = async function() {
    console.log("%c🚀 Starting Automated Unit Tests...", "color: #4A90E2; font-weight: bold; font-size: 14px;");
    let passed = 0, failed = 0;
    
    const api = window.__TEST_API__;
    if (!api) {
        console.error("%c❌ FATAL: __TEST_API__ not exposed. Ensure URL contains '?test=' and the app loaded correctly.", "color: #f44336; font-weight: bold;");
        return;
    }

    // ==================== HELPER FUNCTIONS ====================
    function assert(name, actual, expected, message = "") {
        if (actual === expected) {
            console.log(`%c✅ PASS: ${name}`, "color: #4CAF50; font-weight: bold;");
            passed++;
            return true;
        } else {
            console.error(`❌ FAIL: ${name}\n   Expected: ${expected}\n   Actual:   ${actual} ${message ? "\n   " + message : ""}`);
            failed++;
            return false;
        }
    }

    function assertTrue(name, condition, message = "") {
        if (condition) {
            console.log(`%c✅ PASS: ${name}`, "color: #4CAF50; font-weight: bold;");
            passed++;
            return true;
        } else {
            console.error(`❌ FAIL: ${name}\n   Condition not met. ${message}`);
            failed++;
            return false;
        }
    }

    function assertStartsWith(name, str, prefix) {
        const result = str.startsWith(prefix);
        if (result) {
            console.log(`%c✅ PASS: ${name}`, "color: #4CAF50; font-weight: bold;");
            passed++;
        } else {
            console.error(`❌ FAIL: ${name}\n   Expected string to start with: "${prefix}"\n   Actual start: "${str.substring(0, prefix.length)}..."`);
            failed++;
        }
        return result;
    }

    function base64ToBytes(base64) {
        const binaryString = atob(base64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes;
    }

    function getFaviconHref() {
        const link = document.querySelector('.favicon-link');
        return link ? link.href : '';
    }

    function isDefaultFavicon(href) {
        return href.includes('rect') && 
               href.includes('IMG') && 
               (href.includes('%234A90E2') || href.includes('#4A90E2'));
    }

    function loadTestSVG(svgString, filename = "test.svg") {
        return new Promise((resolve, reject) => {
            const canvas = document.querySelector('#svg-to-png-app canvas');
            const errorDiv = document.querySelector('#svg-to-png-app #svg-error');
            if (!canvas) {
                reject(new Error("Canvas element not found"));
                return;
            }
            api.loadSVGToCanvas(svgString, filename);
            let attempts = 0;
            const interval = setInterval(() => {
                if (canvas.width > 0 && canvas.height > 0 && errorDiv.style.display !== 'block') {
                    clearInterval(interval);
                    setTimeout(() => resolve(), 100);
                    return;
                }
                if (errorDiv.style.display === 'block') {
                    clearInterval(interval);
                    setTimeout(() => resolve(), 100);
                    return;
                }
                attempts++;
                if (attempts > 60) {
                    clearInterval(interval);
                    reject(new Error("Timeout waiting for SVG to load"));
                }
            }, 100);
        });
    }

    async function testEdgeCase(svgString, expectErrorOrClear) {
        const canvas = document.querySelector('#svg-to-png-app canvas');
        const errorDiv = document.querySelector('#svg-to-png-app #svg-error');
        api.loadSVGToCanvas(svgString, "edge.svg");
        await new Promise(r => setTimeout(r, 600));
        const hasError = errorDiv.style.display === 'block';
        const canvasCleared = canvas.width === 0 && canvas.height === 0;
        const condition = expectErrorOrClear ? (hasError || canvasCleared) : (canvas.width > 0);
        return condition;
    }

    // ==================== RESET FUNCTION ====================
    function resetAppToInitialState() {
        const app = document.getElementById('svg-to-png-app');
        const svgInput = app.querySelector('#svg-input');
        const chkPrependPrefix = app.querySelector('#chk-prepend-prefix');
        const chkWrap80 = app.querySelector('#chk-wrap-80');
        const chkWrapLink = app.querySelector('#chk-wrap-link');
        const selFormat = app.querySelector('#sel-format');
        const liveDataUrlInput = app.querySelector('#live-data-url');
        
        const defaultSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#4A90E2" />
  <text x="50" y="58" font-family="sans-serif" font-size="24" font-weight="bold" fill="white" text-anchor="middle">SVG</text>
</svg>`;
        
        svgInput.value = defaultSVG;
        if (chkPrependPrefix) chkPrependPrefix.checked = true;
        if (chkWrap80) chkWrap80.checked = false;
        if (chkWrapLink) chkWrapLink.checked = false;
        if (selFormat) selFormat.value = 'image/png';
        if (liveDataUrlInput) liveDataUrlInput.value = '';
        
        api.loadSVGToCanvas(defaultSVG, 'edited_image.png', true);
        
        setTimeout(() => {
            if (api.syncDataUrl) api.syncDataUrl();
            const errorDiv = app.querySelector('#svg-error');
            if (errorDiv) errorDiv.style.display = 'none';
        }, 100);
        
        console.log("%c🔄 App reset to initial state.", "color: #2196F3; font-weight: bold;");
    }

    // ==================== XML FORMAT TESTS ====================
    console.log("%c📝 Running XML Formatting Tests...", "color: #FF9800; font-weight: bold;");
    assert("formatXML: Empty <svg> keeps closing tag", 
        api.formatXML("<svg></svg>"), "<svg></svg>");
    assert("formatXML: Empty <g> keeps closing tag", 
        api.formatXML("<svg><g></g></svg>"), "<svg>\n  <g></g>\n</svg>");
    assert("formatXML: Empty <circle> collapses", 
        api.formatXML("<svg><circle></circle></svg>"), "<svg>\n  <circle/>\n</svg>");
    assert("formatXML: Base format stripping", 
        api.formatXML('<circle   r="5"  />'), '<circle r="5"/>');

    // ==================== PNG FORMAT TESTS ====================
    console.log("%c📝 Running PNG Format Tests...", "color: #FF9800; font-weight: bold;");
    try {
        const testSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
            <rect width="100" height="100" fill="red"/>
            <circle cx="50" cy="50" r="30" fill="blue"/>
        </svg>`;
        await loadTestSVG(testSVG);
        const canvas = document.querySelector('#svg-to-png-app canvas');
        const pngDataURL = canvas.toDataURL('image/png');
        assertStartsWith("PNG: Data URL format", pngDataURL, "data:image/png;base64,");
        const base64Part = pngDataURL.split(',')[1];
        assertTrue("PNG: Base64 string exists and non-empty", base64Part && base64Part.length > 100);
        const pngBytes = base64ToBytes(base64Part);
        const pngSignature = [137, 80, 78, 71, 13, 10, 26, 10];
        let signatureValid = true;
        for (let i = 0; i < 8; i++) if (pngBytes[i] !== pngSignature[i]) { signatureValid = false; break; }
        assertTrue("PNG: Valid PNG file signature", signatureValid);
        assertTrue("PNG: Canvas has drawn content", canvas.width > 0 && canvas.height > 0);
    } catch (err) {
        console.error("PNG test error:", err);
        assertTrue("PNG: Test execution should not throw", false, err.message);
    }

    // ==================== BMP FORMAT TESTS ====================
    console.log("%c📝 Running BMP Format Tests...", "color: #FF9800; font-weight: bold;");
    try {
        const testSVG2 = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50" width="50" height="50">
            <rect width="50" height="50" fill="green"/>
            <text x="25" y="32" font-size="20" fill="white" text-anchor="middle">BMP</text>
        </svg>`;
        await loadTestSVG(testSVG2);
        const canvas = document.querySelector('#svg-to-png-app canvas');
        const bmpDataURL = api.canvasToBMP(canvas);
        assertStartsWith("BMP: Data URL format", bmpDataURL, "data:image/bmp;base64,");
        const base64Part = bmpDataURL.split(',')[1];
        assertTrue("BMP: Base64 string exists and non-empty", base64Part && base64Part.length > 50);
        const bmpBytes = base64ToBytes(base64Part);
        assertTrue("BMP: File header signature 'BM'", bmpBytes[0] === 0x42 && bmpBytes[1] === 0x4D);
        const fileSize = bmpBytes[2] | (bmpBytes[3] << 8) | (bmpBytes[4] << 16) | (bmpBytes[5] << 24);
        assertTrue("BMP: File size plausible", Math.abs(fileSize - (base64Part.length * 0.75)) < 100);
        const dibSize = bmpBytes[14] | (bmpBytes[15] << 8) | (bmpBytes[16] << 16) | (bmpBytes[17] << 24);
        assertTrue("BMP: DIB header size 40 bytes", dibSize === 40);
        const width = bmpBytes[18] | (bmpBytes[19] << 8) | (bmpBytes[20] << 16) | (bmpBytes[21] << 24);
        const heightAbs = Math.abs(bmpBytes[22] | (bmpBytes[23] << 8) | (bmpBytes[24] << 16) | (bmpBytes[25] << 24));
        assertTrue("BMP: Width matches canvas", width === canvas.width);
        assertTrue("BMP: Height matches canvas", heightAbs === canvas.height);
        const bpp = bmpBytes[28] | (bmpBytes[29] << 8);
        assertTrue("BMP: Bits per pixel is 24", bpp === 24);
    } catch (err) {
        console.error("BMP test error:", err);
        assertTrue("BMP: Test execution should not throw", false, err.message);
    }

    // ==================== EDGE CASE TESTS ====================
    console.log("%c📝 Running Edge Case Tests...", "color: #FF9800; font-weight: bold;");
    try {
        assertTrue("Empty SVG: error or cleared", await testEdgeCase("   ", true));
        assertTrue("Invalid SVG: error or cleared", await testEdgeCase("<svg><invalid></svg>", true));
        const missingXmlns = `<svg viewBox="0 0 20 20" width="20" height="20"><circle cx="10" cy="10" r="8" fill="red"/></svg>`;
        assertTrue("Missing xmlns: auto-fixed and loads", await testEdgeCase(missingXmlns, false));
    } catch (err) {
        console.error("Edge case error:", err);
        assertTrue("Edge cases: Should handle gracefully", false, err.message);
    }

    // ==================== FAVICON FALLBACK TESTS ====================
    console.log("%c📝 Running Favicon Fallback Tests...", "color: #FF9800; font-weight: bold;");

    try {
        const smallSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
            <circle cx="50" cy="50" r="50" fill="#FF6600"/>
        </svg>`;
        await loadTestSVG(smallSVG);
        const faviconHref = getFaviconHref();
        const isCustom = faviconHref.startsWith('data:image/svg+xml,') && faviconHref.includes('circle');
        assertTrue("Small SVG: Custom favicon is set (SVG data URL)", isCustom);
    } catch (err) {
        console.error("Favicon small SVG test error:", err);
        assertTrue("Small SVG favicon test should not throw", false, err.message);
    }

    try {
        const largeSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
            <rect width="300" height="300" fill="blue"/>
        </svg>`;
        await loadTestSVG(largeSVG);
        const faviconHref = getFaviconHref();
        const isDefault = isDefaultFavicon(faviconHref);
        assertTrue("Large dimensions (>200): Favicon falls back to default IMG icon", isDefault);
    } catch (err) {
        console.error("Favicon large dimensions test error:", err);
        assertTrue("Large dimensions favicon test should not throw", false, err.message);
    }

    try {
        let longContent = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">';
        for (let i = 0; i < 3000; i++) {
            longContent += `<circle cx="${i%100}" cy="50" r="1" fill="red"/>`;
        }
        longContent += '</svg>';
        if (longContent.length < 100000) {
            while (longContent.length < 100000) longContent += '<!-- padding -->';
        }
        await loadTestSVG(longContent);
        const faviconHref = getFaviconHref();
        const isDefault = isDefaultFavicon(faviconHref);
        assertTrue("Large SVG string (>100k chars): Favicon falls back to default", isDefault);
    } catch (err) {
        console.error("Favicon large string test error:", err);
        assertTrue("Large string favicon test should not throw", false, err.message);
    }

    // ==================== BMP PIXEL VALIDATION ====================
    console.log("%c📝 Running BMP Pixel Validation...", "color: #FF9800; font-weight: bold;");
    try {
        const solidColorSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
            <rect width="10" height="10" fill="#FF3366"/>
        </svg>`;
        await loadTestSVG(solidColorSVG);
        const canvas = document.querySelector('#svg-to-png-app canvas');
        const bmpURL = api.canvasToBMP(canvas);
        const bytes = base64ToBytes(bmpURL.split(',')[1]);
        const topLeftPixelOffset = 54;
        const r = bytes[topLeftPixelOffset + 2];
        const g = bytes[topLeftPixelOffset + 1];
        const b = bytes[topLeftPixelOffset];
        assertTrue("BMP solid color: Red component #FF3366", r === 255);
        assertTrue("BMP solid color: Green component #FF3366", g === 51);
        assertTrue("BMP solid color: Blue component #FF3366", b === 102);
    } catch (err) {
        console.error("BMP pixel validation error:", err);
        assertTrue("BMP pixel validation should pass", false, err.message);
    }

    // ==================== BMP ALPHA COMPOSITING ====================
    console.log("%c📝 Running BMP Alpha Compositing...", "color: #FF9800; font-weight: bold");
    try {
        const alphaSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="5" height="5">
            <rect width="5" height="5" fill="rgba(0,0,255,0.5)"/>
        </svg>`;
        await loadTestSVG(alphaSVG);
        const canvas = document.querySelector('#svg-to-png-app canvas');
        const bmpURL = api.canvasToBMP(canvas);
        const bytes = base64ToBytes(bmpURL.split(',')[1]);
        const r = bytes[54 + 2];
        const g = bytes[54 + 1];
        const b = bytes[54];
        assertTrue("BMP alpha: Red ~128", Math.abs(r - 128) <= 3);
        assertTrue("BMP alpha: Green ~128", Math.abs(g - 128) <= 3);
        assertTrue("BMP alpha: Blue ~255", Math.abs(b - 255) <= 3);
    } catch (err) {
        console.error("BMP alpha test error:", err);
        assertTrue("BMP alpha test should not throw", false, err.message);
    }

    // ==================== PNG ALPHA TEST ====================
    console.log("%c📝 Running PNG Alpha Channel Test...", "color: #FF9800; font-weight: bold;");
    try {
        const alphaSVG = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20">
            <rect width="20" height="20" fill="rgba(255,0,0,0.3)"/>
        </svg>`;
        await loadTestSVG(alphaSVG);
        const canvas = document.querySelector('#svg-to-png-app canvas');
        const pngURL = canvas.toDataURL('image/png');
        assertTrue("PNG with alpha: Data URL generated", pngURL && pngURL.startsWith('data:image/png;base64,'));
    } catch (err) {
        assertTrue("PNG alpha test should not throw", false, err.message);
    }

    // ==================== BMP ROW PADDING TEST ====================
    console.log("%c📝 Running BMP Row Padding Test...", "color: #FF9800; font-weight: bold;");
    try {
        const oddSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"><rect width="1" height="1" fill="#000000"/></svg>`;
        await loadTestSVG(oddSvg, "odd.svg");
        const canvas = document.querySelector('#svg-to-png-app canvas');
        const bmpURL = api.canvasToBMP(canvas);
        const bytes = base64ToBytes(bmpURL.split(',')[1]);
        // 1 pixel = 3 bytes (BGR). Next multiple of 4 is 4 bytes. 1 byte padding.
        // 54 bytes (header) + 4 bytes (pixel row) = 58 bytes.
        assertTrue("BMP Padding: 1x1 image generates exact 58 byte file", bytes.byteLength === 58);
    } catch (err) {
        assertTrue("BMP Padding test should not throw", false, err.message);
    }

    // ==================== DATA URL SYNC TESTS ====================
    console.log("%c📝 Running Data URL Sync Tests...", "color: #FF9800; font-weight: bold;");
    try {
        const svgInput = document.querySelector('#svg-input');
        const liveDataUrlInput = document.querySelector('#live-data-url');
        const chkWrapLink = document.querySelector('#chk-wrap-link');

        svgInput.value = '<svg><circle/></svg>';
        api.syncDataUrl();
        assertTrue("Data URL Sync: Encodes properly", liveDataUrlInput.value.includes('%3Csvg%3E%3Ccircle%2F%3E%3C%2Fsvg%3E'));

        chkWrapLink.checked = true;
        api.syncDataUrl();
        assertStartsWith("Data URL Sync: Wraps in <link> tag", liveDataUrlInput.value, '<link rel="icon"');
        chkWrapLink.checked = false;

        liveDataUrlInput.value = 'data:image/svg+xml,%3Csvg%3E%3Crect%2F%3E%3C%2Fsvg%3E';
        api.syncFromDataUrl();
        assertTrue("Sync From Data URL: Decodes safely", svgInput.value.includes('<rect/>'));
    } catch (err) {
        assertTrue("Data URL Sync test should not throw", false, err.message);
    }

    // ==================== DIMENSION PARSING TESTS ====================
    console.log("%c📝 Running Dimension Parsing Failsafe Tests...", "color: #FF9800; font-weight: bold;");
    try {
        await loadTestSVG(`<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><rect/></svg>`, "perc.svg");
        const canvas = document.querySelector('#svg-to-png-app canvas');
        assertTrue("Dimensions: 100% width falls back to default 300", canvas.width === 300);

        await loadTestSVG(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150" width="100%" height="100%"><rect/></svg>`, "viewbox.svg");
        assertTrue("Dimensions: Percentage widths yield to viewBox", canvas.width === 150);
    } catch (err) {
        assertTrue("Dimension parsing test should not throw", false, err.message);
    }

    // ==================== ADVANCED XML FORMAT TESTS ====================
    console.log("%c📝 Running Advanced XML Formatting Tests...", "color: #FF9800; font-weight: bold;");
    assert("formatXML: Multi-attribute spacing cleaned", api.formatXML('<rect id="a"  class="b" />'), '<rect id="a" class="b"/>');
    assert("formatXML: Style tag kept open", api.formatXML('<svg><style>.a{fill:red;}</style></svg>'), '<svg>\n  <style>.a{fill:red;}</style>\n</svg>');

    // ==================== SUMMARY, RESET, AND ENLARGED FINAL TOAST ====================
    const color = failed > 0 ? '#f44336' : '#4CAF50';
    console.log(`%c🏁 Test Run Complete: ${passed} Passed, ${failed} Failed`, `font-weight: bold; font-size: 14px; color: ${color}`);
    
    resetAppToInitialState();
    
    // Watchdog to remove any xmlns toast
    let watchdogInterval = setInterval(() => {
        const toast = document.querySelector('#status-toast');
        if (toast && toast.textContent.includes('Added missing xmlns')) {
            toast.classList.remove('show');
            console.log("%c🗑️ Removed xmlns toast.", "color: #888;");
        }
    }, 100);
    setTimeout(() => clearInterval(watchdogInterval), 3000);
    
    // Show enlarged, centered final toast
    setTimeout(() => {
        const toast = document.querySelector('#status-toast');
        if (toast) {
            if (window._toastTimer) clearTimeout(window._toastTimer);
            
            // Store original styles to restore later
            const originalStyles = {
                position: toast.style.position,
                top: toast.style.top,
                left: toast.style.left,
                transform: toast.style.transform,
                bottom: toast.style.bottom,
                right: toast.style.right,
                padding: toast.style.padding,
                fontSize: toast.style.fontSize,
                borderRadius: toast.style.borderRadius,
                boxShadow: toast.style.boxShadow
            };
            
            // Center and enlarge (2x original size)
            toast.style.position = 'fixed';
            toast.style.top = '50%';
            toast.style.left = '50%';
            toast.style.transform = 'translate(-50%, -50%)';
            toast.style.bottom = 'auto';
            toast.style.right = 'auto';
            
            // Double the original toast dimensions
            toast.style.padding = '24px 48px';     // original: 12px 24px
            toast.style.fontSize = '1.8rem';       // original: 0.9rem
            toast.style.borderRadius = '16px';     // original: 8px
            toast.style.boxShadow = '0 8px 24px rgba(0,0,0,0.25)'; // deeper shadow
            
            toast.textContent = `🧪 Tests: ${passed} passed, ${failed} failed. App reset.`;
            toast.classList.add('show');
            
            window._toastTimer = setTimeout(() => {
                toast.classList.remove('show');
                // Restore original styles
                toast.style.position = originalStyles.position || '';
                toast.style.top = originalStyles.top || '';
                toast.style.left = originalStyles.left || '';
                toast.style.transform = originalStyles.transform || '';
                toast.style.bottom = originalStyles.bottom || '';
                toast.style.right = originalStyles.right || '';
                toast.style.padding = originalStyles.padding || '';
                toast.style.fontSize = originalStyles.fontSize || '';
                toast.style.borderRadius = originalStyles.borderRadius || '';
                toast.style.boxShadow = originalStyles.boxShadow || '';
            }, 7000);
        }
    }, 800);
};

console.log("%c💡 test_suite_v2_24_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");