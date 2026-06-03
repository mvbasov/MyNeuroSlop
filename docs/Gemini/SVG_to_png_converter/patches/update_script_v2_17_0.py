import os

# Ensure this targets the previously updated v2.16.0 file
file_path = "svg_to_png_converter_v2_16_0.html"
output_filename = "svg_to_png_converter_v2_17_0.html"

with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# 1. Inject the explicit dimension failsafe
search_dims = r"""                // Auto-inject xmlns if missing to prevent strict browser Image() parser errors
                let safeSvgString = svgString;
                if (!safeSvgString.match(/xmlns=["'][^"']+["']/i)) {
                    safeSvgString = safeSvgString.replace(/<svg/i, '<svg xmlns="http://www.w3.org/2000/svg"');
                    // Sync the fixed string back to the textarea immediately
                    svgInput.value = safeSvgString;
                    syncDataUrl();
                    // Alert the user sequentially (delayed to prevent overlapping the file load toast)
                    setTimeout(() => {
                        showStatus('Added missing xmlns namespace for compatibility.', false);
                    }, 2500);
                }"""

replace_dims = r"""                // Auto-inject xmlns if missing to prevent strict browser Image() parser errors
                let safeSvgString = svgString;
                if (!safeSvgString.match(/xmlns=["'][^"']+["']/i)) {
                    safeSvgString = safeSvgString.replace(/<svg/i, '<svg xmlns="http://www.w3.org/2000/svg"');
                    // Sync the fixed string back to the textarea immediately
                    svgInput.value = safeSvgString;
                    syncDataUrl();
                    // Alert the user sequentially (delayed to prevent overlapping the file load toast)
                    setTimeout(() => {
                        showStatus('Added missing xmlns namespace for compatibility.', false);
                    }, 2500);
                }
                
                // Force explicit dimensions. Browsers like Firefox and Safari will silently fail to
                // draw an SVG onto a canvas if the root <svg> tag lacks explicit width and height attributes.
                if (!safeSvgString.match(/\swidth=["'][^"']+["']/i)) {
                    safeSvgString = safeSvgString.replace(/<svg/i, `<svg width="${parsedWidth}"`);
                }
                if (!safeSvgString.match(/\sheight=["'][^"']+["']/i)) {
                    safeSvgString = safeSvgString.replace(/<svg/i, `<svg height="${parsedHeight}"`);
                }"""

# 2. Bump the Version
search_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.16.0</span>"""
replace_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.17.0</span>"""

# Apply Replacements
updated_content = html_content.replace(search_dims, replace_dims)
updated_content = updated_content.replace(search_version, replace_version)

# Save the updated file
with open(output_filename, "w", encoding="utf-8") as file:
    file.write(updated_content)

print(f"Patch successfully applied! Saved as {output_filename}")