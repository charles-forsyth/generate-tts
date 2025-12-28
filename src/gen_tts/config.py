import os
import stat
import sys
from pathlib import Path

from dotenv import load_dotenv

# Define configuration paths
USER_CONFIG_DIR = Path.home() / ".config" / "gen-tts"
USER_CONFIG_FILE = USER_CONFIG_DIR / ".env"

def ensure_config_exists() -> None:
    """Ensure the user config directory and .env file exist and are secured."""
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not USER_CONFIG_FILE.exists():
        try:
            with open(USER_CONFIG_FILE, "w") as f:
                f.write("GOOGLE_API_KEY=replace_with_your_api_key\n")
                f.write("GCLOUD_PROJECT=ucr-research-computing\n")

            # Set restrictive permissions (600: read/write for owner only)
            os.chmod(USER_CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
        except OSError as e:
            print(
                f"Warning: Could not set secure permissions on {USER_CONFIG_FILE}: {e}",
                file=sys.stderr
            )

        print(f"Created new configuration file at: {USER_CONFIG_FILE}", file=sys.stderr)
        print(
            "Please edit this file to add your GOOGLE_API_KEY and GCLOUD_PROJECT.",
            file=sys.stderr
        )
    else:
        # Check and enforce permissions if they exist but are too open
        try:
            current_permissions = stat.S_IMODE(os.lstat(USER_CONFIG_FILE).st_mode)
            # Check if group or others have any permission
            if current_permissions & (stat.S_IWGRP | stat.S_IXGRP | stat.S_IWOTH | stat.S_IXOTH):
                # Only owner can read/write
                os.chmod(USER_CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
                print(
                    f"Secured permissions for {USER_CONFIG_FILE}. Only owner can read/write.",
                    file=sys.stderr
                )
        except OSError as e:
            print(
                f"Warning: Could not verify permissions on {USER_CONFIG_FILE}: {e}",
                file=sys.stderr
            )

    load_dotenv(USER_CONFIG_FILE)

class Settings:
    """Manages application settings, primarily Google Cloud credentials and project ID."""

    def __init__(self) -> None:
        self._google_api_key = os.getenv("GOOGLE_API_KEY")
        self._gcloud_project = os.getenv("GCLOUD_PROJECT", "ucr-research-computing")

    @property
    def google_api_key(self) -> str:
        """Return the Google API Key from environment variables."""
        return self._google_api_key or ""

    @property
    def gcloud_project(self) -> str:
        """Return the Google Cloud Project ID from environment variables."""
        return self._gcloud_project

# Singleton instance
settings = Settings()
