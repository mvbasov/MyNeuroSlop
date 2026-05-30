Create a standalone web tool to prepare HTML code to be embedded into other HTML or Markdown documents. 

CRITICAL ARCHITECTURE REQUIREMENT: 
The output MUST be a single, self-contained HTML file. It must have ZERO external web requests or dependencies (no Tailwind CDN, no external fonts, no external JS). Write all styling using custom CSS in a <style> block, utilizing CSS variables, flexbox/grid, and modern UI principles (slate/blue palette, soft shadows, custom scrollbars). Use inline SVGs for all icons.

UI & Layout Requirements:
1. Two-column responsive layout (stacked on mobile, side-by-side on desktop).
2. Left Column - Options Card: Checkboxes for "Remove structural tags" and "Remove empty lines".
3. Left Column - Input Card: 
   - Header contains "Input Source", a dynamic live size counter (formatted in B or KB), a "Load File" button (accepts .html, .htm, .txt, .md), and a "Clear" button.
   - Textarea supports direct typing, pasting, AND Drag & Drop files (highlight textarea border on dragover).
4. Right Column - Output Card:
   - Header contains "Prepared Output", a dynamic live size counter (formatted in B or KB), a "Copy" button (with robust document.execCommand fallback), and a "Save" button (triggers file download).
5. Footer: Add a simple, centered footer text reading "mvb HTML Embed Preparer v1.2.0".
6. Notifications: Use a custom Toast notification system at the bottom right for success/error messages.

Real-time Processing: The output and both size counters must update automatically whenever the input changes, a file is loaded/dropped, or options are toggled.

Advanced Processing Engine Logic (MUST happen in this exact order to prevent bugs):
1. Normalization: Replace `\r\n` with `\n` to prevent cross-OS spacing issues.
2. Protection Phase: Find all <script> and <style> blocks. Temporarily encode the `<` and `>` characters inside them so the subsequent HTML regex matchers don't accidentally mangle internal JavaScript logic (like `if (a < b)`). Do NOT protect empty lines here; they should be cleaned up globally later.
3. Structural Tag Removal & Smart Indent (If "Remove structural tags" is checked): 
   - Remove DOCTYPE and <meta> tags globally.
   - For `<html>`, `<head>`, and `<body>` tags: Calculate the exact leading whitespace of the opening tag. Remove that exact amount of whitespace from every line inside that tag's block so the internal code stays perfectly aligned.
4. Empty Line Removal (If "Remove empty lines" is checked): Strip completely empty or whitespace-only lines globally.
5. Markdown Title Conversion: Detect the `<title>...</title>` tag. Remove the tags and convert its text content into a top-level Markdown header (e.g., `# My Page Title`) at the top of the output.
6. Unprotect Phase: Decode the temporarily protected `<` and `>` characters back to normal inside the <script> and <style> blocks. (This MUST happen before step 7).
7. Global Indent Cleanup: As the very last step, scan the entire output to find the smallest common indentation across all non-empty lines. Remove that exact amount from every non-empty line so the final code block sits perfectly flush left. Update the output textarea and output size counter.