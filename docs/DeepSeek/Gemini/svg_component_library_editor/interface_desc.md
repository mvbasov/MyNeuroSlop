Based on the `svg_component_editor_v4_2.html` file, the interface is built using a highly responsive **CSS Grid layout** that divides the screen into four distinct blocks.

Here is a breakdown of what each block does and how they rearrange themselves based on your screen size:

### 1. The Interface Blocks

* **Header (Toolbar):** This is the command center at the top. It houses multiple logical groups:
* *Insert Menu:* A dropdown to inject new SVG tags (rect, circle, path, etc.).
* *Movement Controls:* Four arrow buttons to nudge selected elements or individual points.
* *Transform Tools:* A rotation dropdown (snapping to 45°) and a delete button.
* *File & History Controls:* Undo/Redo, file load, copy to clipboard, and save as SVG.


* **Preview Panel (Visualizer):** This panel renders the live output of your SVG code. It features a dynamically scaling checkerboard background grid with X/Y axis labels. It also hosts an invisible overlay layer (`#overlay-group`) that draws the red interactive dots and bezier handles directly over your shapes using matrix mapping.
* **Editor Panel (Code Input):** This is where you type. It relies on a clever stacking trick: a completely transparent `<textarea>` sits directly on top of a visual `div.backdrop`. When you type, the JavaScript updates the backdrop behind the text with `<mark>` tags to provide syntax highlighting and pinpoint your active selection.
* **Footer (Status Bar):** A small bar at the very bottom. It contains a toggle switch to show/hide the background grid, the application version number (`v4.2`), and a red "Syntax Error" badge that only reveals itself if you break the XML structure.

---

### 2. Large Screen Interaction (Desktop Mode)

On screens wider than 800 pixels, the application uses a **2-column layout** (`grid-template-columns: 1fr 1fr`).

* **Top & Bottom:** The **Header** spans the entire top width, and the **Footer** spans the entire bottom width.
* **Side-by-Side:** The middle of the screen is split evenly. The **Preview Panel** sits on the **left**, and the **Editor Panel** sits on the **right**.
* **Interaction:** This layout is designed for simultaneous workflows. As you type, scroll, or move your cursor in the right-hand editor, the left-hand visualizer updates instantly. The split screen ensures you never lose sight of your code or the visual result.

### 3. Mobile Screen Interaction (Max-Width 800px)

When the screen shrinks to 800px or less, a CSS Media Query triggers and completely restructures the grid into a **single-column layout**. It doesn't just squash the columns; it cleverly reorders the blocks using `grid-template-areas`:

* **1. Preview Panel (Top):** The visualizer jumps to the absolute top of the screen. This ensures the user immediately sees the visual component they are editing without having to scroll down.
* **2. Header (Middle-Top):** The toolbar is sandwiched between the preview and the code editor. This places the manipulation buttons (move, rotate, insert) directly beneath the visualizer, making it easy to tap them with a thumb while watching the shape move above.
* **3. Editor Panel (Middle-Bottom):** The code editor moves below the toolbar. This is crucial for mobile because when the user taps it, the mobile on-screen keyboard will slide up from the bottom, overlapping the editor rather than hiding the visual preview.
* **4. Footer (Bottom):** Remains at the very bottom of the document flow.
