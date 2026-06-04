#!/bin/bash

# BIP39 Converter Version Management Script
# Version: 1.5.0
# Usage:
#   ./manage_bip39.sh diff      - Create patches, keep latest
#   ./manage_bip39.sh restore   - Interactively select version to restore to ./restored
#   ./manage_bip39.sh clean     - Safely clean restored files if recoverable from patches
#   ./manage_bip39.sh add <new_version> - Run update script and generate new patches
#   ./manage_bip39.sh version   - Show current script version

set -e

SCRIPT_VERSION="1.5.0"

# Extracts clean version strings, completely filtering out raw file paths
get_versions() {
    (
        # Extract version from converter files: e.g. bip39_converter_v1_14_1.html -> 1_14_1
        ls bip39_converter_v* 2>/dev/null | sed -n -E 's/.*v([0-9_]+)(\.(html|htm)|_tests\.js)$/\1/p'
        # Extract versions from patch files: e.g. patches/patch_1_1_0_to_1_2_0.diff -> 1_1_0 and 1_2_0
        ls patches/patch_*.diff 2>/dev/null | sed -n -E 's|.*/patch_(tests_)?([0-9_]+)_to_([0-9_]+)\.diff$|\2\n\3|p'
    ) | sort -V | uniq
}

# Verifies if a specific version has a complete patch chain up to the latest version
check_recoverable() {
    local target=$1
    local versions=($(get_versions))
    local latest="${versions[-1]}"
    
    # The latest version is the source base, so it is always inherently "recoverable"
    if [[ "$target" == "$latest" ]]; then
        return 0
    fi
    
    local found_target=false
    for ((j=0; j<${#versions[@]}-1; j++)); do
        local v1="${versions[$j]}"
        local v2="${versions[$j+1]}"
        
        if [[ "$v1" == "$target" ]]; then
            found_target=true
        fi
        
        if [ "$found_target" = true ]; then
            # Verify the main HTML patch exists
            if [ ! -f "patches/patch_${v1}_to_${v2}.diff" ]; then
                return 1 # Chain is broken
            fi
            # Verify the tests patch also exists if the latest version uses tests
            if [ -f "bip39_converter_v${latest}_tests.js" ] && [ ! -f "patches/patch_tests_${v1}_to_${v2}.diff" ]; then
                return 1 # Tests chain is broken
            fi
        fi
    done
    
    if [ "$found_target" = false ]; then
        return 1 # Version doesn't exist in our known sequence
    fi
    return 0
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

# Safely cleans up files inside the restored directory
clean_restored() {
    local target_ver=$1
    local dest_dir="restored"
    
    if [ ! -d "$dest_dir" ]; then
        echo "No restored directory found at ./${dest_dir}"
        return
    fi
    
    # Internal function to process single version deletion with a safety check
    delete_if_recoverable() {
        local ver=$1
        local file_path=$2
        
        if check_recoverable "$ver"; then
            echo "Version v$ver is fully recoverable. Deleting $file_path..."
            rm -f "$file_path"
            # Delete corresponding test suite file if it exists
            rm -f "$dest_dir/bip39_converter_v${ver}_tests.js"
        else
            echo "WARNING: Version v$ver is NOT fully recoverable (broken patch chain)! Keeping files in ./${dest_dir} to prevent data loss."
        fi
    }
    
    if [ -n "$target_ver" ]; then
        # Clean up a single specified version
        local found=false
        for f in "$dest_dir"/bip39_converter_v"$target_ver".*; do
            if [ -f "$f" ]; then
                found=true
                delete_if_recoverable "$target_ver" "$f"
            fi
        done
        if [ "$found" = false ]; then
            echo "No restored files found for version v$target_ver in ./${dest_dir}"
        fi
    else
        # Clean up all files in the restored folder
        echo "Scanning ./${dest_dir} for restored versions..."
        local files=($(ls "$dest_dir"/bip39_converter_v* 2>/dev/null | grep -E '\.(html|htm)$' || true))
        if [ ${#files[@]} -eq 0 ]; then
            echo "No restored HTML/HTM files found in ./${dest_dir}"
            rm -rf "$dest_dir"/*_tests.js 2>/dev/null || true
            rmdir "$dest_dir" 2>/dev/null || true
            return
        fi
        
        for f in "${files[@]}"; do
            local ver=$(echo "$f" | sed -n -E 's/.*v([0-9_]+)\.(html|htm)$/\1/p')
            if [ -n "$ver" ]; then
                delete_if_recoverable "$ver" "$f"
            fi
        done
        
        # Prune directory if now empty
        if [ -d "$dest_dir" ] && [ -z "$(ls -A "$dest_dir" 2>/dev/null)" ]; then
            echo "Removing empty directory ./${dest_dir}"
            rmdir "$dest_dir"
        fi
    fi
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
    clean)   clean_restored "$2" ;;
    add)     add_new_version "$2" ;;
    version) echo "BIP39 Manager Script v$SCRIPT_VERSION" ;;
    *)       echo "Usage: $0 {diff|restore|clean [ver]|add <ver>|version}" ;;
esac