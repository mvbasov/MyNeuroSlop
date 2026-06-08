import os

def apply_patch():
    filepath = "app.py"
    
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found in the current directory.")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Update Version
    old_version = 'VERSION = "1.6.0"'
    new_version = 'VERSION = "1.7.0"'
    
    if old_version in code:
        code = code.replace(old_version, new_version)
    else:
        print("Warning: Version string match not found or already updated.")

    # 2. Inject the extract_markdown_links utility function
    # Placing it cleanly above clean_json_string function
    target_placement = "def clean_json_string(s):"
    
    link_extractor_func = """def extract_markdown_links(content, rel_path, global_metadata):
    \"\"\"Extracts Markdown links [text](url), creating explicit chunks to prevent clipping.\"\"\"
    link_chunks = []
    pattern = r'\\[([^\\]]+)\\]\\((https?://[^\\)]+)\\)'
    
    matches = re.findall(pattern, content)
    for text, url in matches:
        text = text.strip()
        url = url.strip()
        
        if not text or not url:
            continue
            
        # Enrich text to maximize semantic embedding performance
        chunk_text = f"Source File: {rel_path}\\nDescription: {text}\\nURL: {url}"
        
        meta = global_metadata.copy()
        meta.update({
            "extracted_title": text,
            "url": url,
            "chunk_type": "link"
        })
        
        link_chunks.append({
            'text': chunk_text,
            'anchor': None,
            'timestamp': None,
            'file_url': get_file_url(rel_path),
            'metadata': meta
        })
        
    return link_chunks

def clean_json_string(s):"""

    if target_placement in code and "extract_markdown_links" not in code:
        code = code.replace(target_placement, link_extractor_func)

    # 3. Integrate Link Extractor into the master parsing pipeline (process_file_content)
    # Also fully translates all comments inside process_file_content to English
    old_pipeline = """def process_file_content(content, rel_path):
    \"\"\"Master pipeline: Parses JSON entirely, strips Pelican headers, extracts embedded JSON, chunks markdown.\"\"\"
    chunks = []
    global_metadata = {}
    
    # 1. Attempt to parse entire file as pure JSON
    try:
        data = json.loads(clean_json_string(content))
        if isinstance(data, list):
            for item in data:
                chunks.extend(process_json_item(item, rel_path, global_metadata))
            return chunks
        elif isinstance(data, dict):
            chunks.extend(process_json_item(data, rel_path, global_metadata))
            return chunks
    except json.JSONDecodeError:
        pass # Not a pure JSON file, proceed with Markdown parsing
        
    # 2. Extract Pelican Header Block (Contiguous block of Key: Value at start of file)
    lines = content.splitlines()
    header_end = 0
    is_pelican = True
    for idx, line in enumerate(lines):
        if not line.strip(): 
            header_end = idx
            break
        match = re.match(r'^([A-Za-z_-]+):\\s+(.*)$', line)
        if match:
            global_metadata[match.group(1).lower()] = match.group(2)
        else:
            is_pelican = False
            break
            
    if is_pelican and header_end > 0:
        content = '\\n'.join(lines[header_end:]).strip()
        
    # 3. Extract Embedded JSON Blocks (```json ... ```)
    json_blocks = re.findall(r'```json\\s*(.*?)\\s*```', content, re.DOTALL | re.IGNORECASE)
    for block in json_blocks:
        try:
            data = json.loads(clean_json_string(block))
            if isinstance(data, list):
                for item in data:
                    chunks.extend(process_json_item(item, rel_path, global_metadata))
            elif isinstance(data, dict):
                chunks.extend(process_json_item(data, rel_path, global_metadata))
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse embedded JSON in {rel_path}: {e}")
            
    # Strip the JSON blocks from standard markdown parsing so we don't duplicate indexing
    content = re.sub(r'```json\\s*.*?\\s*```', '', content, flags=re.DOTALL | re.IGNORECASE).strip()

    # 4. Extract Embedded Bookmarks JSON (<script>bookmarks = [...]</script>)
    bookmark_scripts = re.finditer(r'<script[^>]*>\\s*bookmarks\\s*=\\s*(.*?)\\s*(?:;)?\\s*</script>', content, re.DOTALL | re.IGNORECASE)
    for match in bookmark_scripts:
        block = match.group(1)
        try:
            data = json.loads(clean_json_string(block))
            if isinstance(data, list):
                for item in data:
                    chunks.extend(process_json_item(item, rel_path, global_metadata))
            elif isinstance(data, dict):
                chunks.extend(process_json_item(data, rel_path, global_metadata))
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse bookmarks JSON in {rel_path}: {e}")
            
    # Strip the bookmarks scripts from standard markdown parsing so we don't duplicate indexing
    content = re.sub(r'<script[^>]*>\\s*bookmarks\\s*=\\s*.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE).strip()
    
    # 5. Process remaining Markdown text via Separator Rules
    if content:
        md_chunks = split_md_sections(content, rel_path, global_metadata)
        chunks.extend(md_chunks)
        
    return chunks"""

    new_pipeline = """def process_file_content(content, rel_path):
    \"\"\"Master pipeline: Parses JSON entirely, strips Pelican headers, extracts explicit links, extracts embedded JSON, chunks markdown.\"\"\"
    chunks = []
    global_metadata = {}
    
    # 1. Attempt to parse entire file as pure JSON
    try:
        data = json.loads(clean_json_string(content))
        if isinstance(data, list):
            for item in data:
                chunks.extend(process_json_item(item, rel_path, global_metadata))
            return chunks
        elif isinstance(data, dict):
            chunks.extend(process_json_item(data, rel_path, global_metadata))
            return chunks
    except json.JSONDecodeError:
        pass # Not a pure JSON file, proceed with Markdown parsing
        
    # 2. Extract Pelican Header Block (Contiguous block of Key: Value at start of file)
    lines = content.splitlines()
    header_end = 0
    is_pelican = True
    for idx, line in enumerate(lines):
        if not line.strip(): 
            header_end = idx
            break
        match = re.match(r'^([A-Za-z_-]+):\\s+(.*)$', line)
        if match:
            global_metadata[match.group(1).lower()] = match.group(2)
        else:
            is_pelican = False
            break
            
    if is_pelican and header_end > 0:
        content = '\\n'.join(lines[header_end:]).strip()

    # 3. Extract and preserve explicit Markdown links [text](url) as unique chunks
    link_chunks = extract_markdown_links(content, rel_path, global_metadata)
    chunks.extend(link_chunks)
        
    # 4. Extract Embedded JSON Blocks (```json ... ```)
    json_blocks = re.findall(r'```json\\s*(.*?)\\s*```', content, re.DOTALL | re.IGNORECASE)
    for block in json_blocks:
        try:
            data = json.loads(clean_json_string(block))
            if isinstance(data, list):
                for item in data:
                    chunks.extend(process_json_item(item, rel_path, global_metadata))
            elif isinstance(data, dict):
                chunks.extend(process_json_item(data, rel_path, global_metadata))
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse embedded JSON in {rel_path}: {e}")
            
    # Strip the JSON blocks from standard markdown parsing so we don't duplicate indexing
    content = re.sub(r'```json\\s*.*?\\s*```', '', content, flags=re.DOTALL | re.IGNORECASE).strip()

    # 5. Extract Embedded Bookmarks JSON (<script>bookmarks = [...]</script>)
    bookmark_scripts = re.finditer(r'<script[^>]*>\\s*bookmarks\\s*=\\s*(.*?)\\s*(?:;)?\\s*</script>', content, re.DOTALL | re.IGNORECASE)
    for match in bookmark_scripts:
        block = match.group(1)
        try:
            data = json.loads(clean_json_string(block))
            if isinstance(data, list):
                for item in data:
                    chunks.extend(process_json_item(item, rel_path, global_metadata))
            elif isinstance(data, dict):
                chunks.extend(process_json_item(data, rel_path, global_metadata))
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse bookmarks JSON in {rel_path}: {e}")
            
    # Strip the bookmarks scripts from standard markdown parsing so we don't duplicate indexing
    content = re.sub(r'<script[^>]*>\\s*bookmarks\\s*=\\s*.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE).strip()
    
    # 6. Process remaining Markdown text via Separator Rules
    if content:
        md_chunks = split_md_sections(content, rel_path, global_metadata)
        chunks.extend(md_chunks)
        
    return chunks"""

    if old_pipeline in code:
        code = code.replace(old_pipeline, new_pipeline)
    else:
        print("Error: Could not trace the exact pipeline function structural body.")
        return

    # Write the modified content back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
        
    print("Patch applied successfully! app.py updated to v1.7.0 with English translations and inline Markdown link protection.")

if __name__ == "__main__":
    apply_patch()