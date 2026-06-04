import os

source_file = "svg_component_editor_v6_5_0.html"
output_file = "svg_component_editor_v6_6_0.html"

try:
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Strip comments from the code string before running the viewBox match
    # Using raw triple quotes avoids Python escape character issues
    old_str = r"""let viewBoxMatch = code.match(/viewBox=["']([^"']+)["']/i);"""
    new_str = r"""let viewBoxMatch = code.replace(/<!--[\s\S]*?-->/g, '').match(/viewBox=["']([^"']+)["']/i);"""

    if old_str not in content:
        print("Warning: Could not find the target string to replace. Was the file already patched?")
    else:
        content = content.replace(old_str, new_str)
        
        # Update version strings
        content = content.replace("v6.5.0", "v6.6.0")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Successfully patched! The viewBox logic now respects comments.")
        print(f"Saved layout as: {output_file}")

except FileNotFoundError:
    print(f"Error: Could not find {source_file} in the current directory.")