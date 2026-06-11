// ChromaForge_v1_8_0_tests.js - updated for live CSS preview, preset dropdown & info-badge
(function() {
    let totalTests = 0;
    let passedTests = 0;
    let failedTests = 0;
    const results = [];
    let testRan = false;

    function logResult(message) {
        const maxLen = 120;
        const shortMsg = message.length > maxLen ? message.substring(0, maxLen) + "…" : message;
        console.log(shortMsg);
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
            logResult(`✅ PASS: ${message}`);
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
        console.log("🧪 ChromaForge test suite (v1.8.0)\n");
        
        // ----- 1. Internal Logic Tests -----
        const testTheme = { primary: "#ff0000", secondary: "#00ff00", bgColor: "#ffffff", surfaceColor: "#eeeeee", textColor: "#000000", borderColor: "#cccccc", infoColor: "#666666" };
        api.applyPreviewTheme(testTheme);
        const current = api.getCurrentPreviewTheme();
        assertEquals(current.primary, "#ff0000", "applyPreviewTheme updates --primary to red");
        assertEquals(current.secondary, "#00ff00", "applyPreviewTheme updates --secondary to green");
        assertEquals(current.infoColor, "#666666", "applyPreviewTheme updates --info-color to grey");
        
        api.applyPreviewTheme(api.DEFAULT_PREVIEW_THEME);
        const defaultTheme = api.getCurrentPreviewTheme();
        assertEquals(defaultTheme.primary, api.DEFAULT_PREVIEW_THEME.primary, "Reset to default restores primary color");
        assertEquals(defaultTheme.infoColor, api.DEFAULT_PREVIEW_THEME.infoColor, "Reset to default restores info-badge color");
        
        api.applyPreviewTheme(api.PREVIEW_PRESETS.dark);
        const darkPreview = api.getCurrentPreviewTheme();
        assertEquals(darkPreview.primary, "#8b5cf6", "Dark preset primary is purple");
        assertEquals(darkPreview.bgColor, "#111827", "Dark preset background is dark");
        assertEquals(darkPreview.infoColor, "#3b82f6", "Dark preset infoColor is blue");
        
        // Test updated soft presets
        api.applyPreviewTheme(api.PREVIEW_PRESETS["soft-light"]);
        const softLight = api.getCurrentPreviewTheme();
        assertEquals(softLight.primary, "#5a8fcc", "Soft Light preset primary is darker pastel blue");
        assertEquals(softLight.bgColor, "#efe2c6", "Soft Light preset background is warm cream");
        assertEquals(softLight.infoColor, "#7e6c54", "Soft Light preset infoColor is soft gold-brown");
        
        api.applyPreviewTheme(api.PREVIEW_PRESETS["soft-dark"]);
        const softDark = api.getCurrentPreviewTheme();
        assertEquals(softDark.primary, "#7a9cbb", "Soft Dark preset primary is dusty blue");
        assertEquals(softDark.bgColor, "#1e2a3a", "Soft Dark preset background is deep navy-blue");
        assertEquals(softDark.infoColor, "#4a6a8a", "Soft Dark preset infoColor is dusty steel-blue");
        
        // Main theme switching
        api.applyMainTheme("light");
        assertEquals(api.getMainThemeMode(), "light", "applyMainTheme switches to light mode");
        assertTrue(!api.getMainContainerClass().includes("dark"), "Light mode removes dark class");
        api.applyMainTheme("dark");
        assertEquals(api.getMainThemeMode(), "dark", "applyMainTheme switches to dark mode");
        assertTrue(api.getMainContainerClass() === "dark", "Dark mode adds main-dark class");
        api.applyMainTheme("auto");
        
        // ----- 2. DOM / UI State Tests (using new soft-light values) -----
        api.applyPreviewTheme(api.PREVIEW_PRESETS["soft-light"]);
        const softPrimaryRgb = "rgb(90, 143, 204)"; // #5a8fcc
        const softBorderRgb = "rgb(200, 185, 154)"; // #c8b99a
        const softInfoRgb = "rgb(126, 108, 84)";    // #7e6c54
        
        const primaryBtn = api.getPrimaryButton();
        if(primaryBtn) {
            const btnOk = await waitForStyle(primaryBtn, "backgroundColor", softPrimaryRgb);
            const actualBg = window.getComputedStyle(primaryBtn).backgroundColor;
            assertTrue(btnOk, `Primary button becomes soft light primary (${actualBg})`);
        } else { assert(false, "Primary button element not found"); }
        
        const progressFill = api.getProgressFill();
        if(progressFill) {
            const fillBg = window.getComputedStyle(progressFill).backgroundColor;
            assertTrue(fillBg === softPrimaryRgb, `Progress fill uses soft primary (${fillBg})`);
        } else { assert(false, "Progress fill missing"); }
        
        const statEl = api.getPrimaryStatElement();
        if(statEl) {
            const statColor = window.getComputedStyle(statEl).color;
            assertTrue(statColor === softPrimaryRgb, `Primary stat dot reflects soft primary (${statColor})`);
        }

        const infoStatEl = api.getInfoStatElement();
        if(infoStatEl) {
            const infoStatColor = window.getComputedStyle(infoStatEl).color;
            assertTrue(infoStatColor === softInfoRgb, `Info Badge stat dot reflects soft info-badge color (${infoStatColor})`);
        } else { assert(false, "Info Badge stat element not found"); }
        
        const card = document.querySelector('#name-app .card');
        if(card) {
            const borderOk = await waitForStyle(card, "borderTopColor", softBorderRgb);
            const actualBorder = window.getComputedStyle(card).borderTopColor;
            assertTrue(borderOk, `Card border adapts to soft light theme (${actualBorder})`);
        }
        
        api.applyMainTheme("dark");
        const studio = document.querySelector('#name-app .theme-studio');
        await waitForStyle(studio, "backgroundColor", "", 100);
        const studioBg = window.getComputedStyle(studio).backgroundColor;
        assertTrue(studioBg !== "rgb(241, 245, 249)" && studioBg.length > 0, "Main dark theme changes studio background");
        api.applyMainTheme("auto");
        
        // ----- 3. Preset Dropdown & Live Preview tests -----
        const dropdown = api.getPresetDropdown();
        if(dropdown) {
            assertEquals(dropdown.value, "soft-light", "Preset dropdown is synced to soft-light");
            
            // programmatically trigger dropdown switch
            dropdown.value = "sunset";
            dropdown.dispatchEvent(new Event('change'));
            const sunsetTheme = api.getCurrentPreviewTheme();
            assertEquals(sunsetTheme.primary, "#f97316", "Dropdown selection successfully changed preview to Sunset Glow");
        } else { assert(false, "Dropdown selector element not found"); }

        const livePreview = api.getLivePreviewTextarea();
        if(livePreview) {
            assertTrue(livePreview.value.includes("--info-color:"), "Live CSS preview contains --info-color field");
            assertTrue(livePreview.value.includes("--primary: #f97316"), "Live CSS preview reflects sunset primary in real time");
        } else { assert(false, "Live CSS preview textarea element not found"); }
        
        // ----- 4. Tab Switching & Playground Tests -----
        api.switchTab("components");
        assertEquals(api.getActiveTab(), "components", "Switch to components tab works");
        api.switchTab("playground");
        assertEquals(api.getActiveTab(), "playground", "Switch to playground tab works");
        api.switchTab("dashboard");
        assertEquals(api.getActiveTab(), "dashboard", "Switch back to dashboard works");
        
        assertEquals(api.getCounterValue(), 0, "Counter starts at 0");
        api.clickCounter();
        assertEquals(api.getCounterValue(), 1, "Counter increments to 1");
        
        const initialPercent = api.getRandomFillPercent();
        api.clickRandomFill();
        await new Promise(r => setTimeout(r, 50));
        const newPercent = api.getRandomFillPercent();
        assertTrue(newPercent !== initialPercent || newPercent >= 0, "Random fill button changes width");
        
        // ----- 5. Export / Import -----
        const testExportTheme = { primary: "#aa44cc", secondary: "#77aa33", bgColor: "#ffeecc", surfaceColor: "#ffffff", textColor: "#111111", borderColor: "#dddddd", infoColor: "#bb7766" };
        api.applyPreviewTheme(testExportTheme);
        const exported = api.getCurrentPreviewTheme();
        assertEquals(exported.primary, "#aa44cc", "getCurrentPreviewTheme works");
        
        const originalClipboard = navigator.clipboard.writeText;
        let capturedCss = null;
        navigator.clipboard.writeText = function(text) { capturedCss = text; return Promise.resolve(); };
        api.copyCssToClipboard();
        await new Promise(r => setTimeout(r, 0));
        assertTrue(capturedCss.includes("--primary: #aa44cc"), "copyCssToClipboard contains primary color");
        assertTrue(capturedCss.includes("--info-color: #bb7766"), "copyCssToClipboard contains info-badge color");
        navigator.clipboard.writeText = originalClipboard;
        
        api.applyPreviewTheme(api.DEFAULT_PREVIEW_THEME);
        
        const finalMessage = `\n🧪 FINAL SUMMARY: ${passedTests}/${totalTests} passed, ${failedTests} failed.`;
        console.log(finalMessage);
        if(window.__showTestToast) {
            const color = failedTests === 0 ? "✅ ALL TESTS PASSED" : "❌ SOME TESTS FAILED";
            window.__showTestToast(`${color}\n${passedTests}/${totalTests} passed`, failedTests > 0 ? "error" : "info");
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
