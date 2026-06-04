#!/bin/bash

# Project Version Management Script
# Version: 1.8.0
# Usage:
#   ./manage_versions.sh diff      - Create patches, keep latest
#   ./manage_versions.sh restore   - Interactively select version to restore to ./restored
#   ./manage_versions.sh clean     - Safely clean restored files if recoverable from patches
#   ./manage_versions.sh add <new_version> - Run update script and generate new patches
#   ./manage_versions.sh version   - Show current script version

set -e

SCRIPT_VERSION="1.8.0"

# Read project name from environment variable; default to generic "converter" if not set
PROJECT_NAME="${PROJECT_NAME:-converter}"

echo "Using Project Name: $PROJECT_NAME"

# Extracts clean version strings, completely filtering out raw file paths
get_versions() {
    (
        # Extract version from converter/script files: e.g. converter_v1_14_1.html or utility_v1_0_0.sh -> 1_14_1 or 1_0_0
        ls ${PROJECT_NAME}_v* 2>/dev/null | sed -n -E 's/.*v([0-9_]+)(\.(html|htm|sh)|_tests\.js)$/\1/p'
        # Extract versions from patch files: e.g. patches/patch_1_1_0_to_1_2_0.diff -> 1_1_0 and 1_2_0
        ls patches/patch_*.diff 2>/dev/null | sed -n -E 's|.*/patch_(tests_)?([0-9_]+)_to_([0-9_]+)\.diff$|\2\n\3|p'
    ) | sort -V | uniq
}

# Verifies if a specific version has a complete patch chain up to any existing base version
check_recoverable() {
    local target=$1
    local versions=($(get_versions))
    
    # Find the highest existing version file in the root directory to act as the source base
    local base_version=""
    for v in "${versions[@]}"; do
        if ls "${PROJECT_NAME}_v$v."* 2>/dev/null | grep -q -E '\.(html|htm|sh)$'; then
            base_version="$v"
        fi
    done
    
    # If no base file exists, we can't recover anything
    if [ -z "$base_version" ]; then
        return 1
    fi
    
    # The base version itself is inherently "recoverable" (it's already there)
    if [[ "$target" == "$base_version" ]]; then
        return 0
    fi
    
    # Determine indices of base and target in the versions array
    local idx_base=-1
    local idx_target=-1
    for idx in "${!versions[@]}"; do
        if [[ "${versions[$idx]}" == "$base_version" ]]; then idx_base=$idx; fi
        if [[ "${versions[$idx]}" == "$target" ]]; then idx_target=$idx; fi
    done
    
    if [ $idx_base -eq -1 ] || [ $idx_target -eq -1 ]; then
        return 1
    fi
    
    # Check the completeness of the patch chain
    if [ $idx_base -gt $idx_target ]; then
        # Going backward: check patches from target up to base
        for ((j=idx_target; j<idx_base; j++)); do
            local v1="${versions[$j]}"
            local v2="${versions[$j+1]}"
            if [ ! -f "patches/patch_${v1}_to_${v2}.diff" ]; then
                return 1
            fi
        done
    else
        # Going forward: check patches from base up to target
        for ((j=idx_base; j<idx_target; j++)); do
            local v1="${versions[$j]}"
            local v2="${versions[$j+1]}"
            if [ ! -f "patches/patch_${v1}_to_${v2}.diff" ]; then
                return 1
            fi
        done
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
        
        ext=$(ls "${PROJECT_NAME}_v$v1."* 2>/dev/null | grep -E '\.(html|htm|sh)$' | head -1 | sed 's/.*\.//')
        
        if [ -n "$ext" ] && [ -f "${PROJECT_NAME}_v$v1.$ext" ]; then
            echo "Creating patch: v$v1 -> v$v2"
            diff -u "${PROJECT_NAME}_v$v1.$ext" "${PROJECT_NAME}_v$v2.$ext" > "patches/patch_${v1}_to_${v2}.diff"
            if [ $? -eq 0 ] || [ $? -eq 1 ]; then rm -f "${PROJECT_NAME}_v$v1.$ext"; fi
        fi
        
        if [ -f "${PROJECT_NAME}_v${v1}_tests.js" ]; then
            diff -u "${PROJECT_NAME}_v${v1}_tests.js" "${PROJECT_NAME}_v${v2}_tests.js" > "patches/patch_tests_${v1}_to_${v2}.diff"
            if [ $? -eq 0 ] || [ $? -eq 1 ]; then rm -f "${PROJECT_NAME}_v${v1}_tests.js"; fi
        fi
    done
    set -e
}

