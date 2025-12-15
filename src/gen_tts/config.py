import os
from pathlib import Path
from dotenv import load_dotenv
import stat
import sys

USER_CONFIG_DIR = Path.home() / ".config" / "gen-tts"
USER_CONFIG_FILE = USER_CONFIG_DIR / ".env"

def ensure_config_exists():
    """Ensures the user config directory and .env file exist and are secured."""
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not USER_CONFIG_FILE.exists():
        with open(USER_CONFIG_FILE, "w") as f:
            f.write("""# Google Cloud API Key (for Gemini TTS authentication)
GOOGLE_API_KEY='replace_with_your_api_key'

# Your Google Cloud Project ID (optional, but good practice)
GCLOUD_PROJECT='ucr-research-computing'
""")
        print(f"Created default config file: {USER_CONFIG_FILE}", file=sys.stderr)
        print(f"Please edit {USER_CONFIG_FILE} and replace 'replace_with_your_api_key' with your actual Google Cloud API Key.", file=sys.stderr)
        sys.exit(1)
    
    # Secure the file permissions
    current_permissions = USER_CONFIG_FILE.stat().st_mode
    # Check if group or others have write/execute permissions
    if current_permissions & (stat.S_IWGRP | stat.S_IXGRP | stat.S_IWOTH | stat.S_IXOTH):
        os.chmod(USER_CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR) # Only owner can read/write
        print(f"Secured permissions for {USER_CONFIG_FILE}. Only owner can read/write.", file=sys.stderr)

    load_dotenv(USER_CONFIG_FILE)
    load_dotenv() # Load from current directory's .env as well (for local overrides)

class Settings:
    """Manages application settings, primarily Google Cloud credentials and project ID."""
    def __init__(self):
        self._google_api_key = os.getenv("GOOGLE_API_KEY")
        self._gcloud_project = os.getenv("GCLOUD_PROJECT", "ucr-research-computing")

    @property
    def google_api_key(self) -> str:
        return self._google_api_key or ""

    @property
    def gcloud_project(self) -> str:
        return self._gcloud_project

# Load settings immediately
ensure_config_exists()
settings = Settings()
