#!/bin/bash

# Script version
SCRIPT_VERSION="1.2.0"

# Function to show usage
show_help() {
    echo "Usage: ./generate_patches_named.sh [DIRECTORY]"
    echo "Finds files matching *_vX_Y_Z.html and generates diff patches."
    echo ""
    echo "Options:"
    echo "  -v, --version    Show script version"
    echo "  -h, --help       Show this help message"
}

# Handle flags
if [[ "$1" == "-v" || "$1" == "--version" ]]; then
    echo "Patch Generator Script v$SCRIPT_VERSION"
    exit 0
elif [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Directory to search
DIR="${1:-.}"

# Find files, sort by version
mapfile -t files < <(find "$DIR" -maxdepth 1 -name "*_v[0-9]*_[0-9]*_[0-9]*.html" | sort -V)

if [ ${#files[@]} -lt 2 ]; then
    echo "Not enough files found to create patches."
    exit 0
fi

echo "Found ${#files[@]} files. Creating patch files..."

for ((i=0; i < ${#files[@]}-1; i++)); do
    f1="${files[$i]}"
    f2="${files[$i+1]}"
    
    base_name=$(basename "$f1")
    common_part="${base_name%%_v*}"
    
    v1=$(echo "$base_name" | grep -o 'v[0-9]*_[0-9]*_[0-9]*')
    v2=$(echo "$(basename "$f2")" | grep -o 'v[0-9]*_[0-9]*_[0-9]*')
    
    patch_name="${common_part}_${v1}_to_${v2}.patch"
    
    echo "Generating: $patch_name"
    diff -u "$f1" "$f2" > "$patch_name"
done

echo "Done. Patch files created in $DIR"