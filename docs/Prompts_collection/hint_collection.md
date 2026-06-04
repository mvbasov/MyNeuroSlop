### If you need diff but standart diff malformatted

"Generate a Python script using str.replace() to apply these updates."

"Use the Python string replacement method for this patch."

"Output a Python replace() script instead of a diff."


### If can't download right side generated text in markdown

"Create a standalone HTML utility to download this text as a file." Mentioning terms like "offline HTML downloader", "client-side download button", or "use a JavaScript Blob to download" will always trigger this exact same approach!

### App requre large amount of well known data (BIP-39 dictionary as example

"Mock the large dataset as a single-line string (e.g., const DATA_RAW = "...") inside the IIFE to keep patch scripts clean. I will insert the real data later"

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
