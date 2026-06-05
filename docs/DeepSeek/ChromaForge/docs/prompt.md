Create an offline HTML+JS application that allows experimenting with color themes for an abstract web app. The page must:

1. **Run fully offline** – no external dependencies, self-contained.
2. **Be embeddable** – all content inside a `<div id="name-app">` container.
3. **Implement a dual‑theme system:**
   - **Main program theme** (controls panel) – switchable between Light, Dark, and Auto (follows system preference). Place this selector at the bottom of the left panel, compact and small.
   - **Mock application preview** (right side) – fully independent theming using color pickers (primary, secondary, background, surface, text, border) and preset themes (Default, Dark Matter, Ocean Drift, Sunset Glow, Forest Canopy). Presets and pickers affect only the preview, not the main program.
4. **Be mobile‑friendly/responsive** – layout adapts to small screens.
5. **Include a built‑in test system (Vanilla Micro Unit Test Suite) with URL‑triggered architecture:**
   - When URL contains `?test=`, the main app exposes internal functions on `window.__TEST_API__` (e.g., `applyPreviewTheme`, `applyMainTheme`, getters for DOM elements).
   - Dynamically load a separate test script named `ChromaForge_v1_2_1_tests.js` (version in filename). If URL contains `?test=run`, automatically execute `window.__runTests()`.
   - Test suite uses `assert()`, `assertTrue()`, `assertEquals()` and logs each result to the console immediately. Final summary appears in a toast notification (7 seconds persistent).
   - Test both internal logic (theme switching, presets) and DOM UI changes (button background, progress bar, stat dot, card border). Use async retry/wait for style updates to avoid race conditions.
   - Avoid any console warnings (e.g., invalid hex colors).
6. **Versioning** – Show version number (e.g., v1.2.1) in the UI. Increment minor on each change, fix reserved for user modifications, major only on explicit request.

Produce the complete HTML file (with embedded CSS and JS) and the separate test file content.