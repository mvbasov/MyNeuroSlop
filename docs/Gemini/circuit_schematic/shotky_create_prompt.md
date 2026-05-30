Act as an expert SVG designer and front-end developer building a mathematically precise, vector-based circuit schematic library. 

I need you to create a new SVG definition for the following electronic component: Schottky diode.

You must strictly adhere to the following design rules to ensure perfect compatibility with my existing library:

1. **Format & Definition:**
   - Define the component using `<symbol id="[component-id]" viewBox="0 0 X X">`.
   - Do NOT use nested `<svg>` tags.

2. **Grid & Snapping Mathematics (CRITICAL):**
   - The standard `viewBox` is `0 0 100 100`. (Expand to `0 0 200 200` only if the component requires greater vertical/horizontal pin separation, such as an SPDT switch, Op-Amp, or Logic Gate).
   - ALL external connection pins MUST land exactly on boundary coordinates that are strict multiples of 50.
   - **For inline/2-pin components** (Resistors, Capacitors, Diodes, SPST Switches): The pins must start exactly on the left boundary at `(0, 50)` and end on the right boundary at `(100, 50)`.
   - **For standard 3-pin semiconductors** (Transistors, MOSFETs): The Base/Gate must be at `(0, 50)`, the Collector/Drain at `(50, 0)`, and the Emitter/Source at `(50, 100)`.
   - **For multi-throw switches or logic/analog ICs** (SPDT, Op-Amps, Flip-Flops): Map common/input poles to the left boundary (`x=0`) and outputs/throws to the right boundary (`x=100` or `x=200`). Space the vertical pins out strictly in 50-unit increments (e.g., `y=50`, `y=100`, `y=150`) to ensure perfect vertical grid snapping.

3. **Global Styling Wrapper:**
   - All internal lines and shapes must be wrapped in a single styling group:
     `<g stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">`
   - NEVER use hardcoded colors (like `#000` or `black`). Always rely on `currentColor` so the component inherits the parent CSS.

4. **Filled Shapes (Arrows, Diodes, Indicators):**
   - If the component requires solid arrows or filled regions (like diode triangles or N/P channel arrows), override the group fill using:
     `fill="currentColor" stroke-width="1.5" stroke-linejoin="miter"`
   - Ensure arrows do not awkwardly intersect or overlap with intersecting lines (leave clean visual gaps where appropriate).

5. **Text & Labels (If required inside the symbol):**
   - Use `<text font-family="monospace" font-size="..." font-weight="bold" fill="currentColor" stroke="none">`.

Please output ONLY the raw `<symbol>` code block so I can paste it directly into my library's `<defs>` section.
