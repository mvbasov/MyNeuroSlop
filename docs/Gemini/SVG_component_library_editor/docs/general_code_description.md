Based on the logic inside `svg_component_editor_v5_1_0.html`, here is a breakdown of the code's hierarchy and a description of its functions.

### I. Overall Code Hierarchy

The application is structured as a single-file, offline-capable, and safely embeddable component. It uses three main layers:

1. **HTML Layout (Grid & Container)**
* **`<div id="svg-editor-app">`**: The master container. Everything is scoped inside this to prevent external clashes.
* **`<header>` (Toolbar)**: Contains modular groups for insertion, movement, transformation, and file operations.
* **`.preview-panel`**: The visual canvas. It holds `svg#main-svg`, which contains the dynamic grid, the user's live-rendered SVG (`#user-svg-container`), and the interactive visual overlay (`#overlay-group`).
* **`.editor-panel`**: The code editor. It layers a transparent `<textarea>` perfectly over a `#backdrop` `<div>` to achieve custom syntax highlighting without external libraries.
* **`<footer>`**: Status indicators (Syntax Error badge), grid/keyboard toggles, step size input, and version number.


2. **CSS Architecture (Embed-Safe)**
* Uses CSS variables mapped specifically to `#svg-editor-app`.
* Utilizes **Container Queries (`@container`)** instead of media queries. This ensures the layout adapts to the space *it is placed in* (for embeddability) rather than the size of the whole browser window.


3. **JavaScript Architecture (IIFE)**
* All JavaScript is wrapped inside an **Immediately Invoked Function Expression (`(function() { ... })();`)**. This prevents global scope pollution, ensuring variables like `history` or `SVGUtils` don't clash with the host page.



---

### II. JavaScript Objects & Namespaces (Strategy Pattern)

The core manipulation logic relies on a Strategy Pattern divided into three specific namespaces:

* **`SVGUtils`**: A library of generic string-manipulation and math utilities.
* *Features:* Regex matchers to extract attributes, coordinate formatters, and mathematical parsers to shift complex `d="..."` path commands or `points="..."` arrays.


* **`UniversalAttributes`**: The fallback handler for generic attributes.
* *Features:* Modifies `stroke-width`, `font-size`, `text-anchor`, or existing `transform` matrices (translate, rotate, scale, skew) regardless of what shape the user is editing.


* **`ShapeRegistry`**: A dictionary mapping SVG tag names (`rect`, `circle`, `path`, `polygon`, `text`, etc.) to specific handlers. Each shape defines its own geometric rules for:
* `getSubElement`: Finds the specific coordinate pair (e.g., `cx/cy` or a bezier curve control point) the cursor is currently hovering over.
* `movePoint`: Shifts just that specific point.
* `moveElement`: Shifts the entire element if no specific point is selected.
* `transformElement`: Handles complex matrix math (rotations, flips), occasionally converting shapes (e.g., `<rect>` to `<polygon>`) to support non-orthogonal rotations (like 45°).



---

### III. Core Functions Description

#### Initialization & Events

* **`initApp()`**: Bootstraps the application, loads the default SVG code, saves the initial history state, and triggers the first render.
* **`bindEvents()`**: Sets up programmatic event delegation (replacing inline `onclick` handlers). Binds UI clicks, file dragging/dropping, and `keydown` shortcuts (like `Ctrl+Z`), scoped strictly to the app container.

#### Parsing & Rendering

* **`processInput(forceUpdate)`**: The main rendering loop. Parses the raw text into a DOM object using `DOMParser`. If valid, it updates the visual preview and redraws the grid. If invalid, it flags the "Syntax Error" badge.
* **`getActiveTag(html, cursor)`**: **(New in v5.1.0)** A robust linear state-machine tokenizer. It reads the raw HTML character-by-character to accurately determine which `<tag>` the user's cursor is currently inside, safely handling edge cases like line breaks and nested brackets.
* **`updateGrid(code)`**: Reads the `viewBox` of the user's SVG and mathematically draws the background grid pattern and coordinate labels to scale.

#### Editor Sync & Highlighting

* **`updateSelection()`**: Called frequently via `requestAnimationFrame`. Identifies the active tag and active sub-element (the specific coordinate under the cursor). It triggers text highlighting and debounces the visual overlay rendering.
* **`updateBackdropText(code, activeSub)`**: Injects `<mark>` and `<mark class="point-mark">` tags into the background `<div>` to visually highlight the selected code and specific coordinates in the text editor.
* **`renderVisualOverlay(activeNode, activeSub)`**: Calculates Screen CTM (Coordinate Transformation Matrix) to draw red/blue helper dots and dashed lines over the preview canvas, mapping exactly to the SVG node the user is editing.

#### User Tools (Actions)

* **`moveShape(dirX, dirY)`**: Takes arrow-key input and passes it sequentially through the Strategy Pattern (`ShapeRegistry.movePoint` → `UniversalAttributes.movePoint` → `ShapeRegistry.moveElement`) to nudge coordinates mathematically inside the raw string.
* **`transformShape(action)`**: Handles rotations (`rot_90`, `rot_45`, etc.) and flips (`flip_h`, `flip_v`). Calculates the center of the bounding box and applies sine/cosine matrix recalculations to individual coordinates.
* **`insertShape(type)`**: Injects template SVG strings (like `<circle>`, `<path>`) into the editor at the cursor's location, matching the current line indentation.
* **`deleteActiveShape()`**: Slices the currently active tag out of the raw text string.

#### History & I/O

* **`saveHistory(code)` / `undo()` / `redo()**`: Manages a bounded array (`MAX_HISTORY = 50`) to save states for undo/redo functionality, capping at 50 to prevent memory bloat on large files.
* **`downloadSVG()` / `copyToClipboard()` / `loadFromFile(event)**`: Utility functions to export the editor's content as an `.svg` file, copy it to the clipboard, or import an existing file.
