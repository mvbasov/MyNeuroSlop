import os

def patch_file():
    input_file = "svg_to_png_converter_v2_8_0.html"
    output_file = "svg_to_png_converter_v2_9_0.html"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Sync the injected xmlns back to the textarea
    search_1 = r"""                // Auto-inject xmlns if missing to prevent strict browser Image() parser errors
                let safeSvgString = svgString;
                if (!safeSvgString.match(/xmlns=["'][^"']+["']/i)) {
                    safeSvgString = safeSvgString.replace(/<svg/i, '<svg xmlns="http://www.w3.org/2000/svg"');
                }"""
                
    replace_1 = r"""                // Auto-inject xmlns if missing to prevent strict browser Image() parser errors
                let safeSvgString = svgString;
                if (!safeSvgString.match(/xmlns=["'][^"']+["']/i)) {
                    safeSvgString = safeSvgString.replace(/<svg/i, '<svg xmlns="http://www.w3.org/2000/svg"');
                    // Sync the fixed string back to the textarea immediately
                    svgInput.value = safeSvgString;
                    syncDataUrl();
                }"""
    content = content.replace(search_1, replace_1)

    # 2. Use safeSvgString for the Favicon Data URL generation
    search_2 = r"""                    // Protect browser performance by limiting complex headers 
                    if (parsedWidth <= 200 && parsedHeight <= 200) {
                        const compactSvg = encodeURIComponent(svgString.replace(/\s+/g, ' ').trim()).replace(/['()]/g, escape).replace(/\*/g, '%2A');
                        const dataUri = `data:image/svg+xml,${compactSvg}`;
                        document.querySelector('.favicon-link').href = dataUri;
                        
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(svgString, 'image/svg+xml');"""
                        
    replace_2 = r"""                    // Protect browser performance by limiting complex headers 
                    if (parsedWidth <= 200 && parsedHeight <= 200) {
                        const compactSvg = encodeURIComponent(safeSvgString.replace(/\s+/g, ' ').trim()).replace(/['()]/g, escape).replace(/\*/g, '%2A');
                        const dataUri = `data:image/svg+xml,${compactSvg}`;
                        document.querySelector('.favicon-link').href = dataUri;
                        
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(safeSvgString, 'image/svg+xml');"""
    content = content.replace(search_2, replace_2)

    # 3. Bump the version number to v2.9.0
    search_3 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.8.0</span>"""
    replace_3 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.9.0</span>"""
    content = content.replace(search_3, replace_3)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully patched! Saved as {output_file}")

if __name__ == "__main__":
    patch_file()