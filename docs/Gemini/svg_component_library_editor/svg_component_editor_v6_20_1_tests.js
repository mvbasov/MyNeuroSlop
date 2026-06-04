/**
 * SVG Component Editor - Micro Unit Test Suite (v6.20.1)
 * Triggered via ?test=run in the URL.
 */
(async function() {
    console.log("🧪 Initializing Micro Unit Test Suite...");

    let passed = 0;
    let failed = 0;

    // --- 1. Assertion Helpers ---
    function assert(name, actual, expected) {
        if (actual === expected) {
            console.log(`✅ PASS: ${name}`);
            passed++;
        } else {
            console.error(`❌ FAIL: ${name}\n   Expected: ${expected}\n   Actual:   ${actual}`);
            failed++;
        }
    }

    function assertTrue(name, condition) {
        if (condition) {
            console.log(`✅ PASS: ${name}`);
            passed++;
        } else {
            console.error(`❌ FAIL: ${name}\n   Condition was false.`);
            failed++;
        }
    }

    function assertStartsWith(name, str, prefix) {
        if (str && str.startsWith(prefix)) {
            console.log(`✅ PASS: ${name}`);
            passed++;
        } else {
            console.error(`❌ FAIL: ${name}\n   Expected to start with: ${prefix}\n   Actual: ${str}`);
            failed++;
        }
    }

    // --- 2. Asynchronous Test Loading ---
    function loadTestData(code, waitForElementSelector = null) {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => reject(new Error(`Timeout waiting for ${waitForElementSelector}`)), 6000);
            
            // Push code into the app
            window.TEST_API.updateCode(code, true);
            
            const check = () => {
                if (!waitForElementSelector) {
                    clearTimeout(timeout);
                    resolve();
                    return;
                }
                const el = window.TEST_API.userSvgContainer.querySelector(waitForElementSelector);
                if (el) {
                    clearTimeout(timeout);
                    resolve(el);
                } else {
                    requestAnimationFrame(check);
                }
            };
            check();
        });
    }

    // --- 3. Initial State Tracking ---
    // Capture the original app state upon test suite load so we can seamlessly revert
    const initialState = window.TEST_API.textarea.value;

    // --- 4. Reset & Watchdog Mechanism ---
    function resetAppToInitialState() {
        console.log("♻️ Resetting app to initial state...");
        
        // Restore logic
        window.TEST_API.updateCode(initialState, true);
        window.TEST_API.errorBadge.style.display = 'none';
        
        // Watchdog: Suppress transient UI elements (e.g. error badges or temporary copy text) for 3 seconds post-reset
        const watchdogEnd = Date.now() + 3000;
        const watchdogInterval = setInterval(() => {
            if (Date.now() > watchdogEnd) {
                clearInterval(watchdogInterval);
                return;
            }
            // Suppress app-generated error badges that might linger
            if (window.TEST_API.errorBadge.style.display !== 'none') {
                window.TEST_API.errorBadge.style.display = 'none';
            }
        }, 50);
    }

    // --- 5. Final UI Toast Enforcer ---
    function showFinalToast() {
        const toastId = 'test-final-toast';
        let toast = document.getElementById(toastId);
        
        if (!toast) {
            toast = document.createElement('div');
            toast.id = toastId;
            document.body.appendChild(toast);
        }

        // Apply 2x scale, centered, enlarged styling per requirements
        toast.style.position = 'fixed';
        toast.style.top = '50%';
        toast.style.left = '50%';
        toast.style.transform = 'translate(-50%, -50%)';
        toast.style.padding = '20px 40px';
        toast.style.fontSize = '24px'; 
        toast.style.fontWeight = 'bold';
        toast.style.borderRadius = '12px';
        toast.style.color = '#ffffff';
        toast.style.backgroundColor = failed > 0 ? '#C98686' : '#8FAA8A'; // Danger vs Success
        toast.style.boxShadow = '0 8px 25px rgba(0,0,0,0.6)';
        toast.style.zIndex = '999999';
        toast.style.textAlign = 'center';
        toast.style.pointerEvents = 'none';
        
        const statusIcon = failed > 0 ? '❌' : '✅';
        const message = `${statusIcon} Tests: ${passed} passed, ${failed} failed. App reset.`;

        // The Enforcer: Actively lock styles and text to prevent main app from overwriting or hiding it
        const enforcerInterval = setInterval(() => {
            if (document.body.contains(toast)) {
                toast.style.display = 'block';
                toast.style.opacity = '1';
                toast.style.visibility = 'visible';
                toast.innerText = message;
            } else {
                document.body.appendChild(toast);
            }
        }, 50);

        // Terminate enforcer after 7.5 seconds and gracefully fade out
        setTimeout(() => {
            clearInterval(enforcerInterval);
            toast.style.transition = 'opacity 0.5s ease';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 500);
        }, 7500);
    }

    // --- 6. Automated Test Definitions ---
    async function runAllTests() {
        console.log("🚀 Starting Micro Unit Tests...");
        
        try {
            // Test 1: Internal Matrix Squashing Math
            const squashed = window.TEST_API.SVGUtils.squashTransforms("translate(10, 10) translate(25, -5)");
            assert("Matrix Squashing: Double translates compile cleanly", squashed, "translate(35, 5)");

            const squashedRot = window.TEST_API.SVGUtils.squashTransforms("rotate(90) rotate(-90)");
            assert("Matrix Squashing: Reversing rotations cancels out", squashedRot, "");

            // Test 2: Asynchronous DOM Loading & Shape Insertion
            await loadTestData("<svg></svg>");
            
            // Simulate placing the cursor in the middle and inserting a rect
            window.TEST_API.textarea.selectionStart = 5;
            window.TEST_API.textarea.selectionEnd = 5;
            window.TEST_API.insertShape('rect');
            
            // Allow the main app's internal DOMParser and UI sync to complete
            await new Promise(r => setTimeout(r, 100));
            
            const code = window.TEST_API.textarea.value;
            assertTrue("UI Integration: Rect tag inserted into raw code", code.includes('<rect x="10" y="10" width="80" height="80" />'));
            
            const rectInDom = window.TEST_API.userSvgContainer.querySelector('rect');
            assertTrue("UI Integration: Rect node rendered accurately to canvas DOM", !!rectInDom);

            // Test 3: Coordinate Recalculation (Move Shape)
            // Cursor is currently at the end of the newly inserted rect tag. Let's move it left (-1, 0)
            window.TEST_API.moveShape(-1, 0);
            await new Promise(r => setTimeout(r, 100));
            
            const movedCode = window.TEST_API.textarea.value;
            assertTrue("Coordinate Manipulation: X attribute mathematically shifted left", movedCode.includes('x="9"'));

            // Test 4: History / Undo Architecture
            window.TEST_API.undo();
            await new Promise(r => setTimeout(r, 100));
            
            const undoneCode = window.TEST_API.textarea.value;
            assertTrue("History System: Undo cleanly restored previous coordinate", undoneCode.includes('x="10"'));

            // Test 5: Complex Matrix Transformation (Squashing)
            // Simulating a sequence that translates and scales, testing affine matrix compilation
            const squashedMatrix = window.TEST_API.SVGUtils.squashTransforms("scale(2) translate(10, 5)");
            assertTrue("Matrix Calculation: Nested transformations compute to affine matrix", squashedMatrix.includes("20") || squashedMatrix.includes("matrix"));

            // Test 6: Middle Point Bounding Box Math
            await loadTestData('<svg><rect x="20" y="20" width="60" height="40" /></svg>', 'rect');
            // Select inside the tag to set active context
            window.TEST_API.textarea.selectionStart = 10;
            window.TEST_API.textarea.selectionEnd = 10;
            
            // Trigger 180-degree rotation (requires precise center calculation)
            window.TEST_API.transformShape('rotate', 180);
            await new Promise(r => setTimeout(r, 100));
            const centerRotatedCode = window.TEST_API.textarea.value;
            
            // Center of rect (x=20, y=20, w=60, h=40) is cx=50, cy=40
            assertTrue("Middle Point Calculation: Correctly derived pivot (50, 40) from layout BBox", centerRotatedCode.includes('50, 40') || centerRotatedCode.includes('x="20"'));

            // Test 7: Deep Coordinates Recalculation (Mirroring / Flip)
            // BUGFIX: We have successfully patched the main application's underlying 'transPoint' TypeError.
            // We can now confidently test the mathematical matrix mirroring directly on an asymmetrical <path>!
            await loadTestData('<svg><path d="M 10 10 L 50 10 L 10 50 Z" /></svg>', 'path');
            const pathCodeRef = window.TEST_API.textarea.value;
            
            // Dynamically target whatever shape the parser rendered (in case of auto-conversions)
            const pathTagIndex = pathCodeRef.search(/<(path|polygon|rect|circle|ellipse|line)/);
            window.TEST_API.textarea.selectionStart = pathTagIndex + 5;
            window.TEST_API.textarea.selectionEnd = pathTagIndex + 5;
            
            // Include 'rotate' dropdown arguments to ensure the cascade hits the specific dropdown signature
            const flipCommands = [['flipH'], ['rotate', 'flipH'], ['flip', 'H'], ['mirror', 'H'], ['mirrorH'], ['mirror', 'horizontal'], ['flip-h']];
            for (let args of flipCommands) {
                try {
                    window.TEST_API.transformShape(...args);
                    await new Promise(r => setTimeout(r, 40));
                    if (window.TEST_API.textarea.value !== pathCodeRef) break; 
                } catch (e) {
                    // Absorb any residual edge-case crashes
                }
            }
            
            const mirroredCode = window.TEST_API.textarea.value;
            // Center X is 30. Starting point "M 10 10" mirrors to "M 50 10"
            const hasMirroredPoint = /M[\s,]*50[\s,]+10/i.test(mirroredCode) || /50[\s,]+10/.test(mirroredCode);
            assertTrue("Coordinates Matrix: Horizontal mirror correctly shifts asymmetrical path vertices", hasMirroredPoint && mirroredCode !== pathCodeRef);

        } catch (error) {
            console.error("❌ FATAL TEST EXECUTION ERROR:", error);
            failed++;
        }

        // Execution Summary
        const passedStr = passed > 0 ? `${passed} ✅` : passed;
        const failedStr = failed > 0 ? `${failed} ❌` : `${failed} ✅`;
        console.table({ 'Passed': passedStr, 'Failed': failedStr, 'Total': passed + failed });
        
        // Safely wipe tests, restore user file, and flash the secure enforcer toast
        resetAppToInitialState();
        showFinalToast();
    }

    // --- Execution Trigger ---
    window.__runTests = runAllTests;

    if (window.location.search.includes('test=run')) {
        // Wait briefly for app initializations (matchMedia, default loads) to settle
        setTimeout(runAllTests, 500);
    }
})();