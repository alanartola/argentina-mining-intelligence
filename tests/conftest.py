import sys
from pathlib import Path

# Streamlit adds `app/` to sys.path at runtime (it's the entrypoint script's
# directory), which is how pages import `style`. Tests need the same so
# `import style` works here too, without changing the app's structure.
APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
