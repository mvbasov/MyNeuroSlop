import re
import sys
import os

def fix_json_formatting(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Fix redundant trailing commas
        # Matches a comma, followed by whitespace/newlines, followed by a closing bracket/brace
        fixed_content = re.sub(r',(\s*[\]}])', r'\1', content)

        # 2. Fix invalid backslash escapes (like \m or stray \)
        # JSON only allows \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
        # This regex finds any backslash NOT followed by a valid JSON escape character
        # and escapes it properly by doubling it (\\)
        fixed_content = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', fixed_content)

        if content != fixed_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"[SUCCESS] Fixed formatting (commas/escapes) in: {file_path}")
        else:
            print(f"[INFO] No fixes needed for: {file_path}")

    except Exception as e:
        print(f"[ERROR] Could not process {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_json_commas.py <path_to_file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        fix_json_formatting(target)
    elif os.path.isdir(target):
        print(f"Scanning directory: {target}")
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith(('.md', '.json', '.txt')):
                    fix_json_formatting(os.path.join(root, file))
    else:
        print(f"[ERROR] Target path not found: {target}")