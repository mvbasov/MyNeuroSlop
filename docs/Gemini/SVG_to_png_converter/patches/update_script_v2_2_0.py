import sys
import os

def patch_file():
    # Target the v2.1.0 file
    file_path = "svg_to_png_converter_v2_1_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Fix the condition to check for dimensions <= 200 instead of string length
    search_logic = r"""                    // Update Favicon and Header dynamically (with fallback for massive SVGs to prevent browser freezing)
                    if (svgString.length < 200000) {
                        const compactSvg = encodeURIComponent(svgString.replace(/\s+/g, ' ').trim()).replace(/['()]/g, escape).replace(/\*/g, '%2A');
                        const dataUri = `data:image/svg+xml,${compactSvg}`;
                        
                        document.querySelector('.favicon-link').href = dataUri;
                        
                        // Parse elements out of SVG and inject them into the header SVG icon to mirror appearance
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(svgString, 'image/svg+xml');
                        if (!doc.querySelector('parsererror')) {
                            const svgNode = doc.documentElement;
                            headerFavicon.setAttribute('viewBox', svgNode.getAttribute('viewBox') || '0 0 100 100');
                            headerFavicon.innerHTML = svgNode.innerHTML;
                        }
                    } else {
                        // Fallback to default icon if the string is too large (> 200,000 characters)
                        document.querySelector('.favicon-link').href = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%234A90E2'/%3E%3Ctext x='50' y='65' font-family='sans-serif' font-size='40' font-weight='bold' fill='white' text-anchor='middle'%3EIMG%3C/text%3E%3C/svg%3E";
                        headerFavicon.setAttribute('viewBox', '0 0 100 100');
                        headerFavicon.innerHTML = '<rect width="100" height="100" rx="20" fill="var(--accent-color)" /><text x="50" y="65" font-family="sans-serif" font-size="40" font-weight="bold" fill="white" text-anchor="middle">IMG</text>';
                    }"""
                    
    replace_logic = r"""                    // Update Favicon and Header dynamically (only if max dimension is 200 or less)
                    if (parsedWidth <= 200 && parsedHeight <= 200) {
                        const compactSvg = encodeURIComponent(svgString.replace(/\s+/g, ' ').trim()).replace(/['()]/g, escape).replace(/\*/g, '%2A');
                        const dataUri = `data:image/svg+xml,${compactSvg}`;
                        
                        document.querySelector('.favicon-link').href = dataUri;
                        
                        // Parse elements out of SVG and inject them into the header SVG icon to mirror appearance
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(svgString, 'image/svg+xml');
                        if (!doc.querySelector('parsererror')) {
                            const svgNode = doc.documentElement;
                            headerFavicon.setAttribute('viewBox', svgNode.getAttribute('viewBox') || '0 0 100 100');
                            headerFavicon.innerHTML = svgNode.innerHTML;
                        }
                    } else {
                        // Fallback to default icon if dimensions are greater than 200
                        document.querySelector('.favicon-link').href = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%234A90E2'/%3E%3Ctext x='50' y='65' font-family='sans-serif' font-size='40' font-weight='bold' fill='white' text-anchor='middle'%3EIMG%3C/text%3E%3C/svg%3E";
                        headerFavicon.setAttribute('viewBox', '0 0 100 100');
                        headerFavicon.innerHTML = '<rect width="100" height="100" rx="20" fill="var(--accent-color)" /><text x="50" y="65" font-family="sans-serif" font-size="40" font-weight="bold" fill="white" text-anchor="middle">IMG</text>';
                    }"""

    if search_logic in content:
        content = content.replace(search_logic, replace_logic)
    else:
        print("Notice: Exact Favicon update logic block not found. Ensure you are targeting the unaltered v2.1.0 file.")

    # Hunk 2: Global Version Bump
    if 'v2.1.0' in content:
        content = content.replace('v2.1.0', 'v2.2.0')

    # Output to new version
    output_filename = "svg_to_png_converter_v2_2_0.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully generated {output_filename} (v2.2.0)!")

if __name__ == "__main__":
    patch_file()