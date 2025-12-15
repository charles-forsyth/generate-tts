import subprocess
import sys
import os
import pytest
from unittest.mock import patch

# Import the modules directly to allow easier patching if we were calling main()
# But for subprocess tests, we just need to ensure the environment is sane.
import gen_tts.core
import gen_tts.config

# Add the src directory to the Python path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Note: Mocks here do NOT affect the subprocess.run calls. 
# They are only useful if we imported and ran main() directly.
# Since these are smoke tests for the CLI command, we rely on the subprocess.

def test_list_voices():
    """Test that the --list-voices command runs without error and prints expected output."""
    
    try:
        # We assume gen-tts is installed or we can run it via python -m gen_tts.cli
        # Using "gen-tts" assumes it's in the path (which it is if installed via uv tool or pip install -e .)
        result = subprocess.run(["gen-tts", "--list-voices"],
                                capture_output=True, text=True, check=True)
        
        assert "Available Gemini TTS Voices:" in result.stdout
        # Check if at least some of the hardcoded voices are present
        assert "Kore" in result.stdout
        assert "Zephyr" in result.stdout
        assert result.returncode == 0
        print("\n--list-voices test passed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\n--list-voices test failed. Stderr: {e.stderr}", file=sys.stderr)
        # If it fails due to config missing, we might need to mock that environment variable or file
        # But ensure_config_exists handles creation.
        pytest.fail(f"Subprocess failed with exit code {e.returncode}: {e.stderr}")
    except FileNotFoundError:
        pytest.fail("gen-tts command not found. Ensure the project is installed.")

def test_no_input_error():
    """Test that running gen-tts without any input arguments raises an error."""
    
    try:
        result = subprocess.run(["gen-tts"],
                                capture_output=True, text=True, check=False)
        
        assert result.returncode != 0
        assert "No input provided." in result.stderr or "the following arguments are required" in result.stderr
        print("\nNo input error test passed successfully.")
    except FileNotFoundError:
        pytest.fail("gen-tts command not found. Ensure the project is installed.")
