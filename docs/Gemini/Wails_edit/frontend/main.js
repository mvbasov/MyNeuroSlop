const editor = document.getElementById('editor');
const scrollFrame = document.getElementById('scroll-frame');
const status = document.getElementById('status');
const resultsPanel = document.getElementById('results-panel');

let fileMeta = { size: 0, chunkSize: 0 };
let currentReadOffset = 0;
let isBufferLoading = false;

function initializeFileStream(event) {
    const file = event.target.files[0];
    if (!file) return;

    document.getElementById('file-info').innerText = `${file.name} (${(file.size / (1024*1024)).toFixed(1)}MB)`;
    editor.value = ""; 
    currentReadOffset = 0;

    window.go.main.App.OpenLargeFile(file.name)
        .then((meta) => {
            fileMeta = meta;
            fetchNextWindowChunk();
        })
        .catch(err => { status.innerText = "Stream Error: " + err; });
}

// Append new bytes asynchronously when infinite trigger threshold cross occurs
function fetchNextWindowChunk() {
    if (isBufferLoading || currentReadOffset >= fileMeta.size) return;
    isBufferLoading = true;
    status.innerText = "Streaming sequential data blocks...";

    window.go.main.App.ReadNextChunk(BigInt(currentReadOffset))
        .then((newText) => {
            if (newText) {
                // Concat text block to existing editor container data seamlessly
                editor.value += newText;
                currentReadOffset += fileMeta.chunkSize;
                status.innerText = `Rendered up to byte position: ${currentReadOffset} / ${fileMeta.size}`;
            }
            isBufferLoading = false;
        })
        .catch(err => {
            console.error(err);
            isBufferLoading = false;
        });
}

// Infinite scroll detection boundary evaluation loop
function handleViewportScroll() {
    const triggerThresholdBytes = 120; // Fire when user is within 120px of bottom margin boundary
    const remainsToScroll = scrollFrame.scrollHeight - scrollFrame.scrollTop - scrollFrame.clientHeight;

    if (remainsToScroll <= triggerThresholdBytes) {
        fetchNextWindowChunk(); // Proactively fetch and load more data rows
    }
}

// Index search processing logic execution sequence
function executeSearch() {
    const queryText = document.getElementById('search-input').value;
    if (!queryText) {
        resultsPanel.style.display = "none";
        return;
    }

    status.innerText = "Executing deep-scan index lookup processing...";
    resultsPanel.innerHTML = "";

    window.go.main.App.GlobalSearch(queryText)
        .then((matches) => {
            if (!matches || matches.length === 0) {
                resultsPanel.innerHTML = "<div class='result-item' style='color:#ff5555'>No match occurrences discovered.</div>";
                resultsPanel.style.display = "block";
                return;
            }

            resultsPanel.style.display = "block";
            matches.forEach(item => {
                const node = document.createElement('div');
                node.className = 'result-item';
                node.innerText = `Line ${item.lineNumber}: ${item.text.substring(0, 60)}`;
                // Assign quick access anchor target jump event 
                node.onclick = () => jumpToByteOffset(item.byteOffset);
                resultsPanel.appendChild(node);
            });
            status.innerText = `Discovered ${matches.length} matches inside current stream structure.`;
        })
        .catch(err => { status.innerText = "Search processing failed: " + err; });
}

// Instantly shift view context targeting exact stream coordinates directly
function jumpToByteOffset(byteOffset) {
    status.innerText = `Jumping position target directly to Byte: ${byteOffset}`;
    resultsPanel.style.display = "none"; // Clear search workspace focus overlay

    // Force application read head to align matching offset index bounds context parameters
    currentReadOffset = parseInt(byteOffset);
    
    window.go.main.App.ReadNextChunk(BigInt(currentReadOffset))
        .then((targetText) => {
            editor.value = "=== COORD JUMP CONTEXT ===\n" + targetText;
            currentReadOffset += fileMeta.chunkSize;
            scrollFrame.scrollTop = 0; // Snap vertical scrolling metrics track straight back to top marker
        });
}

