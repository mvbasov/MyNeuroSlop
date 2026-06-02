import sys
import os

def patch_file():
    # Target the v1.28.0 file
    file_path = "svg_to_png_converter_v1_28_0.html"
    
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Hunk 1: Expand the root container ONLY within the desktop media query
    search1 = r"""        @media (min-width: 700px) {
            #svg-to-png-app .main-content {
                display: grid !important;
                grid-template-columns: 6fr 4fr;
                grid-template-rows: 1fr auto;
                align-items: stretch;
                gap: 24px;
            }"""

    replace1 = r"""        @media (min-width: 700px) {
            #svg-to-png-app {
                max-width: 100%;
                width: calc(100% - 48px);
                margin: 24px auto;
                min-height: calc(100vh - 48px);
                display: flex;
                flex-direction: column;
            }
            #svg-to-png-app .main-content {
                flex-grow: 1;
                display: grid !important;
                grid-template-columns: 6fr 4fr;
                grid-template-rows: 1fr auto;
                align-items: stretch;
                gap: 24px;
            }"""

    # Hunk 2: Version Bump
    search2 = r"""<span class="version">v1.28.0</span>"""
    replace2 = r"""<span class="version">v1.29.0</span>"""

    # Apply patches
    if search1 in content and search2 in content:
        content = content.replace(search1, replace1)
        content = content.replace(search2, replace2)

        output_filename = "svg_to_png_converter_v1_29_0.html"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_filename} (v1.29.0)!")
    else:
        print("Error: Could not find target strings to replace. Ensure you are targeting the unaltered v1.28.0 file.")

if __name__ == "__main__":
    patch_file()