Create a standalone web tool to prepare HTML code to be embedded into other HTML or Markdown documents. 

CRITICAL ARCHITECTURE REQUIREMENT: 
The output MUST be a single, self-contained HTML file. It must have ZERO external web requests or dependencies (no Tailwind CDN, no external fonts, no external JS). Write all styling using custom CSS in a <style> block, utilizing CSS variables, flexbox/grid, and modern UI principles. Use inline SVGs for all icons.

Features & Logic Requirements:
1. Input Methods: Provide a textarea for pasting code, a "Clear" button, and a "Load File" button (accepting .html, .htm, .txt, .md).
2. Output Methods: Provide a read-only textarea for the result. Include a "Copy" button (with robust fallback logic like document.execCommand for iframe compatibility) and a "Save" button to download the output as a file. Provide visual Toast notifications for these actions.
3. Real-time Processing: The output must update automatically whenever the input changes or options are toggled.
4. Togglable Options (Checkboxes):
    * Option A: "Remove empty lines" (filters out lines containing only whitespace).
    * Option B: "Remove structural tags" (safely removes `<html>`, `<head>`, `<body>`, `<meta>`, and `<!DOCTYPE...>` tags without deleting their inner content).
5. Smart Indentation (Runs if Option B is checked): Before removing a structural tag, calculate its exact leading whitespace. Remove that same (or less) amount of whitespace from every line inside that tag's block so the internal code stays perfectly aligned.
6. Global Indent Cleanup: After the above processing, scan the entire output to find the smallest common indentation across all non-empty lines, and remove that amount from every line so the code sits perfectly flush left.
7. Markdown Title Conversion: Detect the `<title>...</title>` tag. Remove the tags and convert its text content into a top-level Markdown header (e.g., `# My Page Title`) at the top of the output.

Design:
Make the interface responsive, splitting into a 2-column layout on desktop (Input/Options on the left, Output on the right). Use a clean, modern color palette (slate/blue) with customized scrollbars and soft shadows.
