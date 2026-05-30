Here is a comprehensive, single prompt you can use to generate the exact final version of the Voronoi Step-by-Step Visualizer in one go. It combines your initial request with all the subsequent mathematical visualizations, normal vector graphics, and contrast adjustments.

---

**Prompt:**

Create a standalone, single-file HTML, CSS (Tailwind), and JavaScript interactive visualizer that explains how a Voronoi diagram is generated using the half-plane intersection method.

**Core Architecture:**

1. **State Recording Engine:** Instead of just drawing the final image, generate 3 random seed points within a 100x100 coordinate space and run the algorithm instantly in the background. Record every microscopic state change into an array (e.g., selecting points, calculating bisectors, checking edges, keeping vertices, finding intersections, finalizing cells).
2. **Playback System:** Create a UI to scrub through these recorded steps using "Play/Pause" (with an 800ms interval), "Next", "Previous", and a range slider.

**UI Layout (Responsive):**

* **Left Column (Visuals):** The SVG canvas (locked to a 1:1 aspect ratio, max 500px wide) followed by the playback controls and a color-coded legend.
* **Right Column (Explanation):** A dynamic title and description of what is happening in the current step, followed by a dark-themed "Live Math Calculations" terminal block.

**SVG Visualization Details:**

* **Grid:** Draw a 100x100 grid with lines every 10 units. The numerical axis labels must have high contrast: use a dark gray fill (`#1f2937`), bold font weight, and explicitly set `stroke="none"` so they are crystal clear and don't blur.
* **Geometry:** Show completed cells in pastel colors. For the active step, highlight the target point (`pA` in blue) and the comparison point (`pB` in red).
* **The Slicing Line & Vector:** Draw the perpendicular bisector line. **Crucially**, draw the normal vector `n` as a bright orange arrow originating from the midpoint and pointing directly towards `pB`. Label the arrow with an `n`.
* **Edge Checking:** When slicing the polygon, highlight the current edge being evaluated. Mark the "current" vertex and the "next" vertex clearly. Draw a green dot where an intersection occurs.

**Live Math Terminal Logic:**
During the edge-checking steps, the dark terminal must dynamically print the exact math happening behind the scenes using the variables from that exact step:

* Print the `mid` point and `normal (n)` vector coordinates.
* Show the expanded dot product formulas and the resulting signed distances for both `currDist` and `nextDist`.
* If the edge crosses the line (signs differ), explicitly show the linear interpolation math: the calculation of the exact ratio `t = currDist / (currDist - nextDist)`, followed by how `t` is used to calculate the physical `intX` and `intY` coordinates.
