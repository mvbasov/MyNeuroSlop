### The Inline SVG Favicon Prompt

**Task:** Analyze the provided HTML/CSS/JS code to understand the core functionality and visual theme of the application.
**Instructions:**
1. **Conceptualize:** Design a simple, scalable, and highly recognizable vector icon that perfectly represents the tool's purpose.
2. **Style:** Extract the primary accent colors and theme variables directly from the provided CSS and apply them to the SVG elements so the icon matches the app's UI perfectly.
3. **Format:** Create the raw SVG code using a standard, square `viewBox` (e.g., `0 0 100 100`).
4. **Encode:** Convert the raw SVG into a URL-encoded `data:image/svg+xml` string, ensuring characters like `#` are properly escaped as `%23`.
5. **Output:** Provide *only* the final, embeddable HTML string. Do not alter or output the rest of my provided source code.

 
**Expected Output Format:**
`<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'...%3E%3C/svg%3E">`
