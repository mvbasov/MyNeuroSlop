Here is a comprehensive initial prompt you can use (or feed to another AI) to perfectly recreate this application from scratch.

---

**System prompt / Instructions:**
"I want you to build a single-file offline SVG Component Editor designed specifically for electronic schematics. The application must be contained entirely within a single `index.html` file, including all HTML, CSS, and Javascript. Do not use external CDNs for styles (like Tailwind); instead, embed the necessary CSS utility classes directly in a `<style>` block to ensure it works completely offline.

The application should have a clean, modern, and mobile-responsive layout split into two main sections:

1. **Visual Preview Panel (Left/Top):** A container that renders the user's SVG code in real-time.
2. **Source Code Editor (Right/Bottom):** A raw text editor `<textarea>` where the user writes their SVG code.

**Key Features Required:**

* **Real-time Rendering:** As the user types in the textarea, the preview should update immediately. If there is a parsing error, fail silently by retaining the last valid render, but display a small 'Syntax Error' badge in the header.
* **Engineering Grid:** Implement a mathematical, scalable background grid in the preview area. The grid should calculate its step size dynamically by taking the user's SVG `viewBox` width and dividing it by 10. Draw the grid lines using an SVG `<pattern>`.
* **Grid Coordinates:** When the grid is toggled on, generate numeric coordinate labels along the top (X-axis) and left (Y-axis) edges of the grid. Only display the first, last, and every second interval (e.g., 0, 20, 40, 60, 80, 100). Ensure the `viewBox` of the preview wrapper dynamically expands to fit these numbers so they aren't cropped.
* **Cursor Highlighting (Optional Toggle):** If enabled via a checkbox, the editor must track where the user's text cursor is located within the `<textarea>`. It must identify the specific SVG element the cursor is currently inside, and simultaneously highlight that specific element in the visual preview (e.g., turning its stroke blue) AND highlight the corresponding code text in the editor (using a synchronized transparent backdrop overlay with `<mark>` tags behind the textarea).
* **Move Tools:** Provide 'Move' buttons (Up, Down, Left, Right). When clicked, these should programmatically parse the SVG element under the user's text cursor and modify its native coordinate attributes (e.g., updating `cx`/`cy` for circles, `x`/`y` for rects, recalculating `points` for polygons, and recalculating absolute/relative commands in the `d` attribute for paths) to shift the element by 1 unit. Do not use `transform="translate()"`.
* **Insert & Delete Tools:** Provide buttons to inject new primitive shapes (`circle`, `line`, `path`, `polygon`) at the cursor's current location, and a Delete button that cleanly removes the entire SVG element the cursor is currently resting on (including cleaning up whitespace).
* **History Stack:** Implement a custom Undo/Redo system that tracks changes, debounces typing events, and explicitly saves state before/after using any tool buttons. Bind this to standard `Ctrl+Z` / `Ctrl+Y` keyboard shortcuts.
* **Component Focus:** The editor should be optimized to work with SVG `<symbol>` fragments (e.g., `<symbol id="resistor" viewBox="0 0 100 100">...</symbol>`). If the user provides a `<symbol>`, wrap it in an outer SVG and `<use>` it over the grid for previewing.
* **Default State:** Pre-load the editor with a sample NPN transistor `<symbol>` fragment to demonstrate functionality. Include a 'Save Fragment' button that downloads the raw textarea content as an `.svg` file. Grid and Highlighting enabled by default.
* **Default Code to Inject**
```
<!-- NPN Transistor -->
<symbol id="npn" viewBox="0 0 100 100">
  <g stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="50" cy="50" r="42" stroke-width="2" />
    <line x1="0" y1="50" x2="35" y2="50" />
    <line x1="35" y1="28" x2="35" y2="72" stroke-width="4.5" />
    <path d="M 35 40 L 60 20 L 60 0" />
    <path d="M 35 60 L 60 80 L 60 100" />
    <polygon points="58,78 46,76 54,67" fill="currentColor" stroke-width="1.5" stroke-linejoin="miter"/>
  </g>
</symbol>
```

