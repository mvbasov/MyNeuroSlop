import re
import sys
import os

def fix_trailing_commas(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex explanation:
        # ,       - matches a literal comma
        # \s* - matches zero or more whitespace characters (spaces, newlines)
        # ([\]}]) - matches and captures a closing bracket ] or brace }
        # r'\1'   - replaces the whole match with just the captured bracket/brace
        fixed_content = re.sub(r',\s*([\]}])', r'\1', content)

        if content != fixed_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"[SUCCESS] Fixed redundant trailing commas in: {file_path}")
        else:
            print(f"[INFO] No trailing commas needed fixing in: {file_path}")

    except Exception as e:
        print(f"[ERROR] Could not process {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_json_commas.py <path_to_file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        fix_trailing_commas(target)
    elif os.path.isdir(target):
        print(f"Scanning directory: {target}")
        for root, _, files in os.walk(target):
            for file in files:
                if file.endswith(('.md', '.json', '.txt')):
                    fix_trailing_commas(os.path.join(root, file))
    else:
        print(f"[ERROR] Target path not found: {target}")