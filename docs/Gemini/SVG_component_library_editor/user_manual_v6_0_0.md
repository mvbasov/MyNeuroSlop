# SVG Component Editor User Manual

**Version 6.0.0**

Welcome to the SVG Component Editor! This standalone, embedded-safe environment allows you to visually design, edit, and fine-tune SVG code directly in your browser.

This manual will guide you through the interface, tools, and keyboard shortcuts to help you build and manipulate SVG components effectively.

## 1. Getting Started

### 1.1 The Interface

The editor is divided into a dual-panel layout:

* **Left Panel (Preview Canvas):** This displays your live-rendered SVG. It features a background grid scaled to your document's `viewBox`, helping you align components precisely.

* **Right Panel (Code Editor):** This is where you write or paste your raw SVG HTML/XML. As you type, the left panel updates instantly.

### 1.2 Loading and Saving Files

* **📂 Load File:** Click the folder icon in the top right to open an existing `.svg`, `.txt`, `.html`, or `.xml` file from your computer. The contents will be loaded into the code editor.

* **💾 Save SVG:** Click the floppy disk icon to download your current design as a clean, ready-to-use `.svg` file. The tool automatically handles wrapping `` definitions if needed.

* **📋 Copy Code:** Click the clipboard icon to instantly copy the raw SVG string from the code editor to your computer's clipboard.

## 2. Navigating and Editing

### 2.1 Live Coordinate Selection (The Red Dot)

The defining feature of this editor is the **Live Coordinate Helper**.

As you click around or move your cursor inside the text in the Code Editor, the application parses the code to determine what you are actively editing.

* If your cursor is near a specific coordinate (like `x="10"` or a specific `50,50` point in a path's `d="..."` string), a **red dot** will appear on the canvas marking exactly where that point exists in visual space.

* If you click at the beginning of a complex tag (like ``), the red dot will snap to the mathematical geometric center of that element, showing you the pivot axis for any future rotations or flips.

* Selected text values will be highlighted with a blue or red background in the code editor to confirm your selection.

### 2.2 Adding Shapes

To quickly insert basic shapes, use the **➕ Dropdown** in the top left toolbar:

1. Click the `➕` dropdown.

2. Select a primitive (Circle, Line, Path, Polygon, Polyline, Rectangle, Text).

3. The shape's baseline code will be instantly injected into the editor exactly where your text cursor is currently placed.

### 2.3 Deleting Shapes

To delete a shape:

1. Click anywhere inside the tag you wish to delete in the Code Editor (e.g., inside ``).

2. Click the **🗑️ Delete** button (the trashcan icon) in the toolbar. The entire tag will be cleanly removed.

## 3. Manipulating Shapes

### 3.1 Nudging and Shifting

You can mathematically shift the coordinates of the selected shape or point without typing new numbers.

1. Click inside the text editor near the coordinate or tag you want to move. Ensure the red dot highlights the correct element.

2. Use the **Arrow Keys (▲, ▼, ◀, ▶)** in the top toolbar to nudge the point up, down, left, or right.

3. **Keyboard Shortcut:** You can also use the Arrow Keys on your physical keyboard to nudge elements instantly.

*Tip: You can change how far elements move with each click by adjusting the **Step:** input box in the bottom footer.*

### 3.2 Rotations and Flips

The editor handles complex rotations and mirroring dynamically.

1. Click inside the tag you want to transform (ensure the red dot is positioned at its center).

2. Open the **↻ Transform Dropdown**.

3. Select your desired action:

   * **↻ 90°, ↺ -90°, ↻ 180°:** Standard orthogonal rotations.

   * **↻ 45°, ↺ -45°:** Irregular angle rotations.

   * **↔ Flip H, ↕ Flip V:** Horizontal and vertical mirroring.

*Note: For primitive shapes like ``, the editor will seamlessly recalculate the raw `x`, `y`, `width`, and `height` properties when possible. For irregular angles (like 45°), it may automatically convert the shape into a `` or `` to accurately map the new angles in raw code. For `` and ``, the editor uses a robust `matrix()` squashing engine to keep your `transform="..."` strings clean and consolidated.*

## 4. Helpful Features

### 4.1 Undo and Redo

The editor tracks your last 50 actions to prevent data loss.

* **↶ Undo:** Reverts your last change. (Keyboard: `Ctrl+Z` or `Cmd+Z`)

* **↷ Redo:** Restores a reverted change. (Keyboard: `Ctrl+Y`, `Cmd+Y`, or `Shift+Cmd+Z`)

### 4.2 Toggles and Settings (Footer)

* **Grid Toggle:** Use the `[ ] Grid` checkbox in the bottom left to show or hide the alignment grid overlay on the preview canvas.

* **Keyboard Toggle (⌨️):** If you are using a mobile device and the virtual keyboard keeps popping up when you just want to use the toolbar buttons, click the keyboard icon. This locks the text area to prevent the virtual keyboard from opening. Click it again to unlock.

Enjoy building with the SVG Component Editor!