The micro unit test system we built for the SVG to PNG Converter is a highly efficient, **zero-dependency testing architecture**. It is specifically designed to work within your strict "standalone/embeddable" and "offline-first" rules.

Because your main application is securely locked inside an IIFE (Immediately Invoked Function Expression) to prevent global scope pollution, a traditional test suite wouldn't be able to access the internal functions.

Here is a breakdown of how this custom architecture works, followed by the exact instructions you can use to ask me to implement it in future projects.

### The 4 Pillars of the Micro Unit Test System

1. **The URL-Triggered Injector (`?test=run`)**
The main HTML file checks `window.location.search` for the word `test=`. If it's missing, the app runs normally with zero performance overhead. If it is present, the app dynamically creates a `<script>` tag and injects the external `..._tests.js` file.
2. **The `__TEST_API__` Bridge**
To test private internal functions (like `formatXML` or `syncDataUrl`) without polluting the global window object for regular users, the app conditionally creates a `window.__TEST_API__` object *only* when test mode is activated. The test script uses this bridge to access internal logic.
3. **Vanilla JS Asynchronous Assertions**
Instead of using bulky external libraries like Jest or Mocha, the test file defines its own lightweight `assert()` and `assertTrue()` functions. Because it operates directly in the browser, it uses `async/await` and DOM polling (`setTimeout` loops) to wait for visual elements (like canvas rendering) to finish before asserting.
4. **The UI Toast "Enforcer"**
Instead of just logging to the hidden developer console, the test suite hooks directly into the application's native UI (the `#status-toast`). It uses a `setInterval` "enforcer" to aggressively keep the final test score visible on the screen, overriding any internal app timeouts.

---

### How to Request This in the Future

Whenever you create a new application and want me to generate this exact testing framework for it, you can copy and paste this block into your prompt:

> **Add the Vanilla Micro Unit Test System.**
> Please implement the URL-triggered testing architecture for this application:
> 1. **The Bridge:** Inside the main app's IIFE, check if the URL contains `?test=`. If true, expose necessary internal functions to a `window.__TEST_API__` object.
> 2. **The Injector:** Dynamically load a separate `{app_name}_tests.js` script. If the URL contains `?test=run`, automatically execute `window.__runTests()`.
> 3. **The Test Suite (Separate File):** Generate the companion Javascript test file. Include lightweight vanilla `assert()` and `assertTrue()` functions. Write tests that validate both internal logic (via the API bridge) and DOM UI changes.
> 4. **Visual Output:** Hook into the app's native UI (e.g., a toast notification) to display the final test pass/fail results. Use an interval enforcer to ensure the final score toast stays visible for 7 seconds without being overwritten by the app's internal timeouts.
> 
>

---


## 📋 **Generic Micro Unit Test Suite Specification**  
*Use this template to request the same testing infrastructure for **any** web application.*

---

### **Goal**  
Generate a self‑contained, offline micro unit test suite that validates critical functionality of a web application, automatically resets the app to its initial state after tests, and displays a prominent final result toast.

---

### **Core Infrastructure (Required for All Apps)**

1. **Test API Exposure**  
   - The host application must expose internal functions via a global object (e.g., `window.__TEST_API__`) when a query parameter (e.g., `?test=`) is present.  
   - Exposed functions should include all methods necessary for testing: core business logic, data transformation, UI update functions, etc.

2. **Assertion Helpers**  
   - `assert(name, actual, expected, message?)` – strict equality.  
   - `assertTrue(name, condition, message?)` – boolean check.  
   - `assertStartsWith(name, str, prefix)` – string prefix validation.

3. **Asynchronous Test Loading**  
   - A generic `loadTestData(inputData, waitForCondition)` function that returns a `Promise`.  
   - Resolves when a specified condition (e.g., UI element appears, data loaded, no error) is met.  
   - Rejects after a configurable timeout (e.g., 6 seconds).

4. **Reset to Initial State**  
   - A `resetAppToInitialState()` function that:  
     - Restores default input values (text fields, checkboxes, dropdowns, etc.).  
     - Reloads the default/initial data into the UI.  
     - Clears any error messages or transient states.  
     - Suppresses or removes any lingering application toasts, alerts, or notifications that appear after reset.  
   - The reset must run **after** all tests complete, regardless of pass/fail.

5. **Final Toast Behaviour**  
   - After reset, display a **centered**, **visually enlarged** toast (2× the original toast size).  
   - Duration: **≥ 7 seconds**.  
   - The toast shows: `🧪 Tests: X passed, Y failed. App reset.`  
   - After it fades, restore the original toast position, size, and padding.

6. **Toast/Notification Suppression Watchdog**  
   - Since some app timeouts (e.g., “operation completed” messages) may fire 2–3 seconds after reset, a watchdog interval must scan for and remove any toast containing a specific identifiable string (e.g., a known transient message) for the first 3 seconds after reset.

7. **Execution & Output**  
   - Tests run automatically when the URL contains `?test=run` (or manually via `window.__runTests()`).  
   - Results are logged to the console with coloured PASS/FAIL messages.  
   - A summary is printed, and the final enlarged toast is shown.

---

### **Test Coverage (Adapt to Your App)**

Write tests that validate:

- **Core functionality** – The primary feature the app provides (e.g., data conversion, calculation, rendering).  
- **Edge cases** – Empty inputs, invalid data, missing required attributes, extreme values.  
- **UI state management** – Input fields reset correctly, error messages appear when expected, disabled/enabled states.  
- **Asynchronous behaviour** – Loading indicators, delayed operations, timeouts.  
- **Fallback / defensive logic** – Default values when data is malformed, fallback UI when feature unavailable.  
- **Output generation** – If the app produces files or data URLs, verify headers, signatures, or structure.  
- **Event handling** – Drag & drop, file upload, button clicks, keyboard shortcuts.

---

### **Example Generic Prompt to Use**

> *“Add the same micro unit test suite as described in the generic specification. Expose `window.__TEST_API__` with the necessary internal functions, implement all assertions, async load tests, reset functionality with toast suppression, and display a large centered final toast for 7 seconds. Adapt the test coverage to this app’s core features, edge cases, and UI state.”*

---

### **Why This Works for Any App**

- **No Hardcoded Domains** – The spec talks about “core functionality,” “UI state,” “output generation” without mentioning SVG, PNG, or BMP.  
- **Configurable** – The test author decides which functions to expose and which conditions to wait for.  
- **Clean Reset** – Works for any form‑based or interactive app.  
- **User‑Friendly** – The large toast and console logs provide clear pass/fail feedback without interfering with normal use.
