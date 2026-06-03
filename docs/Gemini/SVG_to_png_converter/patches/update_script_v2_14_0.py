import os

def patch_file():
    input_file = "svg_to_png_converter_v2_13_0.html"
    output_file = "svg_to_png_converter_v2_14_0.html"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add showStatus popup when xmlns is injected
    search_1 = r"""                let safeSvgString = svgString;
                if (!safeSvgString.match(/xmlns=["'][^"']+["']/i)) {
                    safeSvgString = safeSvgString.replace(/<svg/i, '<svg xmlns="http://www.w3.org/2000/svg"');
                    // Sync the fixed string back to the textarea immediately
                    svgInput.value = safeSvgString;
                    syncDataUrl();
                }"""
                
    replace_1 = r"""                let safeSvgString = svgString;
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
    content = content.replace(search_1, replace_1)

    # 2. Bump the version number to v2.14.0
    search_2 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.13.0</span>"""
    replace_2 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.14.0</span>"""
    content = content.replace(search_2, replace_2)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully patched! Saved as {output_file}")

if __name__ == "__main__":
    patch_file()