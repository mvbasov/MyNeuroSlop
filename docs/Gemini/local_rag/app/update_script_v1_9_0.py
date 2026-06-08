import os

def patch_file():
    target_file = "app.py"
    
    if not os.path.exists(target_file):
        print(f"Error: {target_file} not found in current directory!")
        return

    print(f"Reading {target_file}...")
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Define the replacements (Russian comments to English + Version bump)
    replacements = [
        (
            "# Настройка логирования",
            "# Setup logging"
        ),
        (
            "# Отключение подробных логов библиотек по умолчанию",
            "# Disable verbose library logs by default"
        ),
        (
            'VERSION = "1.8.0"',
            'VERSION = "1.9.0"'
        ),
        (
            "# Текущая версия приложения",
            "# Current version of the application"
        ),
        (
            "# Переменные окружения Docker",
            "# Docker environment variables"
        ),
        (
            "# Базовый путь для file://",
            "# Base path for file://"
        ),
        (
            "# --- Динамический выбор модели эмбеддингов ---",
            "# --- Dynamic embedding model selection ---"
        ),
        (
            "# Считываем выбранную модель из переменной окружения Docker Compose.",
            "# Read selected model from Docker Compose environment variable."
        ),
        (
            '# По умолчанию используется русскоязычная "nomic-embed-text".',
            '# Defaults to multilingual "nomic-embed-text".'
        ),
        (
            '# Для переключения обратно на английскую "all-minilm" просто раскомментируйте её в docker-compose.yaml.',
            '# To switch back to English "all-minilm", uncomment it in docker-compose.yaml.'
        ),
        (
            "# Автоматическое определение размерности вектора на основе выбранной модели",
            "# Auto-detect vector size based on the selected model"
        ),
        (
            "# Размерность для nomic-embed-text",
            "# Dimension for nomic-embed-text"
        ),
        (
            "# Размерность для bge-m3",
            "# Dimension for bge-m3"
        ),
        (
            "# Размерность для all-minilm",
            "# Dimension for all-minilm"
        ),
        (
            "# Размерность для paraphrase-multilingual",
            "# Dimension for paraphrase-multilingual"
        ),
        (
            "# Инициализация коллекции с динамической размерностью вектора (VECTOR_SIZE)",
            "# Initialize collection with dynamic vector dimension (VECTOR_SIZE)"
        )
    ]

    print("Applying patches...")
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

    print("Successfully patched! app.py is now fully in English and upgraded to v1.9.0.")

if __name__ == "__main__":
    patch_file()