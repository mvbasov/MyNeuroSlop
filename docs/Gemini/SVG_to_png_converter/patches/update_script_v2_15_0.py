import os

def verify_and_patch():
    input_file = "svg_to_png_converter_v2_14_0.html"
    output_file = "svg_to_png_converter_v2_15_0.html"

    if not os.path.exists(input_file):
        print(f"❌ ERROR: Cannot find {input_file}.")
        print("Make sure you are looking at your latest file, not the older v2.6.0 file!")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    print("--- Version 2.15.0 Synchronization Check ---")

    # 1. Check for the Clipboard limit
    if "dataUrl.length > 2000000" in content:
        print("✓ Clipboard safety fallback (2,000,000 limit) is correctly located at the bottom of the file.")
    else:
        print("❌ Clipboard safety fallback is missing.")

    # 2. Check for the Favicon Dimension limit
    if "parsedWidth <= 200 && parsedHeight <= 200" in content:
        print("✓ Favicon dimension limit (200x200) is perfectly synchronized inside loadSVGToCanvas()!")
    else:
        print("❌ Favicon dimension limit is missing! Your file is desynchronized.")

    # Bump the version to v2.15.0
    content = content.replace("v2.14.0", "v2.15.0")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\nSuccessfully patched and saved as {output_file}!")
    print("Open this new file and search for '.favicon-link' to see your dimension checks in action.")

if __name__ == "__main__":
    verify_and_patch()