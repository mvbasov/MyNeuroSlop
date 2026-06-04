#!/bin/bash

# BIP39 Converter Version Management Script
# Version: 1.4.0
# Usage:
#   ./manage_bip39.sh diff      - Create patches, keep latest
#   ./manage_bip39.sh restore   - Interactively select version to restore to ./restored
#   ./manage_bip39.sh add <new_version> - Run update script and generate new patches
#   ./manage_bip39.sh version   - Show current script version

set -e

SCRIPT_VERSION="1.4.0"

# Extracts clean version strings, completely filtering out raw file paths
get_versions() {
    (
        # Extract version from converter files: e.g. bip39_converter_v1_14_1.html -> 1_14_1
        ls bip39_converter_v* 2>/dev/null | sed -n -E 's/.*v([0-9_]+)(\.(html|htm)|_tests\.js)$/\1/p'
        # Extract versions from patch files: e.g. patches/patch_1_1_0_to_1_2_0.diff -> 1_1_0 and 1_2_0
        ls patches/patch_*.diff 2>/dev/null | sed -n -E 's|.*/patch_(tests_)?([0-9_]+)_to_([0-9_]+)\.diff$|\2\n\3|p'
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
    local dest_dir="restored"
    
    echo "Select a version to restore:"
    select target in "${versions[@]}"; do
        if [ -z "$target" ]; then echo "Invalid selection."; continue; fi
        
        echo "Creating restoration directory: ./${dest_dir}"
        mkdir -p "$dest_dir"
        
        echo "Restoring v$target to ./${dest_dir} from latest v$latest..."
        local ext=$(ls "bip39_converter_v$latest."* 2>/dev/null | grep -E '\.(html|htm)$' | head -1 | sed 's/.*\.//')
        
        # Copy the latest base files directly into the restoration directory
        cp "bip39_converter_v$latest.$ext" "$dest_dir/bip39_converter_v$target.$ext"
        if [ -f "bip39_converter_v${latest}_tests.js" ]; then
            cp "bip39_converter_v${latest}_tests.js" "$dest_dir/bip39_converter_v$target""_tests.js"
        fi
        
        # Convert target underscores to dots for reliable version-sorting comparison
        local target_dots=$(echo "$target" | tr '_' '.')

        # Apply patches in reverse directly to the files in the restored folder
        for ((i=${#versions[@]}-2; i>=0; i--)); do
            local v_from="${versions[i+1]}"
            local v_to="${versions[i]}"
            
            # Convert current version loop target to dots
            local v_to_dots=$(echo "$v_to" | tr '_' '.')

            # Skip if this patch isn't in our backwards path to the target
            if [ "$(printf '%s\n%s' "$target_dots" "$v_to_dots" | sort -V | head -n1)" != "$target_dots" ]; then
                continue
            fi
            
            echo "Applying reverse patch: $v_from -> $v_to"
            if [ -f "patches/patch_${v_to}_to_${v_from}.diff" ]; then
                patch -R "$dest_dir/bip39_converter_v$target.$ext" < "patches/patch_${v_to}_to_${v_from}.diff"
            fi
            if [ -f "patches/patch_tests_${v_to}_to_${v_from}.diff" ]; then
                patch -R "$dest_dir/bip39_converter_v$target""_tests.js" < "patches/patch_tests_${v_to}_to_${v_from}.diff"
            fi
            
            if [[ "$v_to" == "$target" ]]; then break; fi
        done
        echo "Successfully restored v$target to ./${dest_dir}/bip39_converter_v$target.$ext"
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