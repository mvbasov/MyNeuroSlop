// base64_converter_v1_1_0_tests.js - Micro Unit Test System

window.__runTests = async function() {
    console.log("%c🚀 Starting Automated Unit Tests...", "color: #4A90E2; font-weight: bold; font-size: 14px;");
    let passed = 0, failed = 0;
    
    // 1. Fetch the API exposed conditionally by the main application
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
            console.error(`❌ FAIL: ${name}\n   Condition not met. ${message ? "\n   " + message : ""}`);
            failed++;
            return false;
        }
    }

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // ==================== TEST SUITE ====================
    console.log("%c📝 Running Tests...", "color: #FF9800; font-weight: bold;");
    
    try {
        // --- Test 1: Internal Encoding API ---
        const b64Out = api.encode("Test");
        assert("API Encode: 'Test' -> 'VGVzdA=='", b64Out, "VGVzdA==");

        // --- Test 2: Internal Decoding API (with Unicode) ---
        const decoded = api.decode("4pyTIMOgIGxhIG1vZGU=");
        assert("API Decode: Unicode strings handled safely", decoded, "✓ à la mode");

        // --- Test 3: DOM Interactions & Event Sync ---
        const plainInput = document.querySelector('#plain-text');
        const base64Input = document.querySelector('#base64-text');

        // Simulate user typing into the plain text box
        plainInput.value = "Hello World";
        plainInput.dispatchEvent(new Event('input')); 
        
        await sleep(100); // Allow DOM event loop to process
        
        assert("DOM Sync: Typing plain text updates Base64 textarea", base64Input.value, "SGVsbG8gV29ybGQ=");

        // Simulate user typing invalid base64
        base64Input.value = "%%%INVALID%%%";
        base64Input.dispatchEvent(new Event('input'));

        await sleep(100);

        assert("DOM Sync: Invalid base64 yields safe fallback text", plainInput.value, "Invalid Base64");

    } catch (err) {
        assertTrue("Test suite execution should not throw exceptions", false, err.message);
    }

    // ==================== SUMMARY & UI ENFORCER ====================
    const color = failed > 0 ? '#f44336' : '#4CAF50';
    
    setTimeout(() => {
        let toast = document.querySelector('#status-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'status-toast';
            document.body.appendChild(toast);
        }
        
        if (window._toastTimer) clearTimeout(window._toastTimer);
        if (window._toastEnforcer) clearInterval(window._toastEnforcer);
        
        const enforceToast = () => {
            toast.style.position = 'fixed';
            toast.style.top = '50%';
            toast.style.left = '50%';
            toast.style.transform = 'translate(-50%, -50%)';
            toast.style.bottom = 'auto';
            toast.style.right = 'auto';
            toast.style.padding = '24px 48px';
            toast.style.fontSize = '1.8rem';
            toast.style.borderRadius = '16px';
            toast.style.boxShadow = '0 8px 24px rgba(0,0,0,0.25)';
            toast.style.opacity = '1';
            toast.style.backgroundColor = color;
            toast.style.color = '#fff';
            toast.style.zIndex = '99999';
            toast.style.display = 'block';
            
            const expectedText = `🧪 Tests: ${passed} passed, ${failed} failed.`;
            if (toast.textContent !== expectedText) {
                toast.textContent = expectedText;
                toast.classList.add('show');
            }
        };

        enforceToast();
        window._toastEnforcer = setInterval(enforceToast, 100);
        
        window._toastTimer = setTimeout(() => {
            clearInterval(window._toastEnforcer);
            toast.classList.remove('show');
            toast.style.display = 'none'; 
        }, 7000);
        
    }, 800);
};

console.log("%c💡 base64_converter_v1_1_0_tests.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");