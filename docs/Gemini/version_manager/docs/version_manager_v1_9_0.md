# Project Version Management Script (v1.7.0)

A lightweight, robust, and automated Git-like version management system written in Bash. This script allows developers to track sequential versions of a project (both main files and associated test suites), generate incremental delta patches using unified diffs, clean up intermediate versions to save space, and dynamically reconstruct any historical or future version on demand.

## Table of Contents
1. [Key Features](#key-features)
2. [Directory Structure](#directory-structure)
3. [Environment Configuration](#environment-configuration)
4. [Command Reference](#command-reference)
5. [How the Magic Works](#how-the-magic-works)
6. [Step-by-Step Workflow Example](#step-by-step-workflow-example)

## Key Features
* **Sequential Diff Chains:** Generates space-saving unified patches (`.diff`) between adjacent versions (e.g., `v1_1_0 -> v1_2_0`).
* **Supports Multiple File Types:** Automatically tracks primary code files (supporting `.html` and `.htm` extensions) and corresponding test files (`_tests.js`).
* **Dynamic Project Scoping:** Uses environment variables to configure the project target, removing hardcoded paths and allowing multi-project reuse.
* **Bidirectional Restoration:** Reconstructs both older (reverse patching) and newer (forward patching) versions based on whatever files exist in the working directory.
* **Automated Update Script Integration:** Executes custom Python update scripts to generate and seamlessly patch new releases.
* **Safety-First Cleanups:** Verifies that a restored version is fully recoverable from the current patch set before allowing deletion.

## Directory Structure
To function correctly, the script expects and manages files in the following layout:
```
├── manage_versions.sh             # The Version Management Script
├── bip39_converter_v[VERSION].html # Primary physical code file (e.g., bip39_converter_v1_14_1.html)
├── bip39_converter_v[VERSION]_tests.js # Optional associated test suite file
├── restored/                      # Destination directory for restored files (auto-generated)
│   ├── bip39_converter_v[VERSION].html
│   └── bip39_converter_v[VERSION]_tests.js
└── patches/                       # Storage for unified patches and update scripts
    ├── patch_[v_from]_to_[v_to].diff
    ├── patch_tests_[v_from]_to_[v_to].diff
    └── update_script_v[VERSION].py # Python scripts for generating newer versions
```

## Environment Configuration
The script adapts dynamically to different projects via the `PROJECT_NAME` environment variable.

* **Variable:** `PROJECT_NAME`
* **Default:** `converter` (if the variable is empty or unset)
* **Usage:**
  Before running the script, export the target name matching your file patterns:
  ```bash
  export PROJECT_NAME="bip39_converter"
  ./manage_versions.sh restore
  ```
This allows the same system to manage `bip39_converter_v*.html`, `ethereum_wallet_v*.html`, or any other format effortlessly.

## Command Reference

### 1. `diff`
Processes all existing files in the root folder, generates unified patches between adjacent sorted versions, and removes the older source files.
```bash
./manage_versions.sh diff
```
* **Process:**
  * Sorts all detected versions (using semantic versioning sequence).
  * Creates unified patches: `patches/patch_[v1]_to_[v2].diff` and `patches/patch_tests_[v1]_to_[v2].diff`.
  * Safely deletes the files for `v1` once diffs are successfully written, keeping only the highest version intact.

### 2. `restore`
Launches an interactive Text User Interface (TUI) to select and recreate any known version from the history.
```bash
./manage_versions.sh restore
```
* **Process:**
  * Lists all restorable versions (detected from local files and existing `.diff` files).
  * Prompts you to pick a version.
  * Automatically targets `./restored/` as the sandbox.
  * Copies the nearest physical base version and applies patch chains (either forward or backward) to reconstruct the exact chosen version.

### 3. `clean`
Removes files inside the `./restored` directory, verifying first that they can be safely rebuilt in the future.
```bash
./manage_versions.sh clean [optional_version]
```
* **Options:**
  * `./manage_versions.sh clean` — Safely cleans up all files inside `./restored`.
  * `./manage_versions.sh clean 1_12_0` — Targets only the specified version for safe cleanup.
* **Safety Guardrail:**
  The script steps through the required patch chains. If a `.diff` is missing or corrupted, the deletion is halted, protecting your source code from permanent loss.

### 4. `add`
Runs a Python patch script to transition the project to a newer version and automatically generates the updated diff chain.
```bash
./manage_versions.sh add <new_version>
```
* **Usage Example:**
  ```bash
  ./manage_versions.sh add 1_15_0
  ```
* **Process:**
  * Looks for `patches/update_script_v1_15_0.py`.
  * Executes the script using `python3` (which must write the updated files to the root directory).
  * Automatically runs the `diff` pipeline to generate the newest patch and clean up intermediate source files.

### 5. `version`
Outputs the script's current version identifier.
```bash
./manage_versions.sh version
```

## How the Magic Works

### Incremental Patch Generation
Unified diffs provide a highly human-readable way to observe line-by-line evolutions. Rather than saving duplicates of massive files, the `diff` command registers only the differences:

$$ \text{File}_{B} = \text{File}_{A} + \text{Diff}_{A \to B} $$

This results in an incredibly lightweight directory.

### Smart Bidirectional Reconstitution
Older version control designs required walking the entire commit history from the beginning. This script introduces a **bidirectional relative distance algorithm**:
1. It locates the nearest version file physically present in your working environment (the "Anchor Base").
2. It assesses whether the desired version is older or newer than this anchor.
3. It performs either forward patching (`patch`) or reverse patching (`patch -R`) directly inside the sandboxed `./restored/` directory:

$$ \text{Target} < \text{Anchor} \implies \text{Anchor} - \text{Diff}_{T \to A} = \text{Target} $$
$$ \text{Target} > \text{Anchor} \implies \text{Anchor} + \text{Diff}_{A \to T} = \text{Target} $$

### Safety-First Cleanup
When cleaning up `./restored`, the script executes `check_recoverable`. This algorithm temporarily maps the reconstruction path. If a developer accidentally deleted a `.diff` file, the script flags that version as "unrecoverable" and blocks the cleanup command from purging the local restored file.

## Step-by-Step Workflow Example
Suppose you want to manage the versions of a project called `my_app`.

### 1. Set up your Project environment
```bash
export PROJECT_NAME="my_app"
```

### 2. Check current version of the manager
```bash
./manage_versions.sh version
# Output: my_app Manager Script v1.7.0
```

### 3. Generate patches and clean up workspace
If you have `my_app_v1_0_0.html` and `my_app_v1_1_0.html` in your directory, compress them to a patch:
```bash
./manage_versions.sh diff
# Output:
# Creating patch: v1_0_0 -> v1_1_0
# Files for 1_0_0 cleaned up.
# Patches created. Latest version: v1_1_0
```
Your workspace now contains only `my_app_v1_1_0.html` and the patch folder!

### 4. Create and add a new version
Write an update script `patches/update_script_v1_2_0.py` that modifies `my_app_v1_1_0.html` and outputs `my_app_v1_2_0.html`. Then run:
```bash
./manage_versions.sh add 1_2_0
# Output:
# [Runs python script, generates my_app_v1_2_0.html]
# Creating patch: v1_1_0 -> v1_2_0
# Files for 1_1_0 cleaned up.
```

### 5. Restore an old version for testing
Need to inspect `v1_0_0` again?
```bash
./manage_versions.sh restore
# Output:
# Select a version to restore:
# 1) 1_0_0
# 2) 1_1_0
# 3) 1_2_0
# #? 1
# Creating restoration directory: ./restored
# Restoring v1_0_0 to ./restored using existing base v1_2_0...
# Applying reverse patch: 1_2_0 -> 1_1_0
# Applying reverse patch: 1_1_0 -> 1_0_0
# Successfully restored v1_0_0 to ./restored/my_app_v1_0_0.html
```

### 6. Clean up your restored sandbox
```bash
./manage_versions.sh clean
# Output:
# Scanning ./restored for restored versions...
# Version v1_0_0 is fully recoverable. Deleting ./restored/my_app_v1_0_0.html...
# Removing empty directory ./restored
```
Your workspace is clean, safe, and optimally organized!