import os

file_path = "svg_to_png_converter_v2_15_1.html"
output_filename = "svg_to_png_converter_v2_16_0.html"

with open(file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# 1. Fix the BMP Signature Endianness
search_bmp_header = r"""                view.setUint16(0, 0x4D42, false); """
replace_bmp_header = r"""                view.setUint16(0, 0x4D42, true); """

# 2. Bump the Version
search_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.15.0</span>"""
replace_version = r"""<span class="version" style="font-size: 0.85rem; height: fit-content; padding: 2px 8px; margin-top: 4px; border-radius: 4px;">v2.16.0</span>"""

# Apply Replacements
updated_content = html_content.replace(search_bmp_header, replace_bmp_header)
updated_content = updated_content.replace(search_version, replace_version)

# Save the updated file
with open(output_filename, "w", encoding="utf-8") as file:
    file.write(updated_content)

print(f"Patch successfully applied! Saved as {output_filename}")