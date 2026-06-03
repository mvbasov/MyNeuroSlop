import os

def patch_file():
    input_file = "svg_to_png_converter_v2_11_0.html"
    output_file = "svg_to_png_converter_v2_12_0.html"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Combine string length limits with external viewBox dimension limits
    search_1 = r"""                    // The Favicon Data URI is limited by browser URL length limits (100k characters)
                    if (safeSvgString.length <= 100000) {"""
                
    replace_1 = r"""                    // The Favicon Data URI is limited by browser URL length limits and external viewBox dimensions
                    if (safeSvgString.length <= 100000 && parsedWidth <= 1024 && parsedHeight <= 1024) {"""
    content = content.replace(search_1, replace_1)

    # 2. Bump the version number to v2.12.0
    search_2 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.11.0</span>"""
    replace_2 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.12.0</span>"""
    content = content.replace(search_2, replace_2)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully patched! Saved as {output_file}")

if __name__ == "__main__":
    patch_file()