// template_tests.js - Micro Unit Test System Template

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

    // Standard helper for awaiting asynchronous UI/DOM updates
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // ==================== TEST SUITE ====================
    console.log("%c📝 Running Tests...", "color: #FF9800; font-weight: bold;");
    
    try {
        // --- Example 1: Testing an internal function directly via the API ---
        // const output = api.someInternalMathFunction(2, 2);
        // assert("Internal Math Engine: 2+2=4", output, 4);

        // --- Example 2: Testing DOM interactions asynchronously ---
        // const inputField = document.querySelector('#app-input');
        // inputField.value = "Sample Data";
        // inputField.dispatchEvent(new Event('input')); // Trigger internal event listeners
        
        // await sleep(150); // Give the app time to process and update the DOM
        
        // const outputLabel = document.querySelector('#app-output');
        // assertTrue("DOM updates properly after input", outputLabel.textContent.includes("Sample Data"));

    } catch (err) {
        assertTrue("Test suite execution should not throw exceptions", false, err.message);
    }

    // ==================== SUMMARY & UI ENFORCER ====================
    const color = failed > 0 ? '#f44336' : '#4CAF50';
    
    // Show enlarged, centered final toast (with forced persistence)
    setTimeout(() => {
        // Try to find the app's native toast, or create a fallback container
        let toast = document.querySelector('#status-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'status-toast';
            document.body.appendChild(toast);
        }
        
        if (window._toastTimer) clearTimeout(window._toastTimer);
        if (window._toastEnforcer) clearInterval(window._toastEnforcer);
        
        // The Enforcer function strictly dictates the toast's visual state
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
        // Forcefully maintain the toast against internal app timeouts (every 100ms)
        window._toastEnforcer = setInterval(enforceToast, 100);
        
        // Clean up and hide after exactly 7 seconds
        window._toastTimer = setTimeout(() => {
            clearInterval(window._toastEnforcer);
            toast.classList.remove('show');
            toast.style.display = 'none'; 
        }, 7000);
        
    }, 800);
};

console.log("%c💡 template_tests.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.", "color: #4A90E2;");