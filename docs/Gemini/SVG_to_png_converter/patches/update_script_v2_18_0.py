import os

# Target the previous v2.17.0 file
file_path = "svg_to_png_converter_v2_17_0.html"
output_filename = "svg_to_png_converter_v2_18_0.html"

with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# 1. Inject the conditional Testing API at the end of the IIFE
search_api = r"""            // Initial Load
            updateFormatUI();
            if (svgInput.value.trim()) {
                loadSVGToCanvas(svgInput.value.trim(), 'default_image.png', true);
                syncDataUrl();
            }

        })();"""

replace_api = r"""            // Initial Load
            updateFormatUI();
            if (svgInput.value.trim()) {
                loadSVGToCanvas(svgInput.value.trim(), 'default_image.png', true);
                syncDataUrl();
            }

            // --- Unit Testing API ---
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
            }

        })();"""

# 2. Bump the Version
search_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.17.0</span>"""
replace_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.18.0</span>"""

# Apply Replacements
updated_content = html_content.replace(search_api, replace_api)
updated_content = updated_content.replace(search_version, replace_version)

# Save the updated file
with open(output_filename, "w", encoding="utf-8") as file:
    file.write(updated_content)

print(f"Patch successfully applied! Saved as {output_filename}")