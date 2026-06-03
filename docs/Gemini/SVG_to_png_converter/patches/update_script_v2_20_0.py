import os

# Target the previous v2.19.0 file
file_path = "svg_to_png_converter_v2_19_0.html"
output_filename = "svg_to_png_converter_v2_20_0.html"

with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# 1. Inject the Micro-Testing Framework into the API block
search_api = r"""            // --- Unit Testing API ---
            // Conditionally exposes internal mathematical and parsing functions.
            // Only activates if '?test=true' is appended to the URL.
            if (window.location.search.includes('test=true')) {
                window.__TEST_API__ = {
                    formatXML: formatXML,
                    canvasToBMP: canvasToBMP,
                    loadSVGToCanvas: loadSVGToCanvas,
                    syncDataUrl: syncDataUrl,
                    syncFromDataUrl: syncFromDataUrl
                };
                console.log("🧪 SVG Converter Unit Testing API exposed at window.__TEST_API__");
            }"""

replace_api = r"""            // --- Unit Testing API & Micro-Framework ---
            // Conditionally exposes internals and an automated test runner.
            if (window.location.search.includes('test=')) {
                window.__TEST_API__ = {
                    formatXML: formatXML,
                    canvasToBMP: canvasToBMP,
                    loadSVGToCanvas: loadSVGToCanvas,
                    syncDataUrl: syncDataUrl,
                    syncFromDataUrl: syncFromDataUrl
                };
                console.log("🧪 Unit Testing API exposed at window.__TEST_API__");

                // Built-in Automated Micro-Framework
                window.__TEST_API__.runAll = function() {
                    console.log("%c🚀 Starting Automated Unit Tests...", "color: #4A90E2; font-weight: bold; font-size: 14px;");
                    let passed = 0, failed = 0;

                    // The Assertion Engine
                    function assert(name, actual, expected) {
                        if (actual === expected) {
                            console.log(`%c✅ PASS: ${name}`, "color: #4CAF50; font-weight: bold;");
                            passed++;
                        } else {
                            console.error(`❌ FAIL: ${name}\n   Expected: ${expected}\n   Actual:   ${actual}`);
                            failed++;
                        }
                    }

                    // --- Define Your Automated Tests Here ---
                    assert("formatXML: Empty <svg> keeps closing tag", 
                        formatXML("<svg></svg>"), "<svg></svg>");
                    
                    assert("formatXML: Empty <g> keeps closing tag", 
                        formatXML("<svg><g></g></svg>"), "<svg>\n  <g></g>\n</svg>");
                    
                    assert("formatXML: Empty <circle> collapses", 
                        formatXML("<svg><circle></circle></svg>"), "<svg>\n  <circle/>\n</svg>");
                        
                    assert("formatXML: Base format stripping", 
                        formatXML('<circle   r="5"  />'), '<circle r="5"/>');

                    // Summary Output
                    const color = failed > 0 ? '#f44336' : '#4CAF50';
                    console.log(`%c🏁 Test Run Complete: ${passed} Passed, ${failed} Failed`, `font-weight: bold; font-size: 14px; color: ${color}`);
                };

                // Auto-run trigger
                if (window.location.search.includes('test=run')) {
                    setTimeout(() => window.__TEST_API__.runAll(), 500);
                } else {
                    console.log("💡 Type window.__TEST_API__.runAll() to execute tests, or append '?test=run' to the URL.");
                }
            }"""

# 2. Bump the Version
search_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.19.0</span>"""
replace_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.20.0</span>"""

# Apply Replacements
updated_content = html_content.replace(search_api, replace_api)
updated_content = updated_content.replace(search_version, replace_version)

with open(output_filename, "w", encoding="utf-8") as file:
    file.write(updated_content)

print(f"Patch successfully applied! Saved as {output_filename}")