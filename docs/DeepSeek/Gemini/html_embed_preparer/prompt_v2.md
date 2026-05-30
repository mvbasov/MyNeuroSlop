Create a standalone web tool to prepare HTML code to be embedded into other HTML or Markdown documents. 

CRITICAL ARCHITECTURE REQUIREMENT: 
The output MUST be a single, self-contained HTML file. It must have ZERO external web requests or dependencies (no Tailwind CDN, no external fonts, no external JS). Write all styling using custom CSS in a <style> block, utilizing CSS variables, flexbox/grid, and modern UI principles (slate/blue palette, soft shadows, custom scrollbars). Use inline SVGs for all icons.

Features & Input/Output Requirements:
1. Input Methods: Provide a textarea for pasting code, a "Clear" button, and a "Load File" button (accepting .html, .htm, .txt, .md).
2. Output Methods: Provide a read-only textarea for the result. Include a "Copy" button (with robust fallback logic using document.execCommand for iframe compatibility) and a "Save" button to download the output as a file. Provide visual Toast notifications for these actions.
3. Real-time Processing: The output must update automatically whenever the input changes or options are toggled.

Togglable Options (Checkboxes):
* Option A: "Remove empty lines" (filters out lines containing only whitespace).
* Option B: "Remove structural tags" (safely removes `<html>`, `<head>`, `<body>`, `<meta>`, and `<!DOCTYPE...>` tags without deleting their inner content).

Advanced Processing Engine Logic (MUST happen in this exact order to prevent bugs):
1. Protection Phase: Find all <script> and <style> blocks. Temporarily encode the `<` and `>` characters inside them so the subsequent HTML regex matchers don't accidentally mangle internal JavaScript logic (like `if (a < b)`).
2. Structural Tag Removal & Smart Indent (If Option B is checked): 
   - Remove DOCTYPE and <meta> tags globally.
   - For `<html>`, `<head>`, and `<body>` tags: Calculate the exact leading whitespace of the opening tag. Remove that exact amount of whitespace from every line inside that tag's block so the internal code stays perfectly aligned.
3. Empty Line Removal (If Option A is checked): Strip completely empty or whitespace-only lines.
4. Markdown Title Conversion: Detect the `<title>...</title>` tag. Remove the tags and convert its text content into a top-level Markdown header (e.g., `# My Page Title`) at the top of the output.
5. Unprotect Phase: Decode the temporarily protected `<` and `>` characters back to normal inside the <script> and <style> blocks.
6. Global Indent Cleanup: As the very last step, scan the entire output to find the smallest common indentation across all non-empty lines. Remove that exact amount from every non-empty line so the final code block sits perfectly flush left.

