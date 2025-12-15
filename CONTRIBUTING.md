# Contributing to Gen-TTS

First off, thanks for taking the time to contribute! 🎉

We welcome contributions of all kinds, including bug reports, feature requests, documentation improvements, and code changes.

## How to Contribute

### Reporting Bugs
If you find a bug, please create a new issue. Be sure to include:
- A clear, descriptive title.
- Steps to reproduce the issue.
- Expected vs. actual behavior.
- Your operating system and Python version.

### Suggesting Features
We love new ideas! If you have a feature request, please open an issue and describe:
- The problem you're trying to solve.
- Your proposed solution or feature.
- Any alternative solutions you've considered.

### Pull Requests
1. **Fork the repository** and clone it locally.
2. **Create a new branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/amazing-new-feature
   ```
3. **Install dependencies** (we recommend using `uv`):
   ```bash
   uv sync
   ```
4. **Make your changes.** Please ensure your code follows the existing style.
5. **Run tests** to ensure you haven't broken anything:
   ```bash
   python -m pytest tests/
   ```
6. **Commit your changes** with descriptive commit messages.
7. **Push to your fork** and submit a Pull Request!

## Development Setup

We use `uv` for dependency management.

```bash
# Install uv
pip install uv

# Create virtual env and install dependencies
uv sync

# Run the CLI locally
uv run gen-tts --help
```

## Code of Conduct
Please be respectful and kind to others. We strive to maintain a welcoming and inclusive community.
