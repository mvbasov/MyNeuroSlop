#!/bin/bash

# BIP39 Converter Version Management Script
# Version: 1.2.0
# Usage:
#   ./manage_bip39.sh diff      - Create patches for .html/.htm and _tests.js, keep latest
#   ./manage_bip39.sh restore   - Interactively select version to restore
#   ./manage_bip39.sh add <new_version> - Run update script and generate new patches
#   ./manage_bip39.sh version   - Show current script version

set -e

SCRIPT_VERSION="1.2.0"

get_versions() {
    # Match both .html and .htm files
    ls bip39_converter_v* | grep -E '\.(html|htm)$' | sed -E 's/.*v([0-9_]+)\.(html|htm)/\1/' | sort -V | uniq
}

make_patches() {
    local versions=($(get_versions))
    local count=${#versions[@]}
    if [ "$count" -lt 2 ]; then
        echo "Need at least two versions to create a patch."
        return
    fi

    set +e
    for ((i=0; i<$count-1; i++)); do
        v1="${versions[$i]}"
        v2="${versions[$i+1]}"
        
        # Determine current extension
        ext=$(ls "bip39_converter_v$v1."* | grep -E '\.(html|htm)$' | head -1 | sed 's/.*\.//')
        
        echo "Creating patches: v$v1 -> v$v2"
        
        # Diff Main File
        diff -u "bip39_converter_v$v1.$ext" "bip39_converter_v$v2.$ext" > "patches/patch_${v1}_to_${v2}.diff"
        
        # Diff Test File
        if [ -f "bip39_converter_v$v1""_tests.js" ]; then
            diff -u "bip39_converter_v$v1""_tests.js" "bip39_converter_v$v2""_tests.js" > "patches/patch_tests_${v1}_to_${v2}.diff"
        fi
        
        # Cleanup if successful
        if [ $? -eq 0 ] || [ $? -eq 1 ]; then
            rm "bip39_converter_v$v1.$ext"
            rm -f "bip39_converter_v$v1""_tests.js"
            echo "Files for $v1 cleaned up."
        fi
    done
    set -e
    echo "Patches created. Latest version: v${versions[-1]}"
}

restore_version() {
    local versions=($(get_versions))
    echo "Available versions for restoration:"
    select v in "${versions[@]}"; do
        if [ -n "$v" ]; then
            echo "Restoring v$v..."
            local ext=$(ls "bip39_converter_v${versions[-1]}."* | grep -E '\.(html|htm)$' | head -1 | sed 's/.*\.//')
            cp "bip39_converter_v${versions[-1]}.$ext" "bip39_converter_v$v.$ext"
            if [ -f "bip39_converter_v${versions[-1]}_tests.js" ]; then
                cp "bip39_converter_v${versions[-1]}_tests.js" "bip39_converter_v$v""_tests.js"
            fi
            break
        else
            echo "Invalid selection."
        fi
    done
}

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
    restore) restore_version ;;
    add)     add_new_version "$2" ;;
    version) echo "BIP39 Manager Script v$SCRIPT_VERSION" ;;
    *)       echo "Usage: $0 {diff|restore|add <ver>|version}" ;;
esac