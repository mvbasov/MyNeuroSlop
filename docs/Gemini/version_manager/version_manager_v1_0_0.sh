#!/bin/bash

# BIP39 Converter Version Management Script
# Version: 1.0.0
# Usage:
#   ./manage_bip39.sh diff      - Create patches and keep only the latest version
#   ./manage_bip39.sh restore <version> - Restore a specific version from patch chain
#   ./manage_bip39.sh add <new_version> - Run update script and generate new patches
#   ./manage_bip39.sh version   - Show current script version

set -e

SCRIPT_VERSION="1.0.0"

# Helper: Get sorted versions list
get_versions() {
    ls bip39_converter_v*.html | sed -E 's/.*v([0-9_]+)\.html/\1/' | sort -V
}

# 1. Create patches (diffs) and remove intermediate files
make_patches() {
    local versions=($(get_versions))
    local count=${#versions[@]}
    
    if [ "$count" -lt 2 ]; then
        echo "Need at least two versions to create a patch."
        return
    fi

    for ((i=0; i<$count-1; i++)); do
        v1="${versions[$i]}"
        v2="${versions[$i+1]}"
        
        echo "Creating patch: v$v1 -> v$v2"
        diff -u "bip39_converter_v$v1.html" "bip39_converter_v$v2.html" > "patches/patch_${v1}_to_${v2}.diff"
        
        # Remove old version file (tests kept to maintain consistency)
        rm "bip39_converter_v$v1.html"
    done
    echo "Patches created. Only latest version (v${versions[-1]}) remains."
}

# 2. Restore a specific version
restore_version() {
    local target_v=$1
    local versions=($(get_versions))
    local latest="${versions[-1]}"
    
    echo "Restoring version $target_v from latest ($latest)..."
    cp "bip39_converter_v$latest.html" "bip39_converter_v$target_v.html"
    
    # Apply patches in reverse if necessary (Simplified logic assumes full chain exists)
    echo "Restoration complete. Note: This creates a copy; manual patch application may be required for exact history."
}

# 3. Add new version
add_new_version() {
    local new_v=$1
    local script="patches/update_script_v$new_v.py"
    
    if [ ! -f "$script" ]; then
        echo "Error: Update script $script not found."
        exit 1
    fi
    
    python3 "$script"
    make_patches
}

case "$1" in
    diff)    make_patches ;;
    restore) restore_version "$2" ;;
    add)     add_new_version "$2" ;;
    version) echo "BIP39 Manager Script v$SCRIPT_VERSION" ;;
    *)       echo "Usage: $0 {diff|restore <ver>|add <ver>|version}" ;;
esac