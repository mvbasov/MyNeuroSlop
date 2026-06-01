#!/bin/bash

# Directory to search (default to current directory)
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
    
    # Extract filename without path
    base_name=$(basename "$f1")
    
    # Extract the common part (everything before '_v')
    common_part="${base_name%%_v*}"
    
    # Extract version strings
    v1=$(echo "$base_name" | grep -o 'v[0-9]*_[0-9]*_[0-9]*')
    v2=$(echo "$(basename "$f2")" | grep -o 'v[0-9]*_[0-9]*_[0-9]*')
    
    # Create name: common_v1_to_v2.patch
    patch_name="${common_part}_${v1}_to_${v2}.patch"
    
    echo "Generating: $patch_name"
    diff -u "$f1" "$f2" > "$patch_name"
done

echo "Done. Patch files created in $DIR"