import os

def patch_docker_compose():
    target_file = "docker-compose.yaml"
    
    if not os.path.exists(target_file):
        print(f"Error: {target_file} not found in the current directory!")
        return

    print(f"Reading {target_file}...")
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Define Russian to English comment replacements
    replacements = [
        (
            "# Передаем переменную модели в пуллер для автоматической загрузки",
            "# Pass the model variable to the puller for automated downloading"
        ),
        (
            "# - EMBED_MODEL=all-minilm  # Раскомментируйте для возврата к all-minilm",
            "# - EMBED_MODEL=all-minilm  # Uncomment to revert back to all-minilm"
        ),
        (
            "# Настройка модели эмбеддинга на этапе развертывания",
            "# Configure the embedding model at the deployment stage"
        )
    ]

    print("Applying replacements...")
    patched_content = content
    for old, new in replacements:
        if old in patched_content:
            patched_content = patched_content.replace(old, new)
            print(f" -> Replaced: '{old}' -> '{new}'")
        else:
            print(f" -> Warning: Original text segment not found: '{old}'")

    print(f"Writing changes back to {target_file}...")
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(patched_content)

    print(f"Successfully patched! {target_file} comments are now fully in English.")

if __name__ == "__main__":
    patch_docker_compose()