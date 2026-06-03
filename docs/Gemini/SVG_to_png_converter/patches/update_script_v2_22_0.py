import os

# Target the previous v2.21.0 file
file_path = "svg_to_png_converter_v2_21_0.html"
output_html = "svg_to_png_converter_v2_22_0.html"
test_file_name = "test_suite_v2_22_0.js"

with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# 1. Update the dynamic loader to request the strictly versioned test file
search_loader = r"""                // Dynamically inject the external testing framework
                const script = document.createElement('script');
                script.src = 'test_suite.js';
                script.onload = () => {
                    if (window.location.search.includes('test=run') && window.__runTests) {
                        setTimeout(() => window.__runTests(), 500);
                    }
                };
                script.onerror = () => console.error("❌ Failed to load test_suite.js. Ensure it is in the same directory.");"""

replace_loader = r"""                // Dynamically inject the external testing framework
                const script = document.createElement('script');
                script.src = 'test_suite_v2_22_0.js';
                script.onload = () => {
                    if (window.location.search.includes('test=run') && window.__runTests) {
                        setTimeout(() => window.__runTests(), 500);
                    }
                };
                script.onerror = () => console.error("❌ Failed to load test_suite_v2_22_0.js. Ensure it is in the same directory.");"""

# 2. Bump the Version
search_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.21.0</span>"""
replace_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.22.0</span>"""

# Apply Replacements
updated_content = html_content.replace(search_loader, replace_loader)
updated_content = updated_content.replace(search_version, replace_version)

# 3. Create the version-locked test suite file content
test_suite_js = """// test_suite_v2_22_0.js - Offline Micro-Testing Framework
window.__runTests = function() {
    console.log("%c🚀 Starting Automated Unit Tests...", "color: #4A90E2; font-weight: bold; font-size: 14px;");
    let passed = 0, failed = 0;
    
    // Grab the exposed functions from the host HTML file
    const api = window.__TEST_API__;

    // The Assertion Engine
    function assert(name, actual, expected) {
        if (actual === expected) {
            console.log(`%c✅ PASS: ${name}`, "color: #4CAF50; font-weight: bold;");
            passed++;
        } else {
            console.error(`❌ FAIL: ${name}\\n   Expected: ${expected}\\n   Actual:   ${actual}`);
            failed++;
        }
    }

    // --- Define Your Automated Tests Here ---
    assert("formatXML: Empty <svg> keeps closing tag", 
        api.formatXML("<svg></svg>"), "<svg></svg>");
    
    assert("formatXML: Empty <g> keeps closing tag", 
        api.formatXML("<svg><g></g></svg>"), "<svg>\\n  <g></g>\\n</svg>");
    
    assert("formatXML: Empty <circle> collapses", 
        api.formatXML("<svg><circle></circle></svg>"), "<svg>\\n  <circle/>\\n</svg>");
        
    assert("formatXML: Base format stripping", 
        api.formatXML('<circle   r="5"  />'), '<circle r="5"/>');

    // Summary Output
    const color = failed > 0 ? '#f44336' : '#4CAF50';
    console.log(`%c🏁 Test Run Complete: ${passed} Passed, ${failed} Failed`, `font-weight: bold; font-size: 14px; color: ${color}`);
};

console.log("💡 test_suite_v2_22_0.js loaded successfully. Type window.__runTests() to execute, or use '?test=run' in URL.");
"""

# Save the updated HTML file
with open(output_html, "w", encoding="utf-8") as file:
    file.write(updated_content)

# Save the versioned test suite file
with open(test_file_name, "w", encoding="utf-8") as file:
    file.write(test_suite_js)

print(f"Patch successfully applied! Saved {output_html}")
print(f"Extracted testing framework to: {test_file_name}")