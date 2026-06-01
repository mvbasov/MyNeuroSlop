#!/bin/bash

# Script version
SCRIPT_VERSION="1.2.2"

# Function to show usage
show_help() {
    echo "Usage: ./make_patches.sh [DIRECTORY] [EXTENSION]"
    echo "Finds files matching *_vX_Y_Z.EXTENSION and generates diff patches."
    echo ""
    echo "Arguments:"
    echo "  DIRECTORY    Target directory to search (default: .)"
    echo "  EXTENSION    File extension to look for (default: html)"
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

# Define arguments
TARGET_DIR="${1:-.}"
EXT="${2:-html}"

# Validate directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

# Find files, sort by version
mapfile -t files < <(find "$TARGET_DIR" -maxdepth 1 -name "*_v[0-9]*_[0-9]*_[0-9]*.$EXT" | sort -V)

# FIXED: Changed [ ${#files[@]] to [ ${#files[@]} ]
if [ ${#files[@]} -lt 2 ]; then
    echo "Not enough files found (extension: .$EXT) in '$TARGET_DIR' to create patches."
    exit 0
fi

echo "Found ${#files[@]} files. Creating patch files in '$TARGET_DIR'..."

for ((i=0; i < ${#files[@]}-1; i++)); do
    f1="${files[$i]}"
    f2="${files[$i+1]}"
    
    # Extract filename without path
    base_name=$(basename "$f1")
    
    # Extract the common part (everything before the first '_v')
    common_part="${base_name%%_v*}"
    
    # Extract version strings for file naming
    v1=$(echo "$base_name" | grep -o 'v[0-9]*_[0-9]*_[0-9]*')
    v2=$(echo "$(basename "$f2")" | grep -o 'v[0-9]*_[0-9]*_[0-9]*')
    
    # Create patch filename inside the target directory
    patch_name="${TARGET_DIR}/${common_part}_${v1}_to_${v2}.patch"
    
    echo "Generating: $(basename "$patch_name")"
    diff -u "$f1" "$f2" > "$patch_name"
done

echo "Done. All .patch files have been created in '$TARGET_DIR'."