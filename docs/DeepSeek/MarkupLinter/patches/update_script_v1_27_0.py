import os

def main():
    input_file = "MarkupLinter_v1_26_0.html"
    output_file = "MarkupLinter_v1_27_0.html"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found in the current directory.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Define patch mappings
    patches = []

    # 1. Update stylesheet layout for scroll synchronization, monospace fonts, pixel line-height, and matching background colors
    patches.append((
        r"""        .line-numbers {
            background: var(--app-line-number-bg);
            padding: 1rem 0.5rem 1rem 1rem;
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 13px;
            line-height: 1.5;
            text-align: right;
            color: var(--app-line-number-color);
            user-select: none;
            white-space: pre;
            overflow-y: hidden;
            border-right: 1px solid var(--app-textarea-border);
            flex-shrink: 0;
        }
        .editor-wrapper { position: relative; flex: 1; }
        .backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: var(--app-textarea-bg);
            pointer-events: none;
            z-index: 1;
            box-sizing: border-box;
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 13px;
            line-height: 1.5;
            padding: 1rem;
        }
        .highlights { white-space: pre-wrap; word-wrap: break-word; color: transparent; background-color: transparent; }
        .highlights mark { color: transparent; background-color: var(--app-highlight-bg); display: inline; background: var(--app-highlight-bg); }
        textarea {
            position: relative;
            z-index: 2;
            width: 100%;
            height: 380px;
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 13px;
            line-height: 1.5;
            background: transparent;
            border: none;
            padding: 1rem;
            resize: vertical;
            tab-size: 2;
            color: var(--app-text-primary);
            caret-color: var(--app-text-primary);
            overflow: auto;
            outline: none;
        }
        textarea:focus { outline: none; }
        .backdrop .highlights, textarea {
            white-space: pre-wrap;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
        }""",
        r"""        .line-numbers {
            background: var(--app-textarea-bg);
            padding: 1rem 0.5rem 1rem 1rem;
            font-family: 'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', Consolas, Menlo, Monaco, monospace;
            font-size: 13px;
            line-height: 20px;
            text-align: right;
            color: var(--app-line-number-color);
            user-select: none;
            white-space: pre;
            overflow-y: hidden;
            border-right: 1px solid var(--app-textarea-border);
            flex-shrink: 0;
        }
        .editor-wrapper { position: relative; flex: 1; }
        .backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: var(--app-textarea-bg);
            pointer-events: none;
            z-index: 1;
            box-sizing: border-box;
            font-family: 'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', Consolas, Menlo, Monaco, monospace;
            font-size: 13px;
            line-height: 20px;
            padding: 1rem;
        }
        .highlights {
            white-space: pre;
            word-wrap: normal;
            color: transparent !important;
            -webkit-text-fill-color: transparent !important;
            background-color: transparent;
        }
        .highlights mark {
            color: transparent !important;
            -webkit-text-fill-color: transparent !important;
            background-color: var(--app-highlight-bg);
            display: inline;
        }
        textarea {
            position: relative;
            z-index: 2;
            width: 100%;
            height: 380px;
            font-family: 'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', Consolas, Menlo, Monaco, monospace;
            font-size: 13px;
            line-height: 20px;
            background: transparent;
            border: none;
            padding: 1rem;
            resize: vertical;
            tab-size: 2;
            color: var(--app-text-primary);
            caret-color: var(--app-text-primary);
            overflow: auto;
            outline: none;
            box-sizing: border-box;
        }
        textarea:focus { outline: none; }
        .backdrop .highlights, textarea {
            white-space: pre;
            word-wrap: normal;
            word-break: normal;
            overflow-wrap: normal;
        }"""
    ))

    # 2. Add line numbers toggle button to HTML layout
    patches.append((
        r"""                <button id="themeToggleBtn" class="theme-toggle" title="Switch theme">🌓</button>
                <button id="jumpToInnerBtn" class="icon-btn" title="Jump to innermost error">🎯</button>""",
        r"""                <button id="themeToggleBtn" class="theme-toggle" title="Switch theme">🌓</button>
                <button id="toggleLineNumbersBtn" class="icon-btn" title="Toggle Line Numbers">🔢</button>
                <button id="jumpToInnerBtn" class="icon-btn" title="Jump to innermost error">🎯</button>"""
    ))

    # 3. Add global variable to track showLineNumbers with localStorage support
    patches.append((
        r"""        // ----- Global state -----
        let currentErrors = [];
        let loadedFileName = null;
        let validationTimeout = null;
        let currentHighlightedLine = null;
        let editor = null;""",
        r"""        // ----- Global state -----
        let currentErrors = [];
        let loadedFileName = null;
        let validationTimeout = null;
        let currentHighlightedLine = null;
        let showLineNumbers = true;
        
        try {
            const storedLineNumbers = localStorage.getItem('markup_validator_show_line_numbers');
            if (storedLineNumbers === 'false') {
                showLineNumbers = false;
            }
        } catch(e) {}
        
        let editor = null;"""
    ))

    # 4. Update core synchronization math inside fullSync() to match scroll widths flawlessly
    patches.append((
        r"""        function fullSync() {
            if (!backdrop || !editor) return;
            // Force backdrop height to match textarea exactly
            backdrop.style.height = editor.clientHeight + 'px';
            // Rebuild overlay to ensure marks are correctly placed
            updateOverlay();
            // Sync scroll positions
            syncScroll();
            updateLineNumbers();
        }""",
        r"""        function fullSync() {
            if (!backdrop || !editor) return;
            // Force backdrop size to match textarea's client size exactly (handles scrollbar widths flawlessly)
            backdrop.style.width = editor.clientWidth + 'px';
            backdrop.style.height = editor.clientHeight + 'px';
            // Rebuild overlay to ensure marks are correctly placed
            updateOverlay();
            // Sync scroll positions
            syncScroll();
            updateLineNumbers();
        }"""
    ))

    # 5. Add custom layout handler and visual toggler, update line numbers output format
    patches.append((
        r"""        function updateLineNumbers() {
            if (!editor || !lineNumbersDiv) return;
            const lines = editor.value.split('\n');
            let numbersHtml = '';
            for (let i = 1; i <= lines.length; i++) numbersHtml += i + '\n';
            lineNumbersDiv.innerText = numbersHtml;
        }""",
        r"""        function updateLineNumbers() {
            if (!editor || !lineNumbersDiv) return;
            const lines = editor.value.split('\n');
            let numbersHtml = '';
            for (let i = 1; i <= lines.length; i++) numbersHtml += i + '.\n';
            lineNumbersDiv.innerText = numbersHtml;
        }
        
        function applyLineNumbersVisibility() {
            if (lineNumbersDiv) {
                lineNumbersDiv.style.display = showLineNumbers ? 'block' : 'none';
            }
            const toggleBtn = document.getElementById('toggleLineNumbersBtn');
            if (toggleBtn) {
                toggleBtn.style.opacity = showLineNumbers ? '1' : '0.5';
                toggleBtn.style.borderColor = showLineNumbers ? 'var(--app-btn-border)' : 'var(--app-textarea-border)';
            }
        }

        function toggleLineNumbers() {
            showLineNumbers = !showLineNumbers;
            applyLineNumbersVisibility();
            try {
                localStorage.setItem('markup_validator_show_line_numbers', showLineNumbers ? 'true' : 'false');
            } catch(e) {}
            fullSync();
        }"""
    ))

    # 6. Apply visibility controls on initialization loop
    patches.append((
        r"""            // Event listeners
            editor.addEventListener('input', function() { scheduleValidation(); updateOverlay(); updateLineNumbers(); });
            editor.addEventListener('scroll', syncScroll);
            
            // Initial sync
            fullSync();""",
        r"""            // Event listeners
            editor.addEventListener('input', function() { scheduleValidation(); updateOverlay(); updateLineNumbers(); });
            editor.addEventListener('scroll', syncScroll);
            
            // Apply line numbers setting
            applyLineNumbersVisibility();
            
            // Initial sync
            fullSync();"""
    ))

    # 7. Bind interactive toggle button listener
    patches.append((
        r"""        function bindGlobalButtons() {
            const loadBtn = document.getElementById('loadBtn');
            const pasteBtn = document.getElementById('pasteBtn');
            const saveBtn = document.getElementById('saveBtn');
            const copyBtn = document.getElementById('copyBtn');
            const clearBtn = document.getElementById('clearBtn');
            const jumpBtn = document.getElementById('jumpToInnerBtn');
            if (loadBtn) loadBtn.addEventListener('click', loadFileModern);
            if (pasteBtn) pasteBtn.addEventListener('click', pasteFromClip);
            if (saveBtn) saveBtn.addEventListener('click', saveToFile);
            if (copyBtn) copyBtn.addEventListener('click', copyEditorText);
            if (clearBtn) clearBtn.addEventListener('click', clearAll);
            if (jumpBtn) jumpBtn.addEventListener('click', jumpToInnermostError);
            modeSelect.addEventListener('change', onModeChange);
        }""",
        r"""        function bindGlobalButtons() {
            const loadBtn = document.getElementById('loadBtn');
            const pasteBtn = document.getElementById('pasteBtn');
            const saveBtn = document.getElementById('saveBtn');
            const copyBtn = document.getElementById('copyBtn');
            const clearBtn = document.getElementById('clearBtn');
            const jumpBtn = document.getElementById('jumpToInnerBtn');
            const toggleLineNumbersBtn = document.getElementById('toggleLineNumbersBtn');
            if (loadBtn) loadBtn.addEventListener('click', loadFileModern);
            if (pasteBtn) pasteBtn.addEventListener('click', pasteFromClip);
            if (saveBtn) saveBtn.addEventListener('click', saveToFile);
            if (copyBtn) copyBtn.addEventListener('click', copyEditorText);
            if (clearBtn) clearBtn.addEventListener('click', clearAll);
            if (jumpBtn) jumpBtn.addEventListener('click', jumpToInnermostError);
            if (toggleLineNumbersBtn) toggleLineNumbersBtn.addEventListener('click', toggleLineNumbers);
            modeSelect.addEventListener('change', onModeChange);
        }"""
    ))

    # 8. Minor version increment in the footer layout
    patches.append((
        r"""    <footer>
        <span>✔ Strict XML: correct error line, full highlighting, no overlay artifacts</span>
        <span class="version">v1.26.0 · rock‑solid sync</span>
    </footer>""",
        r"""    <footer>
        <span>✔ Strict XML: correct error line, full highlighting, no overlay artifacts</span>
        <span class="version">v1.27.0 · perfect sync & design</span>
    </footer>"""
    ))

    # Apply patches sequentially
    print("Applying updates...")
    for index, (search, replace) in enumerate(patches, 1):
        if search in content:
            content = content.replace(search, replace)
            print(f" -> Patch {index} applied successfully.")
        else:
            print(f" -> Warning: Patch {index} target block not found! skipping...")

    # Write output back to disk
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Success! Updated layout saved safely as '{output_file}'.")

if __name__ == '__main__':
    main()