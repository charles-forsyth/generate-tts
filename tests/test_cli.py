import subprocess
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Import the modules directly to allow easier patching
import gen_tts.core
import gen_tts.config

# Add the src directory to the Python path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock gen_tts.config.ensure_config_exists to prevent exit during tests
@patch.object(gen_tts.config, 'ensure_config_exists', autospec=True)
# Mock gen_tts.core.genai.configure to prevent actual API key configuration
@patch.object(gen_tts.core.genai, 'configure', autospec=True)
# Mock gen_tts.core.GenerativeModel to prevent actual model instantiation
@patch.object(gen_tts.core, 'GenerativeModel', autospec=True)
def test_list_voices(mock_generative_model, mock_genai_configure, mock_ensure_config_exists):
    """Test that the --list-voices command runs without error and prints expected output."""
    mock_ensure_config_exists.return_value = None # Ensure it does not exit
    mock_genai_configure.return_value = None # Ensure configure runs without error
    
    # The list_gemini_voices() in core.py is now hardcoded, so no need to mock model listing

    try:
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
        assert False, f"Subprocess failed with exit code {e.returncode}: {e.stderr}"
    except FileNotFoundError:
        print("\nError: 'gen-tts' command not found. Ensure the project is installed with `pip install -e .`", file=sys.stderr)
        assert False, "gen-tts command not found."

@patch.object(gen_tts.config, 'ensure_config_exists', autospec=True)
def test_no_input_error(mock_ensure_config_exists):
    """Test that running gen-tts without any input arguments raises an error."""
    mock_ensure_config_exists.return_value = None # Ensure it does not exit
    
    try:
        result = subprocess.run(["gen-tts"],
                                capture_output=True, text=True, check=False)
        
        assert result.returncode != 0
        assert "No input provided." in result.stderr or "the following arguments are required" in result.stderr
        print("\nNo input error test passed successfully.")
    except FileNotFoundError:
        print("\nError: 'gen-tts' command not found. Ensure the project is installed with `pip install -e .`", file=sys.stderr)
        assert False, "gen-tts command not found."