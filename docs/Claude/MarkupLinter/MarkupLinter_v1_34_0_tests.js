(function() {
    const results = {
        total: 0,
        passed: 0,
        failed: 0,
        details: []
    };

    function assert(name, actual, expected, message = '') {
        results.total++;
        if (actual === expected) {
            results.passed++;
            results.details.push({ name, status: 'PASS' });
            console.log(`  🟢 %c✔ PASS%c: ${name}`, 'color: #10b981; font-weight: bold;', '');
        } else {
            results.failed++;
            const failMsg = `Expected [${expected}], got [${actual}]. ${message}`;
            results.details.push({ name, status: 'FAIL', error: failMsg });
            console.log(`  🔴 %c✘ FAIL%c: ${name} — ${failMsg}`, 'color: #ef4444; font-weight: bold;', '');
        }
    }

    function assertTrue(name, condition, message = '') {
        assert(name, !!condition, true, message);
    }

    window.__runTests = async function() {
        console.log("%c==================================================", 'color: #3b82f6; font-weight: bold;');
        console.log("🚀 %cStarting Markup Linter Unit Test Suite...%c", 'font-weight: bold; font-size: 14px; color: #3b82f6;', '');
        console.log("%c==================================================", 'color: #3b82f6; font-weight: bold;');
        
        const api = window.__TEST_API__;
        if (!api) {
            console.error("🔴 %cError: Test API is not exposed! Please append ?test=run to your URL.%c", 'color: #ef4444; font-weight: bold;', '');
            return;
        }

        // Capture initial app state for full test isolation
        const initialEditorVal = api.getEditor().value;
        const initialMode = api.getModeSelect().value;
        const initialWrap = api.getLineWrapEnabled();
        const initialLineNumbers = api.getShowLineNumbers();

        try {
            // Test Case 1: HTML Validation Correctness
            console.log("\n🔷 %cTest Case 1: HTML unclosed tag error recognition%c", 'font-weight: bold; color: #8b5cf6;', '');
            api.getModeSelect().value = 'html';
            api.initContent(`<div>\n  <p>Hello\n</div>`);
            const htmlErrors = api.getCurrentErrors();
            assertTrue("HTML: Detects unclosed paragraph tag", htmlErrors.some(e => e.message.includes("Unclosed tag <p>")));

            // Test Case 2: HTML Mismatched Tags
            console.log("\n🔷 %cTest Case 2: HTML mismatched tag detections%c", 'font-weight: bold; color: #8b5cf6;', '');
            api.initContent(`<div>\n  <span>Hello</p>\n</div>`);
            const htmlMismatched = api.getCurrentErrors();
            assertTrue("HTML: Detects mismatched tags", htmlMismatched.some(e => e.message.includes("Mismatched closing")));

            // Test Case 3: XML/SVG Correctness (Strict parser)
            console.log("\n🔷 %cTest Case 3: XML/SVG strict parser validation%c", 'font-weight: bold; color: #8b5cf6;', '');
            api.getModeSelect().value = 'xml';
            api.initContent(`<svg>\n  <path d="M10 10" />\n  <g>\n</svg>`);
            const xmlErrors = api.getCurrentErrors();
            assertTrue("XML: Detects unclosed tag in strict mode", xmlErrors.length > 0);

            // Test Case 4: Line Number Toggle Syncing
            console.log("\n🔷 %cTest Case 4: Line numbers count validation%c", 'font-weight: bold; color: #8b5cf6;', '');
            // Normalize UI state so the line-number gutter is actually visible before we
            // measure it. On a display:none element, .innerText collapses the <br>-separated
            // numbers into one line ("1.2.3."), which would make this assertion depend on the
            // user's saved wrap / line-number preferences rather than the counting logic.
            if (api.getLineWrapEnabled()) api.toggleWrap();        // wrap hides the gutter
            if (!api.getShowLineNumbers()) api.toggleLineNumbers(); // must be off-wrap first (toggle no-ops under wrap)
            api.getModeSelect().value = 'html';
            api.initContent("one\ntwo\nthree");
            const initialLineNumCount = api.getLineNumbersDiv().innerText.split('\n').filter(Boolean).length;
            assert("Line Numbers: Count matches total lines in file", initialLineNumCount, 3);

            // Test Case 5: Scroll Syncing Viewport checks
            console.log("\n🔷 %cTest Case 5: Scroll offset synchronization%c", 'font-weight: bold; color: #8b5cf6;', '');
            const editor = api.getEditor();
            editor.scrollTop = 100;
            editor.dispatchEvent(new Event('scroll'));
            assert("Scroll Sync: Line numbers div scrolled matching the editor", api.getLineNumbersDiv().scrollTop, editor.scrollTop);

            // Test Case 6: Optional Wrapping Toggle
            console.log("\n🔷 %cTest Case 6: Optional wrapping adaptive visibility%c", 'font-weight: bold; color: #8b5cf6;', '');
            if (api.getLineWrapEnabled()) {
                api.toggleWrap(); // Ensure off first
            }
            api.toggleWrap(); // Turn wrap ON
            assert("Wrap: Wrap status set to enabled", api.getLineWrapEnabled(), true);
            assert("Wrap adaptive layout: Line numbers hidden when wrap is enabled to prevent vertical drift", api.getLineNumbersDiv().style.display, 'none');
            
            api.toggleWrap(); // Turn wrap OFF
            assert("Wrap: Wrap status restored to disabled", api.getLineWrapEnabled(), false);

            // Test Case 7: Innermost error detection logic (depth prioritizing)
            console.log("\n🔷 %cTest Case 7: Innermost nested tag depth prioritizations%c", 'font-weight: bold; color: #8b5cf6;', '');
            api.initContent(`<div>\n  <span>\n    <p>\n      <b>Bold missing closing\n    </p>\n  </span>\n</div>`);
            const errors = api.getCurrentErrors();
            const deepest = errors.reduce((max, e) => (e.depth || 0) > (max.depth || 0) ? e : max, errors[0]);
            assertTrue("Innermost Error: Identified deep tag error inside nested blocks", (deepest.depth || 0) >= 3);

            // Test Case 8: UI Updates (Valid and Invalid Summary Badge States)
            console.log("\n🔷 %cTest Case 8: UI Validation state representation%c", 'font-weight: bold; color: #8b5cf6;', '');
            api.initContent(`<div>Hello World</div>`);
            const summaryOk = api.getSummaryLabel().innerText;
            assertTrue("UI Badge: Shows green valid validation badge for valid markup", summaryOk.includes("Valid markup"));

            api.initContent(`<div>Unclosed`);
            const summaryErr = api.getSummaryLabel().innerText;
            assertTrue("UI Badge: Shows warning validation badge when error count > 0", summaryErr.includes("error(s) found"));

            // Test Case 9: JSON valid input passes cleanly
            console.log("\n🔷 %cTest Case 9: JSON valid parsing%c", 'font-weight: bold; color: #8b5cf6;', '');
            api.getModeSelect().value = 'json';
            api.initContent(`{\n  "name": "test",\n  "items": [1, 2, 3],\n  "nested": { "ok": true }\n}`);
            assert("JSON: Valid object reports zero errors", api.getCurrentErrors().length, 0);

            // Test Case 10: JSON invalid input is caught with a line number
            console.log("\n🔷 %cTest Case 10: JSON invalid detection + line mapping%c", 'font-weight: bold; color: #8b5cf6;', '');
            api.initContent(`{\n  "a": 1,\n  "b": 2\n  "c": 3\n}`);
            const jsonErrors = api.getCurrentErrors();
            assertTrue("JSON: Detects a syntax error in malformed JSON", jsonErrors.length > 0);
            assertTrue("JSON: Error message is labelled as a JSON parse error", jsonErrors.some(e => e.message.includes("JSON parse")));
            assertTrue("JSON: Error carries a plausible line number (>= 3)", jsonErrors.length > 0 && jsonErrors[0].line >= 3);

            // Test Case 11: JSON direct validator handles truncated input
            console.log("\n🔷 %cTest Case 11: JSON truncated input via direct validator%c", 'font-weight: bold; color: #8b5cf6;', '');
            const truncErrors = api.validateJson(`{\n  "unterminated": [1, 2, 3`);
            assertTrue("JSON: Truncated input yields at least one error", truncErrors.length > 0);

            // ---------------------------------------------------------------
            // Test Cases 12-16 guard the strict-mode line number.
            //
            // A DOMParser parse error names TWO lines: where the parser stopped
            // (end of file, for an unclosed tag) and where the offending tag
            // was opened. Reading the wrong one is invisible to a test that
            // only asks whether an error exists -- which is exactly how a
            // version shipped reporting line 4 on desktop and line 8 on
            // Android. These cases assert the line itself.
            // ---------------------------------------------------------------

            // The page's own demo document: the <img> on line 4 is never
            // closed, and the file ends on line 8.
            const DEMO_XML = '<div>\n  <h1>Title</h1>\n  <p>Text</p>\n  <img src="photo.jpg" alt="demo" >\n  <span class="test">Text\n    <b>Bold</b>\n  </span>\n</div>';

            // Test Case 12: through the UI, the way a person hits it
            console.log("\n🔷 %cTest Case 12: XML strict reports the opening line, not EOF%c", 'font-weight: bold; color: #8b5cf6;', '');
            api.getModeSelect().value = 'xml';
            api.initContent(DEMO_XML);
            const demoErrors = api.getCurrentErrors();
            assertTrue("XML: unclosed <img> produces an error", demoErrors.length > 0);
            assert("XML: error sits on the line the tag was OPENED (4), not the end of file (8)",
                   demoErrors.length ? demoErrors[0].line : -1, 4);

            // Test Case 13: tag names the old \w+ pattern could not read
            console.log("\n🔷 %cTest Case 13: namespaced and hyphenated tag names%c", 'font-weight: bold; color: #8b5cf6;', '');
            const nsErrors = api.validateXmlSvg('<root xmlns:s="urn:x">\n  <s:box>\n</root>');
            assert("XML: namespaced <s:box> reported at its opening line",
                   nsErrors.length ? nsErrors[0].line : -1, 2);
            const hyphenErrors = api.validateXmlSvg('<root>\n  <my-tag>\n</root>');
            assert("XML: hyphenated <my-tag> reported at its opening line",
                   hyphenErrors.length ? hyphenErrors[0].line : -1, 2);

            // Test Case 14: THE regression test. Same document, same fault,
            // different engine wording -- the line must not move. The wordings
            // below are a real older-libxml2 phrasing, a localized message, and
            // a namespaced tag, each of which defeated the old regex and sent
            // the report to the last line of the file.
            console.log("\n🔷 %cTest Case 14: line survives the engine's wording%c", 'font-weight: bold; color: #8b5cf6;', '');
            const originalParseFromString = DOMParser.prototype.parseFromString;
            const WORDINGS = [
                ['older libxml2', 'This page contains the following errors:error on line 8 at column 7: Premature end of data in tag img line 4\nBelow is a rendering of the page up to the first error.'],
                ['localized', 'Diese Seite enthält die folgenden Fehler:error on line 8 at column 7: Nicht übereinstimmende Tags: img line 4 and div\nUnten folgt eine Darstellung der Seite.'],
                ['namespaced tag', 'This page contains the following errors:error on line 8 at column 7: Opening and ending tag mismatch: svg:image line 4 and div\nBelow is a rendering of the page up to the first error.']
            ];
            try {
                for (const [label, text] of WORDINGS) {
                    DOMParser.prototype.parseFromString = function(str, type) {
                        const parsed = originalParseFromString.call(this, str, type);
                        const pe = parsed.querySelector('parsererror');
                        if (pe) pe.textContent = text;
                        return parsed;
                    };
                    const worded = api.validateXmlSvg(DEMO_XML);
                    assert("XML: still line 4 when the engine words it as " + label,
                           worded.length ? worded[0].line : -1, 4);
                }
            } finally {
                DOMParser.prototype.parseFromString = originalParseFromString;
            }

            // Test Case 15: the fix must not over-reach. A fault that is NOT
            // about tag nesting has no "opening line" to find, and the parser's
            // own stop position is the right answer for it.
            console.log("\n🔷 %cTest Case 15: non-structural faults keep the parser's position%c", 'font-weight: bold; color: #8b5cf6;', '');
            const attrErrors = api.validateXmlSvg('<a b=<c>\n</a>');
            assertTrue("XML: a malformed attribute is still reported", attrErrors.length > 0);
            assert("XML: malformed attribute keeps the parser's own line",
                   attrErrors.length ? attrErrors[0].line : -1, 1);
            const rootsErrors = api.validateXmlSvg('<a/>\n<b/>');
            assert("XML: a second root element is reported where it starts",
                   rootsErrors.length ? rootsErrors[0].line : -1, 2);

            // Test Case 16: and a well-formed document stays silent
            console.log("\n🔷 %cTest Case 16: well-formed XML reports nothing%c", 'font-weight: bold; color: #8b5cf6;', '');
            assert("XML: well-formed document yields zero errors",
                   api.validateXmlSvg('<a>\n  <b/>\n</a>').length, 0);

        } catch (err) {
            console.error("🔴 Error during test execution:", err);
            results.failed++;
            results.details.push({ name: "Global execution error", status: "FAIL", error: err.toString() });
        } finally {
            // Restore initial state as required (Full state reset)
            api.getEditor().value = initialEditorVal;
            api.getModeSelect().value = initialMode;
            if (api.getLineWrapEnabled() !== initialWrap) {
                api.toggleWrap();
            }
            if (api.getShowLineNumbers() !== initialLineNumbers) {
                api.toggleLineNumbers();
            }
            api.runValidation();

            // Success Metrics calculation
            const successRate = Math.round((results.passed / results.total) * 100);

            // Print beautiful tabular summaries
            console.log("\n");
            console.log("%c==================================================", 'color: #10b981; font-weight: bold;');
            console.log("📋 %cASSERTION SPECIFICATION RESULTS%c", 'font-weight: bold; font-size: 13px; color: #10b981;', '');
            console.log("%c==================================================", 'color: #10b981; font-weight: bold;');
            console.table(results.details.map(d => ({
                "Test Aspect Name": d.name,
                "Status": d.status === 'PASS' ? '🟢 PASS' : '🔴 FAIL',
                "Details": d.error || '✔️ OK (Passed)'
            })));

            console.log("\n");
            console.log("%c==================================================", 'color: #10b981; font-weight: bold;');
            console.log("📊 %cSUMMARY REPORT%c", 'font-weight: bold; font-size: 13px; color: #10b981;', '');
            console.log("%c==================================================", 'color: #10b981; font-weight: bold;');
            console.table({
                "Total Assertions": results.total,
                "Passed Assertions": results.passed,
                "Failed Assertions": results.failed,
                "Success Rate": `${successRate}%`
            });

            // Display final score toast
            const toastMsg = results.failed === 0 
                ? `🏆 Test Suite Passed! ${results.passed}/${results.total} asserts OK (100% success rate)`
                : `⚠️ Test Suite Finished: ${results.passed}/${results.total} assertions passed (${successRate}% success rate). Failed: ${results.failed}`;
            
            api.showToast(toastMsg, 7000, true);
        }
    };
})();
