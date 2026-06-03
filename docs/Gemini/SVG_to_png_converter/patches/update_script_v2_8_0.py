import os

def patch_file():
    input_file = "svg_to_png_converter_v2_7_0.html"
    output_file = "svg_to_png_converter_v2_8_0.html"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject the auto-xmlns failsafe before creating the Blob
    search_1 = r"""                canvas.width = parsedWidth;
                canvas.height = parsedHeight;
                
                const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
                const url = URL.createObjectURL(blob);"""
                
    replace_1 = r"""                canvas.width = parsedWidth;
                canvas.height = parsedHeight;
                
                // Auto-inject xmlns if missing to prevent strict browser Image() parser errors
                let safeSvgString = svgString;
                if (!safeSvgString.match(/xmlns=["'][^"']+["']/i)) {
                    safeSvgString = safeSvgString.replace(/<svg/i, '<svg xmlns="http://www.w3.org/2000/svg"');
                }
                
                const blob = new Blob([safeSvgString], { type: 'image/svg+xml;charset=utf-8' });
                const url = URL.createObjectURL(blob);"""
                
    content = content.replace(search_1, replace_1)

    # 2. Bump the version number to v2.8.0
    search_2 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.7.0</span>"""
    replace_2 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.8.0</span>"""
    content = content.replace(search_2, replace_2)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully patched! Saved as {output_file}")

if __name__ == "__main__":
    patch_file()