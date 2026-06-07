# patch.py

with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# 1. Update Version
app_code = app_code.replace(
    'VERSION = "1.3.0"',
    'VERSION = "1.4.0"'
)

# 2. Update chunk_text_smart default character limit
app_code = app_code.replace(
    'def chunk_text_smart(text, max_chars=400):',
    'def chunk_text_smart(text, max_chars=150):'
)

# 3. Increase Ollama context window explicitly in the payload
old_payload = """        "options": {"num_thread": 1}
    }"""

new_payload = """        "options": {
            "num_thread": 1,
            "num_ctx": 512
        }
    }"""

app_code = app_code.replace(old_payload, new_payload)

# 4. Update the split_md_sections limits
old_split = """        if len(text) > 400:
            sub_chunks = chunk_text_smart(text, max_chars=400)"""

new_split = """        if len(text) > 150:
            sub_chunks = chunk_text_smart(text, max_chars=150)"""

app_code = app_code.replace(old_split, new_split)

# Save the updated code
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

print("Successfully patched app.py to version 1.4.0 with token limit fixes!")