<div align="center">

# 🎵 SoundSight - Audio Analyzer & Waveform Generator

**Analyze your music • Extract key, tempo & chords • Generate stunning waveforms**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-BSD--2--Clause-orange.svg)](LICENSE)

[Features](#-features) • [How It Works](#-how-it-works) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api) • [Contributing](#-contributing)

---

> ⚠️ **Note to Contributors**: This is a **base version** of the SoundSight. We welcome contributions to extend functionality, improve accuracy, and add new features. The music analysis is based on audio signal processing heuristics and may not be 100% accurate for all tracks. See [Contributing](#-contributing) for guidelines.

---

## 📊 How It Works

The application processes your MP3 file through several stages to generate visual waveforms and extract musical information.

### Processing Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AUDIO WAVEFORM GENERATOR FLOW                        │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │  User Upload │
                              │   MP3 File   │
                              └──────┬───────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   1. FILE VALIDATION  │
                         │   • Check file type   │
                         │   • Verify MP3 format │
                         │   • Size limit check  │
                         └───────────┬───────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌───────────────────┐             ┌───────────────────┐
        │ 2. AUDIO CONVERT  │             │  3. MUSIC ANALYSIS │
        │   (FFmpeg/pydub)  │             │     (librosa)      │
        │                   │             │                    │
        │ • MP3 → WAV       │             │ • Extract tempo    │
        │ • Resample 8kHz   │             │ • Detect key/mode  │
        │ • Mono/Stereo     │             │ • Find chords      │
        └─────────┬─────────┘             │ • Estimate scale   │
                  │                       │ • Identify genre   │
                  │                       │ • Detect energy    │
                  ▼                       └─────────┬──────────┘
        ┌───────────────────┐                       │
        │ 4. WAVEFORM GEN   │                       │
        │    (Pillow)       │                       │
        │                   │                       │
        │ • Parse WAV data  │                       │
        │ • Scale amplitude │                       │
        │ • Draw waveform   │                       │
        │ • Apply colors    │                       │
        │ • Resize image    │                       │
        └─────────┬─────────┘                       │
                  │                                 │
                  └─────────────┬───────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   5. RESULTS DISPLAY  │
                    │                       │
                    │ • Waveform PNG image  │
                    │ • Key & Mode          │
                    │ • Scale (Dorian, etc) │
                    │ • Tempo (BPM)         │
                    │ • Chord progressions  │
                    │ • Instrument chords   │
                    │ • Genre hints         │
                    │ • Download option     │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  6. AUTO CLEANUP      │
                    │                       │
                    │ • Delete temp files   │
                    │ • Clear WAV files     │
                    │ • Free memory         │
                    └───────────────────────┘
```

### Key Processing Steps

| Step | Component | Description |
|------|-----------|-------------|
| 1 | **Validation** | Checks file type, format, and size limits (max 10MB) |
| 2 | **Conversion** | Uses FFmpeg via pydub to convert MP3 to WAV format |
| 3 | **Analysis** | librosa extracts musical features from the audio |
| 4 | **Generation** | Pillow creates the visual waveform from WAV data |
| 5 | **Display** | Results shown with analysis and download option |
| 6 | **Cleanup** | Temporary files automatically deleted after processing |

---

## ✨ Features

### Waveform Generation
- 🎨 **Custom Colors** - Choose any HEX color for waveform and background
- 📐 **Flexible Dimensions** - Set custom width and height for your output
- 🎧 **Stereo Support** - Visualize left and right channels separately
- 🖼️ **Transparent PNG** - Export with transparent backgrounds

### Music Analysis
- 🎵 **Key Detection** - Automatically detect the musical key (C, D, E, etc.)
- 🎹 **Mode Detection** - Identify Major or Minor mode
- 🎼 **Scale Detection** - Detect scale types (Dorian, Phrygian, Lydian, Mixolydian, etc.)
- 🥁 **Tempo Detection** - Extract BPM (beats per minute)
- 🎸 **Chord Estimation** - Identify possible chord progressions
- 🎹 **Instrument Chords** - View chords for different instruments (Guitar, Piano, Ukulele)
- 🎭 **Genre Hints** - Get suggestions about the genre style
- 🎻 **Instrument Detection** - Basic instrument presence hints

### Technical Features
- ⚡ **Real-time Progress** - Animated progress bar during processing
- 🗑️ **Auto Cleanup** - Temporary files automatically deleted after analysis
- 🐳 **Docker Ready** - Deploy instantly with production-ready containers
- 🌐 **Modern UI** - Beautiful, responsive interface with AJAX uploads
- 🔧 **Programmatic API** - Import as a Python module for automation

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/MyOldRepositories/Keys-Notations-Scales-Chords-Mp3-php.git
cd Keys-Notations-Scales-Chords-Mp3-php

# Start with Docker Compose
docker-compose up --build

# Open http://localhost:5000 in your browser
```

### Using Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python waveform_generator.py

# Open http://localhost:5000
```

---

## 📦 Installation

### Prerequisites

- **Python 3.8+** (for local installation)
- **FFmpeg** (required for audio processing)
- **Docker** (optional, for containerized deployment)

### Installing FFmpeg

FFmpeg is required for MP3 to WAV conversion.

<details>
<summary><b>Windows</b></summary>

```powershell
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
# Add to system PATH after installation
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
# Using Homebrew
brew install ffmpeg
```
</details>

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```
</details>

### Local Installation

```bash
# Clone the repository
git clone https://github.com/MyOldRepositories/Keys-Notations-Scales-Chords-Mp3-php.git
cd Keys-Notations-Scales-Chords-Mp3-php

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python waveform_generator.py
```

### Docker Installation

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t waveform-generator .
docker run -p 5000:5000 waveform-generator
```

---

## 🎯 Usage

### Web Interface

1. Open your browser to `http://localhost:5000`
2. Upload an MP3 file
3. Customize your settings:
   - **Width/Height**: Set dimensions in pixels
   - **Waveform Color**: Choose a HEX color (e.g., `#FF0000`)
   - **Background Color**: Set background or leave blank for transparent
   - **Stereo**: Enable to show separate L/R channels
   - **Analyze Music**: Enable to get key, tempo, chords, and scale analysis
4. Click **Generate Waveform**
5. View results including:
   - Waveform image with download option
   - Musical key and mode (e.g., "C Major")
   - Scale type (e.g., "Dorian", "Mixolydian")
   - Tempo in BPM
   - Chord progressions
   - Instrument-specific chord diagrams (dropdown)
6. Files are automatically cleaned up after processing

### Programmatic Usage

```python
from waveform_generator import convert_mp3_to_wav, generate_waveform_image, analyze_music

# Convert MP3 to WAV
convert_mp3_to_wav('my_song.mp3', 'my_song.wav')

# Generate waveform image
img = generate_waveform_image(
    wav_files=['my_song.wav'],
    width=800,
    height=200,
    foreground='#00FF00',  # Green waveform
    background='#000000'   # Black background
)

# Save the image
img.save('waveform.png')

# Analyze the music
analysis = analyze_music('my_song.mp3')
print(f"Key: {analysis['key']} {analysis['mode']}")
print(f"Scale: {analysis['scale']}")
print(f"Tempo: {analysis['tempo']} BPM")
print(f"Chords: {analysis['possible_chords']}")
```

---

## 🔧 API

### `convert_mp3_to_wav(mp3_path, output_path, stereo=False, channel='mono')`

Convert an MP3 file to WAV format.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mp3_path` | str | required | Path to input MP3 file |
| `output_path` | str | required | Path for output WAV file |
| `stereo` | bool | `False` | Process for stereo output |
| `channel` | str | `'mono'` | Channel to extract: `'mono'`, `'left'`, or `'right'` |

### `generate_waveform_image(wav_files, width, height, foreground, background, draw_flat)`

Generate a waveform PNG image from WAV files.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `wav_files` | List[str] | required | List of WAV file paths |
| `width` | int | `500` | Output image width in pixels |
| `height` | int | `100` | Output image height (per channel) |
| `foreground` | str | `'#FF0000'` | Waveform color (HEX) |
| `background` | str | `'#FFFFFF'` | Background color (HEX, empty for transparent) |
| `draw_flat` | bool | `False` | Draw flat-line sections |

### `analyze_music(mp3_path)`

Analyze an MP3 file for musical properties.

**Returns:** Dictionary containing:
- `key` - Musical key (C, C#, D, etc.)
- `mode` - Major or Minor
- `scale` - Scale type (Ionian, Dorian, Phrygian, etc.)
- `tempo` - BPM
- `possible_chords` - List of detected chords
- `instrument_chords` - Chord fingerings for different instruments
- `genre_hints` - Genre suggestions
- `energy` - Energy level (Low, Medium, High)

---

## 🐳 Docker Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `0` | Set to `1` for debug mode |

### Docker Commands

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild after changes
docker-compose up --build
```

### Resource Limits

The default `docker-compose.yml` includes:
- CPU limit: 1 core
- Memory limit: 512MB
- Health checks every 30 seconds

---

## 🛠️ Development

```bash
# Enable debug mode
FLASK_DEBUG=1 python waveform_generator.py

# Run tests (coming soon)
pytest tests/
```

---

## 🤝 Contributing

> 🚧 **This is a base version** - We actively welcome contributions to improve accuracy, add features, and enhance the user experience!

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- 🎵 **Improved Key Detection** - Better algorithms for key/mode detection
- 🎸 **More Instruments** - Add chord diagrams for more instruments
- 🎼 **Chord Recognition** - More accurate chord progression detection
- 🎭 **Genre Classification** - ML-based genre detection
- 🔊 **Audio Formats** - Support for WAV, OGG, FLAC, etc.
- 🌐 **Localization** - Multi-language support
- 📱 **Mobile UI** - Improved mobile responsiveness

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📋 Roadmap

- [ ] Support for additional audio formats (WAV, OGG, FLAC)
- [ ] Real-time waveform preview
- [ ] Batch processing multiple files
- [ ] REST API endpoint for headless usage
- [ ] Color gradient support for waveforms
- [ ] Audio playback with waveform visualization
- [ ] Export to SVG format
- [ ] Waveform animation support
- [ ] Machine learning-based genre detection
- [ ] Chord sheet/tab generation
- [ ] MIDI export from detected chords

---

## 📦 Versioning & Releases

- This project follows [Semantic Versioning](https://semver.org/).
- The current version is tracked in the `VERSION` file.
- All notable changes are documented in `CHANGELOG.md`.
- Release tags are created in the git repository for each public release (e.g., `v1.0.0`).

### Release Workflow

1. Update code and documentation as needed.
2. Bump the version in the `VERSION` file.
3. Add a new entry to `CHANGELOG.md`.
4. Commit changes and create a git tag:
   ```sh
   git add .
   git commit -m "Release v1.0.0"
   git tag v1.0.0
   git push origin master --tags
   ```

See `CHANGELOG.md` for release history.

---

## 📄 License

This project is licensed under the **BSD-2-Clause License**.

```
BSD 2-Clause License

Copyright (c) 2024, SoundSight Contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Pillow](https://pillow.readthedocs.io/) - Image processing
- [pydub](https://pydub.com/) - Audio manipulation
- [librosa](https://librosa.org/) - Music analysis
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [FFmpeg](https://ffmpeg.org/) - Audio conversion

---

<div align="center">

**Made with ❤️**

⭐ Star this repo if you find it useful!

[⬆ Back to top](#-audio-waveform-generator--music-analyzer)

</div>
