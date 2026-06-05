# SVG Component Editor v7.8.0

## Official End-User Manual

Welcome to the **SVG Component Editor v7.8.0**. This tool is a highly advanced, standalone environment for creating, manipulating, and exporting SVG graphics. It is designed to work completely offline, runs seamlessly in your browser, and features powerful mathematical engines to keep your SVG code clean and optimized.

### 1. Getting Started

The SVG Component Editor is a zero-dependency web application.

* **Offline Ready:** Simply save the `.html` file to your computer and double-click it to open it in any modern web browser. No internet connection is required.

* **Embeddable:** The tool is scoped safely within its own container, meaning it can be embedded into other web tools or dashboards without conflicting with existing styles or scripts.

### 2. Interface Overview

The interface is split into two primary panes:

* **The Code Editor (Right):** A live text area where you can write raw SVG code.

* **The Visual Canvas (Left):** A real-time, interactive preview of your graphic.

Whenever you type in the Code Editor, the Visual Canvas updates instantly. More importantly, whenever you interact with elements on the Visual Canvas, the exact changes are mathematically calculated and injected perfectly back into your Code Editor!

### 3. Basic Editing & Selection

1. **Selecting Elements:** Click anywhere inside a tag in the Code Editor, or click on a visual shape in the Canvas. The active element will be highlighted.

2. **Inserting Shapes:** Use the `Insert` dropdown in the toolbar to quickly inject standard SVG tags (e.g., `<rect>`, `<circle>`, `<path>`, `<text>`, `<use>`) or even Comment blocks directly into your code at the cursor's location.

3. **Nudging/Moving:** With an element selected, use the directional arrow buttons in the toolbar (or your keyboard arrows if enabled) to safely move the shape around the grid. You can control exactly how far the shape moves per click by adjusting the **Step Size** input located at the bottom of the interface.

4. **Deleting Elements:** To remove an element, select it and click the red Delete (🗑️) button in the toolbar to completely and safely erase the active tag from your code.

### 4. Advanced Geometric Manipulation

Unlike standard editors that pile on messy `transform` attributes, v7.8.0 features a powerful mathematical engine that modifies the raw coordinates whenever possible.

* **Rotation:** Use the rotation dropdown to rotate the selected element by **90°, -90°, 45°, or -45°**. Additionally, you can intuitively adjust the rotation angle of a shape by selecting its `rotate()` attribute and using your **arrow keys** to increment or decrement the angle in real-time.

  * *Smart Fallbacks:* For paths and polygons, the editor uses a sine/cosine matrix to recalculate the actual point coordinates. If a basic shape (like a `<rect>`) is rotated by a non-right angle (like 45°), it safely falls back to applying a clean `transform` attribute.

* **Mirroring / Flipping:** Use the Horizontal and Vertical flip buttons. The editor recalculates coordinates to perfectly mirror the graphic across its center axis.

* **Smart `<use>` Support:** The editor automatically tracks down the original symbol a `<use>` tag references to ensure it rotates and flips around its *true* visual center.

* **Matrix Squashing:** If your code contains messy, duplicated transformations (e.g., `translate(50, 50) rotate(90) translate(-10, -10)`), the editor automatically squashes them into a single, clean Affine Matrix or simple translation!

### 5. Comment Management (New in v7.8.0)

Managing multi-line HTML/SVG comments (`<!-- ... -->`) is now fully supported as an interactive geometric block.

1. **Highlighting:** Click anywhere inside a comment block in the code. The editor will parse the entire block, even if it spans multiple lines.

2. **Delete Block (🗑️):** Click the red Delete button to instantly erase the entire comment block.

3. **Uncomment Block (🔓):** Click the new Unlock icon to reactivate commented code.

   * **Ghost Line Eradication:** If your `<!--` and `-->` markers are on their own empty lines, the uncomment tool will completely eradicate those empty "ghost lines", leaving your layout formatting perfectly intact and clean!

### 6. File Management & Export

The top toolbar provides robust tools for getting your code in and out of the editor:

* **Load File:** Click `Load` to upload an `.svg` file from your hard drive directly into the editor.

* **Save File:** Click `Save` to instantly download your current canvas as a `.svg` file.

* **Copy Data URL:** Need to embed your graphic directly into CSS or HTML as a background image? Click `Copy Data URL` to generate a safely percent-encoded `data:image/svg+xml;...` string directly to your clipboard.

### 7. UI Settings & Customization

* **Theme Toggle:** Look in the bottom footer for the Theme icon (🌗, 🌙, ☀️). Click it to cycle through **Auto** (syncs with your operating system), **Dark Mode**, and **Light Mode**.

* **On-Screen Keyboard:** Toggle the visual directional pad on or off using the keyboard icon in the footer, freeing up screen space if you prefer using native keyboard shortcuts or typing.

### 8. Diagnostics (Advanced)

If you ever suspect an issue with the application's mathematical engine, simply append `?test=run` to the URL in your browser and reload the page. The app will lock the interface and run its built-in, offline **Micro Unit Test Suite**, validating all geometric matrix calculations, comment stripping (including Test 16 for Ghost Lines), and DOM safety checks before restoring your workspace.