restore_version() {
    local versions=($(get_versions))
    
    # 1. Dynamically locate the highest physical version file in the root directory to act as base
    local base_version=""
    local ext=""
    for v in "${versions[@]}"; do
        local found_ext=$(ls "${PROJECT_NAME}_v$v."* 2>/dev/null | grep -E '\.(html|htm|sh)$' | head -1 | sed 's/.*\.//')
        if [ -n "$found_ext" ]; then
            base_version="$v"
            ext="$found_ext"
        fi
    done

    if [ -z "$base_version" ]; then
        echo "Error: No base ${PROJECT_NAME}_v*.html/htm/sh file found in the root directory to use as a restoration base."
        exit 1
    fi

    echo "Select a version to restore:"
    select target in "${versions[@]}"; do
        if [ -z "$target" ]; then echo "Invalid selection."; continue; fi
        
        local dest_dir="restored"
        echo "Creating restoration directory: ./${dest_dir}"
        mkdir -p "$dest_dir"
        
        echo "Restoring v$target to ./${dest_dir} using existing base v$base_version..."
        
        # Copy the physical base files directly into the restoration directory
        cp "${PROJECT_NAME}_v$base_version.$ext" "$dest_dir/${PROJECT_NAME}_v$target.$ext"
        if [ -f "${PROJECT_NAME}_v${base_version}_tests.js" ]; then
            cp "${PROJECT_NAME}_v${base_version}_tests.js" "$dest_dir/${PROJECT_NAME}_v${target}_tests.js"
        fi
        
        # Determine index locations
        local idx_base=-1
        local idx_target=-1
        for idx in "${!versions[@]}"; do
            if [[ "${versions[$idx]}" == "$base_version" ]]; then idx_base=$idx; fi
            if [[ "${versions[$idx]}" == "$target" ]]; then idx_target=$idx; fi
        done

        if [ $idx_base -eq -1 ] || [ $idx_target -eq -1 ]; then
            echo "Error: Could not determine version indices."
            break
        fi

        # Apply appropriate forward or backward patch chains
        if [ $idx_base -gt $idx_target ]; then
            # Target is older: apply REVERSE patches backwards from base index down to target index
            for ((i=idx_base-1; i>=idx_target; i--)); do
                local v_to="${versions[$i]}"
                local v_from="${versions[$i+1]}"
                echo "Applying reverse patch: $v_from -> $v_to"
                if [ -f "patches/patch_${v_to}_to_${v_from}.diff" ]; then
                    patch -R "$dest_dir/${PROJECT_NAME}_v$target.$ext" < "patches/patch_${v_to}_to_${v_from}.diff"
                fi
                if [ -f "patches/patch_tests_${v_to}_to_${v_from}.diff" ]; then
                    [ ! -f "$dest_dir/${PROJECT_NAME}_v${target}_tests.js" ] && touch "$dest_dir/${PROJECT_NAME}_v${target}_tests.js"
                    patch -R "$dest_dir/${PROJECT_NAME}_v${target}_tests.js" < "patches/patch_tests_${v_to}_to_${v_from}.diff"
                fi
            done
        elif [ $idx_base -lt $idx_target ]; then
            # Target is newer: apply FORWARD patches from base index up to target index
            for ((i=idx_base; i<idx_target; i++)); do
                local v_from="${versions[$i]}"
                local v_to="${versions[$i+1]}"
                echo "Applying forward patch: $v_from -> $v_to"
                if [ -f "patches/patch_${v_from}_to_${v_to}.diff" ]; then
                    patch "$dest_dir/${PROJECT_NAME}_v$target.$ext" < "patches/patch_${v_from}_to_${v_to}.diff"
                fi
                if [ -f "patches/patch_tests_${v_from}_to_${v_to}.diff" ]; then
                    [ ! -f "$dest_dir/${PROJECT_NAME}_v${target}_tests.js" ] && touch "$dest_dir/${PROJECT_NAME}_v${target}_tests.js"
                    patch "$dest_dir/${PROJECT_NAME}_v${target}_tests.js" < "patches/patch_tests_${v_from}_to_${v_to}.diff"
                fi
            done
        fi

        # Prune target test file if it ended up empty
        if [ -f "$dest_dir/${PROJECT_NAME}_v${target}_tests.js" ] && [ ! -s "$dest_dir/${PROJECT_NAME}_v${target}_tests.js" ]; then
            rm -f "$dest_dir/${PROJECT_NAME}_v${target}_tests.js"
        fi

        echo "Successfully restored v$target to ./${dest_dir}/${PROJECT_NAME}_v$target.$ext"
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
            rm -f "$dest_dir/${PROJECT_NAME}_v${ver}_tests.js"
        else
            echo "WARNING: Version v$ver is NOT fully recoverable (broken patch chain)! Keeping files in ./${dest_dir} to prevent data loss."
        fi
    }
    
    if [ -n "$target_ver" ]; then
        # Clean up a single specified version
        local found=false
        for f in "$dest_dir"/${PROJECT_NAME}_v"$target_ver".*; do
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
        local files=($(ls "$dest_dir"/${PROJECT_NAME}_v* 2>/dev/null | grep -E '\.(html|htm|sh)$' || true))
        if [ ${#files[@]} -eq 0 ]; then
            echo "No restored HTML/HTM/SH files found in ./${dest_dir}"
            rm -rf "$dest_dir"/*_tests.js 2>/dev/null || true
            rmdir "$dest_dir" 2>/dev/null || true
            return
        fi
        
        for f in "${files[@]}"; do
            local ver=$(echo "$f" | sed -n -E 's/.*v([0-9_]+)\.(html|htm|sh)$/\1/p')
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
    version) echo "${PROJECT_NAME} Manager Script v$SCRIPT_VERSION" ;;
    *)       echo "Usage: $0 {diff|restore|clean [ver]|add <ver>|version}" ;;
esac