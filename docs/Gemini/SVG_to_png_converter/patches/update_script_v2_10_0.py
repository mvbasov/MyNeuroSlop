import os

def patch_file():
    input_file = "svg_to_png_converter_v2_9_0.html"
    output_file = "svg_to_png_converter_v2_10_0.html"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace geometric limit with string size limit for Favicons
    search_1 = r"""                    // Protect browser performance by limiting complex headers 
                    if (parsedWidth <= 200 && parsedHeight <= 200) {
                        const compactSvg = encodeURIComponent(safeSvgString.replace(/\s+/g, ' ').trim()).replace(/['()]/g, escape).replace(/\*/g, '%2A');"""
                
    replace_1 = r"""                    // Protect browser performance by limiting string size instead of geometric dimensions
                    if (safeSvgString.length <= 100000) {
                        const compactSvg = encodeURIComponent(safeSvgString.replace(/\s+/g, ' ').trim()).replace(/['()]/g, escape).replace(/\*/g, '%2A');"""
    content = content.replace(search_1, replace_1)

    # 2. Bump the version number to v2.10.0
    search_2 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.9.0</span>"""
    replace_2 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.10.0</span>"""
    content = content.replace(search_2, replace_2)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully patched! Saved as {output_file}")

if __name__ == "__main__":
    patch_file()