# Шпаргалка: Как быстро запросить интерактивный HTML-загрузчик

# Cheat Sheet: How to Quickly Request an Interactive HTML Downloader

## 🇷🇺 На русском языке (Russian)

Чтобы получить такой загрузчик для любого текста, кода или файла конфигурации, отправьте мне простой запрос, используя следующий шаблон:

### 📋 Шаблон промпта

> «Создай интерактивный HTML-файл-загрузчик для контента из \[Имя вашего файла или описание\].
>
> **Технические требования:**
>
> 1. **Формат:** Один самостоятельный HTML-файл с использованием Tailwind CSS (стильная темная тема).
>
> 2. **Интерактив:** Кнопка «Скачать (.md)» (или расширение вашего файла) и кнопка «Скопировать в буфер обмена».
>
> 3. **Совместимость:** Для копирования используй традиционный метод `document.execCommand('copy')`, встроенный в невидимую `textarea`, так как стандартный `navigator.clipboard` блокируется политиками безопасности iframe.
>
> 4. **Интерфейс:** Окно предпросмотра контента с прокруткой и красивая анимация нажатия кнопок.»

### 💡 Почему это работает?

* **Использование `execCommand`:** Это критически важно в среде Canvas (веб-интерфейсах чатов). Стандартные методы работы с буфером обмена безопасности часто блокируются внутри фреймов, а старый добрый `execCommand` работает безотказно.

* **Tailwind CSS через CDN:** Позволяет мгновенно собрать интерфейс премиум-уровня без локальной установки зависимостей.

## 🇬🇧 На английском языке (English)

To get a similar downloader for any text, code, or configuration file, you can send a simple prompt using this template:

### 📋 Prompt Template

> "Create an interactive HTML file downloader for the content of \[Your File Name or Description\].
>
> **Technical Requirements:**
>
> 1. **Format:** A single, self-contained HTML file styled with Tailwind CSS (modern dark theme).
>
> 2. **Interactivity:** A "Download (.md)" button (or your specific file extension) and a "Copy Text" button.
>
> 3. **Compatibility:** For copying, use the fallback `document.execCommand('copy')` method inside a temporary, hidden `textarea` because the standard `navigator.clipboard` is often blocked by iframe security policies.
>
> 4. **UI:** A scrollable preview pane showing the raw content, with nice active/hover states for the buttons."

### 💡 Why this works

* **`execCommand` usage:** Essential for Canvas or iframe-based preview spaces. Modern browser APIs like `navigator.clipboard.writeText` might fail inside nested sandboxed documents, but this fallback bypasses those limitations perfectly.

* **Tailwind via CDN:** Ensures a stunning, modern look instantly within the Preview window without complex assets.