import sys

def patch_file():
    input_file = "bip39_converter_v1_2_0.html"
    output_file = "bip39_converter_v1_3_0.html"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    # 1. Bump the application version gracefully
    content = content.replace("v1.2.0", "v1.3.0")

    # 2. Update the dynamic test script loader reference
    search_str = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_2_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_2_0_tests.js");
        document.body.appendChild(script);"""

    replace_str = r"""        const script = document.createElement('script');
        script.src = 'bip39_converter_v1_3_0_tests.js';
        script.onerror = () => console.error("Test suite file not found: bip39_converter_v1_3_0_tests.js");
        document.body.appendChild(script);"""

    if search_str not in content:
        print("Error: Target string not found. Ensure you are running this against the clean v1.2.0 file.")
    else:
        content = content.replace(search_str, replace_str)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully generated {output_file}")

if __name__ == "__main__":
    patch_file()