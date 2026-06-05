### If you need diff but standart diff malformatted

`Generate a Python script using str.replace() to apply these updates.`

`Use the Python string replacement method for this patch.`

`Output a Python replace() script instead of a diff.`


### If can't download right side generated text in markdown

`Create a standalone HTML utility to download this text as a file.` Mentioning terms like `offline HTML downloader`, `client-side download button`, or `use a JavaScript Blob to download` will always trigger this exact same approach!

```
Please provide the requested file wrapped in a standalone HTML Downloader utility. Store the raw, fully formatted content (like Markdown or code) safely inside a hidden <textarea> to preserve all brackets and spacing. Include a simple, styled UI with a 'Download' button that uses JavaScript to create a Blob and trigger a local file download directly to my machine.
```

### App requre large amount of well known data (BIP-39 dictionary as example

`Mock the large dataset as a single-line string (e.g., const DATA_RAW = "...") inside the IIFE to keep patch scripts clean. I will insert the real data later`

and use this code
```
// =========================================================================
// >>> BEGIN OF BLACK BOX DATA <<<
// [DO NOT MODIFY, PRINT, OR INCLUDE THIS BLOCK IN PYTHON PATCH SCRIPTS]
const BIP39_RAW = "abandon ... table ... zoo"; // (truncated for example)
// >>> END OF BLACK BOX DATA <<<
// =========================================================================

// Runtime Parsing (Instantly converts the string into a 2048-item array)
const bip39Dictionary = BIP39_RAW.split(" ");
```
shorter forms of comments
```
// [AI-SKIP-START] Do not modify or include in python scripts
const BIP39_DICTIONARY = [
    "abandon", 
    "ability", 
    // ...
];
// [AI-SKIP-END]
```
```
// [AI-SKIP] Black box data. Do not modify or include in python scripts.
const BIP39_RAW = "abandon ability able about above..."; 
```
