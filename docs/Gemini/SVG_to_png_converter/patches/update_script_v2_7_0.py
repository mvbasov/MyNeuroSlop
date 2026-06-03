import os

def patch_file():
    input_file = "svg_to_png_converter_v2_6_0.html"
    output_file = "svg_to_png_converter_v2_7_0.html"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Inject HTML elements into the controls bar
    search_1 = r"""                <select id="sel-format">"""
    replace_1 = r"""                <button id="btn-load-file" class="btn-clear">Load SVG</button>
                <input type="file" id="file-input" accept=".svg" style="display: none;">
                <select id="sel-format">"""
    content = content.replace(search_1, replace_1)

    # 2. Inject JavaScript variable declarations
    search_2 = r"""            const chkWrap80 = app.querySelector('#chk-wrap-80');
            const statusToast = app.querySelector('#status-toast');"""
    replace_2 = r"""            const chkWrap80 = app.querySelector('#chk-wrap-80');
            const statusToast = app.querySelector('#status-toast');
            
            const btnLoadFile = app.querySelector('#btn-load-file');
            const fileInput = app.querySelector('#file-input');"""
    content = content.replace(search_2, replace_2)

    # 3. Inject the file loading event listeners
    search_3 = r"""            btnDownload.addEventListener('click', () => {"""
    replace_3 = r"""            btnLoadFile.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file && (file.type === 'image/svg+xml' || file.name.toLowerCase().endsWith('.svg'))) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        loadSVGToCanvas(event.target.result, file.name);
                        showStatus('SVG file loaded!');
                    };
                    reader.readAsText(file);
                } else if (file) {
                    showStatus('Please select a valid .svg file.', true);
                }
                e.target.value = ''; // Reset input so same file can be reloaded if needed
            });

            btnDownload.addEventListener('click', () => {"""
    content = content.replace(search_3, replace_3)

    # 4. Bump the version number
    search_4 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.6.0</span>"""
    replace_4 = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.7.0</span>"""
    content = content.replace(search_4, replace_4)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully patched! Saved as {output_file}")

if __name__ == "__main__":
    patch_file()