# Contributing to SoundSight

Thank you for your interest in contributing to SoundSight! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## 📜 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Please:

- Be respectful and inclusive in your language and actions
- Accept constructive criticism gracefully
- Focus on what's best for the community and project
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- Git for version control
- Docker (optional, for containerized development)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/Keys-Notations-Scales-Chords-Mp3-php.git
cd Keys-Notations-Scales-Chords-Mp3-php
```

3. Add the upstream remote:

```bash
git remote add upstream https://github.com/MyOldRepositories/Keys-Notations-Scales-Chords-Mp3-php.git
```

## 💻 Development Setup

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
FLASK_DEBUG=1 python waveform_generator.py
```

### Docker Development

```bash
# Build and run with Docker
docker-compose up --build
```

## 🌳 Branching Strategy

We follow a simplified Git Flow branching model:

### Branch Types

| Branch | Purpose | Base Branch | Merge Into |
|--------|---------|-------------|------------|
| `main` | Production-ready code | - | - |
| `develop` | Integration branch for features | `main` | `main` |
| `feature/*` | New features | `develop` | `develop` |
| `bugfix/*` | Bug fixes | `develop` | `develop` |
| `hotfix/*` | Critical production fixes | `main` | `main` & `develop` |
| `release/*` | Release preparation | `develop` | `main` & `develop` |

### Branch Naming Convention

```
feature/short-description
bugfix/issue-number-short-description
hotfix/critical-fix-description
release/v1.2.0
```

### Examples

```bash
# Feature branch
git checkout -b feature/add-svg-export

# Bug fix branch
git checkout -b bugfix/123-fix-color-parsing

# Hotfix branch
git checkout -b hotfix/fix-ffmpeg-crash

# Release branch
git checkout -b release/v1.1.0
```

### Workflow

1. **Features**: Create from `develop`, merge back to `develop`
2. **Bug fixes**: Create from `develop`, merge back to `develop`
3. **Hotfixes**: Create from `main`, merge to both `main` and `develop`
4. **Releases**: Create from `develop`, merge to both `main` and `develop`

## ✏️ Making Changes

### 1. Sync Your Fork

```bash
git fetch upstream
git checkout develop
git merge upstream/develop
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Write clean, readable code
- Follow the coding standards (see below)
- Add or update tests as needed
- Update documentation if required

### 4. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: <type>(<scope>): <description>

git commit -m "feat(waveform): add gradient color support"
git commit -m "fix(converter): handle empty MP3 files"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(api): add unit tests for color parsing"
```

#### Commit Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |
| `perf` | Performance improvements |

### 5. Push Your Branch

```bash
git push origin feature/your-feature-name
```

## 🔄 Pull Request Process

### Creating a Pull Request

1. Go to the repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] My code follows the project's coding standards
- [ ] I have tested my changes locally
- [ ] I have updated documentation as needed
- [ ] I have added tests (if applicable)
```

### PR Guidelines

- **One feature/fix per PR** - Keep PRs focused
- **Reference issues** - Link related issues using `Fixes #123` or `Relates to #456`
- **Provide context** - Explain why changes are needed
- **Include screenshots** - For UI changes, add before/after screenshots
- **Keep it small** - Smaller PRs are easier to review

### Review Process

1. Automated checks must pass
2. At least one maintainer review required
3. Address all review feedback
4. Maintain a clean commit history

## 📝 Coding Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with these additions:

```python
# Use type hints
def process_audio(file_path: str, options: dict) -> Image.Image:
    pass

# Use docstrings for public functions
def generate_waveform(wav_file: str) -> Image.Image:
    """
    Generate a waveform image from a WAV file.
    
    Args:
        wav_file: Path to the WAV file
        
    Returns:
        PIL Image object containing the waveform
        
    Raises:
        ValueError: If the file is not a valid WAV file
    """
    pass

# Use meaningful variable names
waveform_color = "#FF0000"  # Good
wc = "#FF0000"              # Bad

# Use constants for magic values
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
DEFAULT_WIDTH = 500
```

### File Organization

```
project/
├── waveform_generator.py   # Main application
├── requirements.txt        # Dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Container orchestration
├── README.md              # Project documentation
├── CONTRIBUTING.md        # This file
├── LICENSE                # License file
└── tests/                 # Test files (coming soon)
    ├── __init__.py
    ├── test_converter.py
    └── test_waveform.py
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=waveform_generator

# Run specific test file
pytest tests/test_converter.py
```

### Writing Tests

```python
import pytest
from waveform_generator import html2rgb, convert_mp3_to_wav

def test_html2rgb_valid_color():
    assert html2rgb("#FF0000") == (255, 0, 0)
    assert html2rgb("00FF00") == (0, 255, 0)

def test_html2rgb_invalid_color():
    with pytest.raises(ValueError):
        html2rgb("invalid")
```

## 📚 Documentation

### When to Update Documentation

- Adding new features
- Changing existing behavior
- Adding new configuration options
- Fixing documentation errors

### Documentation Locations

| Type | Location |
|------|----------|
| User guide | `README.md` |
| API reference | Docstrings in code |
| Contributing | `CONTRIBUTING.md` |
| Changelog | `CHANGELOG.md` (create if needed) |

## 🎯 Areas for Contribution

Looking for ways to contribute? Here are some ideas:

### Good First Issues

- Improve error messages
- Add input validation
- Fix typos in documentation
- Add more examples to README

### Feature Ideas

- Support for additional audio formats (WAV, OGG, FLAC)
- Real-time waveform preview
- Batch processing multiple files
- REST API endpoint
- Color gradient support
- Export to SVG format
- Waveform animation support
- Audio playback with visualization

### Infrastructure

- Add CI/CD pipeline
- Set up automated testing
- Improve Docker configuration
- Add linting checks

## ❓ Questions?

If you have questions about contributing:

1. Check existing [issues](https://github.com/MyOldRepositories/Keys-Notations-Scales-Chords-Mp3-php/issues)
2. Open a new issue with the `question` label
3. Ask in discussions (if enabled)

---

Thank you for contributing to SoundSight! 🎵
