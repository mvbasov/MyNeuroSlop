#!/bin/bash

# BIP39 Converter Version Management Script
# Version: 1.3.2
# Usage:
#   ./manage_bip39.sh diff      - Create patches, keep latest
#   ./manage_bip39.sh restore   - Interactively select version to restore
#   ./manage_bip39.sh add <new_version> - Run update script and generate new patches
#   ./manage_bip39.sh version   - Show current script version

set -e

SCRIPT_VERSION="1.3.2"

get_versions() {
    (
        ls bip39_converter_v* 2>/dev/null | sed -E 's/.*v([0-9_]+)(\..*|_tests\.js)/\1/'
        ls patches/patch_*_to_*.diff 2>/dev/null | sed -E 's/.*v([0-9_]+)_to_([0-9_]+)\.diff/\1\n\2/'
    ) | sort -V | uniq
}

make_patches() {
    local versions=($(get_versions))
    local count=${#versions[@]}
    if [ "$count" -lt 2 ]; then
        echo "Error: Need at least two versions to create a patch."
        return
    fi

    set +e
    for ((i=0; i<$count-1; i++)); do
        v1="${versions[$i]}"
        v2="${versions[$i+1]}"
        
        ext=$(ls "bip39_converter_v$v1."* 2>/dev/null | grep -E '\.(html|htm)$' | head -1 | sed 's/.*\.//')
        
        if [ -n "$ext" ] && [ -f "bip39_converter_v$v1.$ext" ]; then
            echo "Creating patch: v$v1 -> v$v2"
            diff -u "bip39_converter_v$v1.$ext" "bip39_converter_v$v2.$ext" > "patches/patch_${v1}_to_${v2}.diff"
            if [ $? -eq 0 ] || [ $? -eq 1 ]; then rm -f "bip39_converter_v$v1.$ext"; fi
        fi
        
        if [ -f "bip39_converter_v$v1""_tests.js" ]; then
            diff -u "bip39_converter_v$v1""_tests.js" "bip39_converter_v$v2""_tests.js" > "patches/patch_tests_${v1}_to_${v2}.diff"
            if [ $? -eq 0 ] || [ $? -eq 1 ]; then rm -f "bip39_converter_v$v1""_tests.js"; fi
        fi
    done
    set -e
}

restore_version() {
    local versions=($(get_versions))
    local latest="${versions[-1]}"
    
    echo "Select a version to restore:"
    # This displays only the version numbers as the selectable list
    select target in "${versions[@]}"; do
        if [ -z "$target" ]; then echo "Invalid selection."; continue; fi
        
        echo "Restoring v$target from v$latest..."
        local ext=$(ls "bip39_converter_v$latest."* 2>/dev/null | grep -E '\.(html|htm)$' | head -1 | sed 's/.*\.//')
        
        cp "bip39_converter_v$latest.$ext" "bip39_converter_v$target.$ext"
        [ -f "bip39_converter_v${latest}_tests.js" ] && cp "bip39_converter_v${latest}_tests.js" "bip39_converter_v$target""_tests.js"
        
        for ((i=${#versions[@]}-2; i>=0; i--)); do
            local v_from="${versions[i+1]}"
            local v_to="${versions[i]}"
            
            if [ "$(printf '%s\n%s' "$target" "$v_to" | sort -V | head -n1)" != "$target" ]; then
                continue
            fi
            
            echo "Applying patch: $v_from -> $v_to"
            [ -f "patches/patch_${v_to}_to_${v_from}.diff" ] && patch -R "bip39_converter_v$target.$ext" < "patches/patch_${v_to}_to_${v_from}.diff"
            [ -f "patches/patch_tests_${v_to}_to_${v_from}.diff" ] && patch -R "bip39_converter_v$target""_tests.js" < "patches/patch_tests_${v_to}_to_${v_from}.diff"
            
            if [[ "$v_to" == "$target" ]]; then break; fi
        done
        echo "Successfully restored v$target"
        break
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