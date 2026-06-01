For v5.1.0

I can certainly explain the relationship between these two functions based on the code in the Canvas!

The relationship between `movePoint` inside `UniversalAttributes` and `movePoint` inside `ShapeRegistry` is based on the **Chain of Responsibility** (or fallback) design pattern. They work together sequentially to determine exactly what part of an SVG element the user is trying to move using their keyboard.

Here is how they interact, specifically orchestrated inside the `moveShape` function:

1. **`ShapeRegistry`'s `movePoint` (The First Priority):** When you press an arrow key, the application first checks the `ShapeRegistry` for the specific shape you are hovering over (like `polygon`, `rect`, or `path`). Its `movePoint` function looks for **shape-specific coordinates** near your cursor (like the `x`/`y` of a `<rect>`, the `cx`/`cy` of a `<circle>`, or individual path nodes inside a `d="..."` string).
* *If your cursor is near one of these coordinates, it moves it and returns `modified: true`.*


2. **`UniversalAttributes`'s `movePoint` (The Fallback):**
If the `ShapeRegistry` fails to find a shape-specific point to move (meaning it returns `modified: false`), the application hands the string over to `UniversalAttributes.movePoint`. This function looks for **global attributes** that can apply to *any* SVG shape—such as `stroke-width`, `font-size`, `text-anchor`, or a generic `transform="translate(x, y)"` command.

**In Summary:**
`ShapeRegistry` acts as the specialist, handling the unique geometry points of specific tags. `UniversalAttributes` acts as the generalist, catching and modifying global styling or transform attributes if the specialist didn't find anything to move. (And if *both* fail, the app falls back to moving the entire element at once via `moveElement`).
