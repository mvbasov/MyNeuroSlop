// ChromaForge_v1_2_1_tests.js - Fixed reset preview test
(function() {
    let totalTests = 0;
    let passedTests = 0;
    let failedTests = 0;
    const results = [];
    let testRan = false;

    function logResult(message) {
        console.log(message);
        results.push(message);
    }

    function assert(condition, message) {
        totalTests++;
        if(condition) {
            passedTests++;
            logResult(`✅ PASS: ${message}`);
            return true;
        } else {
            failedTests++;
            logResult(`❌ FAIL: ${message}`);
            return false;
        }
    }
    function assertTrue(condition, message) { return assert(condition, message); }
    function assertEquals(actual, expected, message) {
        const condition = actual === expected;
        totalTests++;
        if(condition) {
            passedTests++;
            logResult(`✅ PASS: ${message} (${actual} === ${expected})`);
        } else {
            failedTests++;
            logResult(`❌ FAIL: ${message} (expected ${expected}, got ${actual})`);
        }
        return condition;
    }

    const api = window.__TEST_API__;
    if(!api) {
        console.error("Test API missing. Load page with ?test= parameter.");
        if(window.__showTestToast) window.__showTestToast("⚠️ Test API missing. Reload with ?test=run", "error");
        return;
    }

    async function waitForStyle(element, property, expectedValue, timeout = 500) {
        const start = Date.now();
        while(Date.now() - start < timeout) {
            const actual = window.getComputedStyle(element)[property];
            if(actual === expectedValue) return true;
            await new Promise(r => setTimeout(r, 30));
        }
        return false;
    }

    async function runAllTests() {
        if(testRan) return;
        testRan = true;
        totalTests = 0; passedTests = 0; failedTests = 0;
        results.length = 0;
        console.log("🧪 Starting ChromaForge test suite...\n");
        
        // ----- 1. Internal Logic Tests -----
        const testTheme = { primary: "#ff0000", secondary: "#00ff00", bgColor: "#ffffff", surfaceColor: "#eeeeee", textColor: "#000000", borderColor: "#cccccc" };
        api.applyPreviewTheme(testTheme);
        const current = api.getCurrentPreviewTheme();
        assertEquals(current.primary, "#ff0000", "applyPreviewTheme updates --primary to red");
        assertEquals(current.secondary, "#00ff00", "applyPreviewTheme updates --secondary to green");
        
        api.applyPreviewTheme(api.DEFAULT_PREVIEW_THEME);
        const defaultTheme = api.getCurrentPreviewTheme();
        assertEquals(defaultTheme.primary, api.DEFAULT_PREVIEW_THEME.primary, "Reset to default restores primary color");
        
        api.applyPreviewTheme(api.PREVIEW_PRESETS.dark);
        const darkPreview = api.getCurrentPreviewTheme();
        assertEquals(darkPreview.primary, "#8b5cf6", "Dark preset primary is purple");
        assertEquals(darkPreview.bgColor, "#111827", "Dark preset background is dark");
        
        // Main theme switching
        api.applyMainTheme("light");
        assertEquals(api.getMainThemeMode(), "light", "applyMainTheme switches to light mode");
        assertTrue(!api.getMainContainerClass().includes("dark"), "Light mode removes dark class");
        api.applyMainTheme("dark");
        assertEquals(api.getMainThemeMode(), "dark", "applyMainTheme switches to dark mode");
        assertTrue(api.getMainContainerClass() === "dark", "Dark mode adds main-dark class");
        api.applyMainTheme("auto");
        
        // ----- 2. DOM / UI State Tests with retry -----
        api.applyPreviewTheme(api.PREVIEW_PRESETS.ocean);
        const oceanPrimaryRgb = "rgb(14, 165, 233)"; // #0ea5e9
        const oceanBorderRgb = "rgb(186, 230, 253)"; // #bae6fd
        
        const primaryBtn = api.getPrimaryButton();
        if(primaryBtn) {
            const btnOk = await waitForStyle(primaryBtn, "backgroundColor", oceanPrimaryRgb);
            const actualBg = window.getComputedStyle(primaryBtn).backgroundColor;
            assertTrue(btnOk, `Primary button becomes ocean primary (${actualBg})`);
        } else {
            assert(false, "Primary button element not found");
        }
        
        const progressFill = api.getProgressFill();
        if(progressFill) {
            const fillBg = window.getComputedStyle(progressFill).backgroundColor;
            assertTrue(fillBg === oceanPrimaryRgb, `Progress fill uses ocean primary (${fillBg})`);
        } else {
            assert(false, "Progress fill missing");
        }
        
        const statEl = api.getPrimaryStatElement();
        if(statEl) {
            const statColor = window.getComputedStyle(statEl).color;
            assertTrue(statColor === oceanPrimaryRgb, `Primary stat dot reflects ocean primary (${statColor})`);
        }
        
        const card = document.querySelector('#name-app .card');
        if(card) {
            const borderOk = await waitForStyle(card, "borderTopColor", oceanBorderRgb);
            const actualBorder = window.getComputedStyle(card).borderTopColor;
            assertTrue(borderOk, `Card border adapts to ocean theme (${actualBorder})`);
        }
        
        api.applyMainTheme("dark");
        const studio = document.querySelector('#name-app .theme-studio');
        await waitForStyle(studio, "backgroundColor", "", 100);
        const studioBg = window.getComputedStyle(studio).backgroundColor;
        assertTrue(studioBg !== "rgb(241, 245, 249)" && studioBg.length > 0, "Main dark theme changes studio background");
        api.applyMainTheme("auto");
        
        // ----- 3. Edge Cases & Integrity -----
        // Test that applying a valid hex works and restores cleanly
        const backupTheme = api.getCurrentPreviewTheme();
        try {
            api.applyPreviewTheme({ ...api.DEFAULT_PREVIEW_THEME, primary: "#123456" });
            const newTheme = api.getCurrentPreviewTheme();
            assertEquals(newTheme.primary, "#123456", "applyPreviewTheme accepts any valid hex without crashing");
            api.applyPreviewTheme(backupTheme);
            assert(true, "Theme restoration after valid change works");
        } catch(e) {
            assert(false, "applyPreviewTheme threw unexpectedly: " + e.message);
        }
        
        // FIX: Reset preview should restore DEFAULT theme, not the previous one
        const defaultThemeExpected = api.DEFAULT_PREVIEW_THEME;
        api.applyPreviewTheme(api.PREVIEW_PRESETS.sunset);
        api.applyPreviewTheme(api.DEFAULT_PREVIEW_THEME);
        const afterReset = api.getCurrentPreviewTheme();
        assertEquals(afterReset.primary, defaultThemeExpected.primary, "Reset preview restores default theme (primary)");
        assertEquals(afterReset.secondary, defaultThemeExpected.secondary, "Reset preview restores default theme (secondary)");
        
        const finalMessage = `\n🧪 FINAL SUMMARY: ${passedTests}/${totalTests} passed, ${failedTests} failed.`;
        console.log(finalMessage);
        if(window.__showTestToast) {
            const color = failedTests === 0 ? "✅ ALL TESTS PASSED" : "❌ SOME TESTS FAILED";
            window.__showTestToast(`${color}\n${passedTests}/${totalTests} passed`, failedTests > 0 ? "error" : "info");
        } else {
            alert(finalMessage);
        }
    }
    
    window.__runTests = runAllTests;
    if(new URLSearchParams(window.location.search).get('test') === 'run') {
        if(document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => runAllTests());
        } else {
            runAllTests();
        }
    }
})();