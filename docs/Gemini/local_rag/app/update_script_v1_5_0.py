# patch_logs.py
import os

with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

# 1. Update Version
if 'VERSION = "1.4.0"' in app_code:
    app_code = app_code.replace(
        'VERSION = "1.4.0"',
        'VERSION = "1.5.0"'
    )
elif 'VERSION =' not in app_code:
    # Fallback if version was somehow stripped in a previous step
    app_code = app_code.replace(
        'logger = logging.getLogger(__name__)\n',
        'logger = logging.getLogger(__name__)\n\n# Versioning\nVERSION = "1.5.0"\n'
    )

# 2. Add the HTTP logging switch
old_logging_setup = """# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)"""

new_logging_setup = """# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Make third-party HTTP logging switchable off by default
if os.environ.get("ENABLE_HTTP_LOGS", "false").lower() != "true":
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client.http").setLevel(logging.WARNING)"""

app_code = app_code.replace(old_logging_setup, new_logging_setup)

# Save the updated code
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

print("Successfully patched app.py to version 1.5.0! HTTP logs are now silenced by default.")