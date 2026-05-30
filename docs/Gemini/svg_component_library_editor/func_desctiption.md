Here is a detailed breakdown of the functions in your `svg_component_editor_v4_2.html` application, categorized by what they do and their role in the architecture.

### 1. Core State & Editor Mechanics

These functions handle the fundamental operations of the editor, including history (undo/redo), syncing text with the visual preview, and updating the code.

* **`processInput(forceUpdate)`**: The main engine of the editor. It grabs the text from the `<textarea>`, checks it for syntax errors using `DOMParser`, updates the live SVG preview container (`userSvgContainer.innerHTML`), hides/shows the error badge, calls the grid updater, and schedules the syntax highlighter/selection tracker.
* **`updateCode(newCode, save)`**: A helper function used whenever a tool (like moving, inserting, or loading a file) changes the code programmatically. It sets the new value, runs `processInput()`, and optionally pushes the change to the undo history.
* **`saveHistory(code)`**, **`applyState()`**, **`undo()`**, **`redo()`**: This cluster manages the Undo/Redo stack. `saveHistory` truncates any "future" history and pushes a new state. `applyState` restores the text and cursor scroll positions. `undo`/`redo` trigger the navigation through this stack array.

### 2. Parsers & UI Synchronizers

These functions magically sync the raw text inside the `<textarea>` to the physical SVG elements displayed on the screen without using a heavy external library like CodeMirror.

* **`getActiveTag(html, cursor)`**: A lightweight, custom regex-based HTML/XML parser. It scans the entire code to figure out exactly which tag the user's cursor is currently resting inside. It builds a mini DOM-tree mapping to link the text snippet to the actual active index on the screen.
* **`escapeHTML(str)`**: A simple utility to sanitize text (converting `<` to `&lt;`, etc.) before injecting it into the visible highlight backdrop, preventing XSS and layout breakage.
* **`updateSelection()`**: The visual coordinator, triggered on every click, keyup, or scroll. It performs three huge tasks:
1. Highlights the exact tag/point in the text editor backdrop using `<mark>` tags.
2. Puts a blue highlight stroke on the active SVG element in the visualizer.
3. Uses `getScreenCTM()` matrix math to pinpoint exactly where the cursor's current sub-element (like an `x` coordinate or a path bezier handle) is on the physical screen, and draws the interactive red dots/dashed lines over it.


* **`getActiveSubElement(tagStr, relPos, tagName, activeNode)`**: A router function. It looks at the cursor position and delegates to `UniversalAttributes` or `ShapeRegistry` to figure out *exactly* what the user is selecting (e.g., "Are they selecting the whole `<rect>`, or just the `width` attribute?").

### 3. Toolbar Actions (Manipulation)

These functions are directly tied to the toolbar buttons and keyboard shortcuts.

* **`moveShape(dx, dy)`**: The master coordinator for the arrow keys. It uses the Strategy Pattern to figure out what shape you are editing, asks the `ShapeRegistry` to modify the code string by shifting coordinates by `dx` and `dy`, and smoothly updates the code while preserving cursor position.
* **`rotateShape(angle)`**: Triggered by the rotate dropdown. It calculates the geometric center of the selected shape's bounding box (`cx`, `cy`), creates a mathematical point-rotation function (`rotPoint`), and passes it to the `ShapeRegistry` to rewrite the string data for that shape.
* **`insertShape(type)`**: Triggers when using the "Add Element" dropdown. Looks up a template (like a `<circle>` or `<rect>`), safely injects it at the cursor position, and auto-indents it to match surrounding code.
* **`deleteActiveShape()`**: Deletes the entirety of the currently selected XML tag from the code editor and restores the cursor.
* **`updateGrid(code)`**: Reads the `viewBox` attribute of the user's root SVG. It mathematically recalculates the background checkerboard pattern and dynamically draws X/Y axis labels so the grid flawlessly matches the scale of the user's component.

### 4. Component Strategy Pattern (`ShapeRegistry` & `UniversalAttributes`)

This is the architectural core we refactored. Instead of one giant function, rules for different elements are isolated into objects.

* **`UniversalAttributes`**: Handles logic for attributes that can exist on *any* element (like `transform="translate(...)"`, `stroke-width`, `font-size`, and `text-anchor`). It knows how to parse them and how to increment/decrement their values.
* **`ShapeRegistry`**: A dictionary containing handlers for `rect`, `circle`, `line`, `polygon`, `path`, and `text`. Every handler contains:
* **`getSubElement`**: Logic to detect if the cursor is resting on a specific point/property (e.g., detecting if the cursor is on the `ry` attribute of a `<rect>`).
* **`movePoint`**: Logic to rewrite the SVG string when a specific point is nudged by arrow keys.
* **`moveElement`**: Fallback logic to shift the entire element if no specific point is selected.
* **`rotateElement`**: Logic specific to that shape's geometry to mathematically process a rotation (e.g., swapping `width` and `height` for a 90-degree rectangle rotation, or doing matrix math on the `d` attribute of a path).



### 5. String/Math Utilities (`SVGUtils`)

A collection of pure, reusable "helper" functions that perform regex text replacements.

* **`getAttrMatch`**, **`adjustAttr`**, **`setOrReplaceAttr`**, **`checkAndAdjustNearAttr`**: Tools to safely search for an SVG attribute (like `x="10"`) inside a string and do math on the number without breaking surrounding text.
* **`adjustPoints`**, **`formatPointsData`**: Tools for manipulating the space/comma-separated strings found in `<polygon>` or `<polyline>`.
* **`formatPathData`**, **`shiftPathD`**, **`shiftSinglePathCommand`**: Highly specialized regex tools that tear apart complex SVG `<path>` data strings, correctly interpret relative (`m`, `l`, `c`) vs absolute (`M`, `L`, `C`) commands, apply coordinate math, and perfectly rebuild the string with strict, clean spacing.

### 6. Export & File I/O

* **`downloadSVG()`**: Looks at the user's code, intelligently wraps it in standard `xmlns` and `<svg>` tags (or unwraps `<symbol>` tags) to create a valid, standalone file, and triggers a `.svg` browser download.
* **`copyToClipboard()`**: Executes the `document.execCommand('copy')` API to quickly load the raw code to the clipboard, providing visual "✅" feedback on the button.
* **`loadFromFile(event)`**: Uses the native HTML5 `FileReader` API to parse text or SVG files uploaded via the file input or drag-and-drop into the editor window.
