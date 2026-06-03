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
