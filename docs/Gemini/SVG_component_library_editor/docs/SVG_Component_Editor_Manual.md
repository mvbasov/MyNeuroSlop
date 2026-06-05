# SVG Component Editor User Manual

## Overview

The SVG Component Editor is a robust, offline-capable, and fully embeddable tool designed for creating, editing, and mathematically manipulating scalable vector graphics directly in your browser.

Operating entirely on the client side, the application features an immersive dual-pane interface: a live visual preview canvas and an intelligent, synchronized raw-text editor. It utilizes a custom linear state-machine tokenizer to parse code safely and provides a suite of geometric transformation tools that manipulate SVG coordinates with mathematical precision.

## Interface and Layout

The application is structured into four primary regions within a responsive grid layout.

### 1. The Toolbar (Header)

The toolbar at the top provides all primary interaction controls, grouped logically:

* **Insert Tool (`➕`):** A dropdown menu used to rapidly inject standard SVG templates (`<circle>`, `<line>`, `<path>`, `<polygon>`, `<rect>`, `<text>`) into your code.

* **Directional Controls (`▲`, `▼`, `◀`, `▶`):** Nudge the actively selected shape or coordinate point by a specific distance (defined in the footer's "Step" input).

* **Transform Tool (`↻`):** A dropdown menu used to apply complex geometric transformations (e.g., ±45° rotation, ±90° rotation, 180° rotation, Horizontal/Vertical Mirroring).

* **Delete (`🗑️`):** Removes the currently active shape from the code.

* **Undo (`↶`) / Redo (`↷`):** Step backward or forward through the editor's history states.

* **Load File (`📂`):** Opens a system dialog to import an `.svg`, `.xml`, `.html`, or `.txt` file into the editor.

* **Copy (`📋`):** Copies the raw code in the editor to your system clipboard.

* **Save (`💾`):** Downloads the current workspace as a standard `.svg` file.

### 2. The Preview Panel (Left Pane)

This panel provides a real-time visual representation of the SVG code.

* **Background Grid:** A mathematical coordinate grid overlay (toggleable in the footer) that scales automatically to your SVG's `viewBox`.

* **Live Rendering:** Displays the active SVG graphic exactly as it would appear in a browser.

* **Visual Overlay:** When you place your text cursor inside an SVG tag in the editor, this overlay projects red and blue helper indicators directly onto the preview canvas, pinpointing the specific shape or geometric coordinate you are actively editing.

### 3. The Editor Panel (Right Pane)

The raw-code editing environment.

* **Syntax & Selection Highlighting:** Instead of relying on heavy third-party libraries, the editor uses a layered `div`/`textarea` approach to provide instant visual feedback. The `<tag>` your cursor is currently inside is highlighted in blue. If your cursor rests near a specific coordinate (like `cx="50"` or a bezier curve point in a `path d="..."`), that specific coordinate is highlighted in red.

* **Drag-and-Drop:** You can drag and drop an `.svg` file directly into this panel to instantly load its code.

### 4. The Status Bar (Footer)

* **Error Badge:** Displays a red "Syntax Error" warning if the code is malformed and cannot be parsed.

* **Grid Toggle:** Turns the mathematical background grid in the preview panel on or off.

* **Keyboard Toggle (`⌨️`):** Disables the virtual keyboard from popping up on mobile touchscreen devices when selecting code.

* **Step Size:** Sets the pixel multiplier (default: 1) for the directional nudge controls.

* **Version Number:** Displays the current application version.

## Core Features and Interactions

### Intelligent Coordinate Manipulation

The editor's most powerful feature is its ability to contextually target and modify geometric data within the raw text string using the Directional Controls or Keyboard Arrows.

The application uses a "Chain of Responsibility" to determine *what* to move based on where your text cursor is placed:

1. **Point-Specific Movement (Red Highlight):** If your cursor is inside a specific coordinate attribute (e.g., inside the `50` of `cx="50"` on a circle, or near the numbers of a `Q 20,20 40,40` path command), the directional controls will shift *only* that specific point mathematically.

2. **Attribute Modification:** If your cursor is inside global attributes like `stroke-width`, `font-size`, or `text-anchor`, the directional controls will increment/decrement their values.

3. **Element Movement (Blue Highlight):** If your cursor is anywhere else inside a valid tag (but not on a specific coordinate), the directional controls will shift the *entire* shape seamlessly.

### Geometric Transformations

The Transform dropdown (`↻`) applies complex matrix math to rotate or mirror shapes based on their bounding box center.

* **Coordinate Recalculation:** For elements like `<line>`, `<polygon>`, and `<path>`, the application mathematically applies a sine/cosine matrix directly to the underlying coordinates in the raw text string (e.g., altering a `points` array or a `d` string).

* **Shape Conversion Fallbacks:** If you rotate an axis-aligned `<rect>` or `<ellipse>` by a non-orthogonal angle (such as 45°), the app will dynamically convert the tag into a `<polygon>` or a cubic-bezier `<path>` to recalculate the coordinates properly without relying on CSS transforms.

* **Transform Attributes:** For tags where direct coordinate manipulation is natively unsupported (like `<text>` or `<use>`), the app will inject or update an SVG `transform="rotate(...)"` attribute.

### Embeddability and Technical Architecture

* **Offline Standalone:** The application is contained entirely within a single HTML file with no external CSS or JS dependencies. It operates fully offline.

* **Namespace Scoping:** All styles are isolated using CSS Container Queries and variables scoped exclusively to the `#svg-editor-app` wrapper.

* **JavaScript Isolation:** All logic is wrapped in an Immediately Invoked Function Expression (IIFE), and all event listeners are bound programmatically to ensure the tool cannot pollute the `window` object or clash with scripts if embedded inside a larger host page.

## Keyboard Shortcuts

The following keyboard shortcuts are supported while the application is actively focused:

* **`ArrowUp`, `ArrowDown`, `ArrowLeft`, `ArrowRight`:** Navigates the text cursor. The visual overlay and highlighting sync instantly.

* **`Ctrl` + `Z`** (or `Cmd` + `Z` on Mac): Undo the previous edit.

* **`Ctrl` + `Y`** (or `Cmd` + `Shift` + `Z` on Mac): Redo the previous edit.