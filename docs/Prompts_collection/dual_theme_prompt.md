**System & Fallback Theme Prompt:**

Implement an isolated Light/Dark theme mechanism inside the `#name-app` container using CSS variables.
1. **CSS Variables**: Define custom properties for background, borders, text-main, and inputs on `#name-app` (default light) and override them under `#name-app.theme-dark`.
2. **Standalone Scoping**: Map body background variables under `body.theme-dark` and `body:not(.theme-dark)`. Apply smooth `transition: background-color 0.3s ease` to all themeable properties.
3. **JS Theme Controller**: Within an IIFE, declare a configurable constant `const APP_THEME = 'auto';` (supporting `'auto'`, `'dark'`, `'light'`). If `'auto'`, bind a change listener to the system preference `window.matchMedia('(prefers-color-scheme: dark)')` and toggle `.theme-dark` on the body and app container accordingly."

---
