#!/usr/bin/env python3
"""
SoundSight - Audio Analyzer & Waveform Generator

A modern web application that generates beautiful waveform PNG images from MP3 files
and analyzes music to extract key, tempo, chords, and other musical information.

Features:
- Upload MP3 files and generate visual waveforms
- Detect musical key, tempo (BPM), and mode
- Estimate chord progressions
- Customizable colors, dimensions, and output options
- Support for mono and stereo channel visualization
- Transparent background support
- AJAX-based processing with progress indicator

Author: SoundSight Contributors
License: BSD-2-Clause
"""

import os
import struct
import tempfile
import hashlib
import time
import base64
import json
from io import BytesIO
from typing import Optional, Tuple, List, Dict, Any

from flask import Flask, request, send_file, render_template_string, jsonify
from PIL import Image, ImageDraw
from pydub import AudioSegment
import numpy as np

# Try to import librosa for music analysis
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

app = Flask(__name__)

# Configuration constants
DETAIL = 5  # How many bytes/frames to skip processing (higher = less detail, faster)
DEFAULT_WIDTH = 500
DEFAULT_HEIGHT = 100
DEFAULT_FOREGROUND = "#FF0000"
DEFAULT_BACKGROUND = "#FFFFFF"
GITHUB_URL = "https://github.com/MyOldRepositories/Keys-Notations-Scales-Chords-Mp3-php"

# Error message for missing FFmpeg
FFMPEG_NOT_FOUND_MSG = (
    "FFmpeg not found. Please install FFmpeg:\n"
    "  - Windows: choco install ffmpeg OR download from https://ffmpeg.org/download.html\n"
    "  - macOS: brew install ffmpeg\n"
    "  - Linux: sudo apt-get install ffmpeg\n"
    "After installation, ensure FFmpeg is in your system PATH."
)

# Musical key names
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Maximum upload size (10 MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


def html2rgb(html_color: str) -> Tuple[int, int, int]:
    color = html_color.lstrip('#')
    if len(color) != 6:
        raise ValueError(f"Invalid color format: {html_color}")
    return (
        int(color[0:2], 16),
        int(color[2:4], 16),
        int(color[4:6], 16)
    )


def find_values(byte1: int, byte2: int) -> int:
    return byte1 + (byte2 * 256)


def parse_wav_header(file_handle) -> dict:
    header = {}
    header['chunk_id'] = file_handle.read(4)
    header['chunk_size'] = struct.unpack('<I', file_handle.read(4))[0]
    header['format'] = file_handle.read(4)
    header['subchunk1_id'] = file_handle.read(4)
    header['subchunk1_size'] = struct.unpack('<I', file_handle.read(4))[0]
    header['audio_format'] = struct.unpack('<H', file_handle.read(2))[0]
    header['num_channels'] = struct.unpack('<H', file_handle.read(2))[0]
    header['sample_rate'] = struct.unpack('<I', file_handle.read(4))[0]
    header['byte_rate'] = struct.unpack('<I', file_handle.read(4))[0]
    header['block_align'] = struct.unpack('<H', file_handle.read(2))[0]
    header['bits_per_sample'] = struct.unpack('<H', file_handle.read(2))[0]
    header['subchunk2_id'] = file_handle.read(4)
    header['subchunk2_size'] = struct.unpack('<I', file_handle.read(4))[0]
    return header


def process_wav_file(filename: str, height: int, detail: int = DETAIL) -> List[int]:
    data_points = []
    with open(filename, 'rb') as handle:
        header = parse_wav_header(handle)
        bits_per_sample = header['bits_per_sample']
        byte_per_sample = bits_per_sample // 8
        num_channels = header['num_channels']
        ratio = 40 if num_channels == 2 else 80
        file_size = os.path.getsize(filename)
        data_size = (file_size - 44) // (ratio + byte_per_sample) + 1
        data_point = 0
        while data_point < data_size:
            try:
                if data_point % detail == 0:
                    bytes_data = handle.read(byte_per_sample)
                    if len(bytes_data) < byte_per_sample:
                        break
                    if byte_per_sample == 1:
                        data = bytes_data[0]
                    elif byte_per_sample == 2:
                        byte1 = bytes_data[0]
                        byte2 = bytes_data[1]
                        if byte2 & 128:
                            temp = 0
                        else:
                            temp = 128
                        temp = (byte2 & 127) + temp
                        data = find_values(byte1, temp) // 256
                    else:
                        data = 128
                    handle.seek(ratio, 1)
                    v = int(data / 255 * height)
                    data_points.append(v)
                else:
                    handle.seek(ratio + byte_per_sample, 1)
                data_point += 1
            except (IOError, struct.error):
                break
    return data_points


def generate_waveform_image(
    wav_files: List[str],
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    foreground: str = DEFAULT_FOREGROUND,
    background: str = DEFAULT_BACKGROUND,
    draw_flat: bool = False
) -> Image.Image:
    if height <= 0:
        raise ValueError("Height must be a positive integer")
    if width <= 0:
        raise ValueError("Width must be a positive integer")
    all_data_points = []
    for wav_file in wav_files:
        data_points = process_wav_file(wav_file, height, DETAIL)
        all_data_points.append(data_points)
    if not all_data_points or not all_data_points[0]:
        raise ValueError("No data points extracted from WAV files")
    original_width = len(all_data_points[0])
    total_height = height * len(wav_files)
    if not background:
        img = Image.new('RGBA', (original_width, total_height), (0, 0, 0, 0))
    else:
        bg_color = html2rgb(background)
        img = Image.new('RGB', (original_width, total_height), bg_color)
    draw = ImageDraw.Draw(img)
    if foreground:
        fg_color = html2rgb(foreground)
    else:
        fg_color = (255, 0, 0)
    for wav_idx, data_points in enumerate(all_data_points):
        y_offset = height * wav_idx
        for x, v in enumerate(data_points):
            if not (v / height == 0.5 and not draw_flat):
                y1 = y_offset + (height - v)
                y2 = y_offset + v
                if y1 > y2:
                    y1, y2 = y2, y1
                draw.line([(x, y1), (x, y2)], fill=fg_color)
    if width and width != original_width:
        final_height = height
        img = img.resize((width, final_height), Image.Resampling.LANCZOS)
    return img


def convert_mp3_to_wav(
    mp3_path: str,
    output_path: str,
    stereo: bool = False,
    channel: str = 'mono'
) -> str:
    try:
        audio = AudioSegment.from_mp3(mp3_path)
    except FileNotFoundError as e:
        raise RuntimeError(FFMPEG_NOT_FOUND_MSG) from e
    except Exception as e:
        if "ffmpeg" in str(e).lower() or "ffprobe" in str(e).lower():
            raise RuntimeError(FFMPEG_NOT_FOUND_MSG) from e
        raise
    audio = audio.set_frame_rate(8000)
    audio = audio.set_sample_width(2)
    if stereo and audio.channels == 2:
        channels = audio.split_to_mono()
        if channel == 'left':
            audio = channels[0]
        elif channel == 'right':
            audio = channels[1]
        else:
            audio = audio.set_channels(1)
    else:
        audio = audio.set_channels(1)
    audio.export(output_path, format='wav')
    return output_path


def analyze_music(mp3_path: str) -> Dict[str, Any]:
    analysis = {
        'key': 'Unknown',
        'mode': 'Unknown',
        'scale': 'Unknown',
        'tempo': 0,
        'time_signature': '4/4',
        'duration': 0,
        'energy': 'Medium',
        'possible_chords': [],
        'instrument_chords': {},
        'instruments': [],
        'genre_hints': [],
        'analysis_available': False
    }
    if not LIBROSA_AVAILABLE:
        analysis['error'] = 'Music analysis library not available'
        return analysis
    try:
        y, sr = librosa.load(mp3_path, sr=22050, mono=True)
        analysis['analysis_available'] = True
        analysis['duration'] = round(librosa.get_duration(y=y, sr=sr), 2)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if hasattr(tempo, '__iter__'):
            tempo = float(tempo[0]) if len(tempo) > 0 else 0
        analysis['tempo'] = round(float(tempo), 1)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        key_idx = int(np.argmax(chroma_mean))
        analysis['key'] = KEY_NAMES[key_idx]
        
        # Detect mode (Major/Minor) and scale type
        minor_third = chroma_mean[(key_idx + 3) % 12]
        major_third = chroma_mean[(key_idx + 4) % 12]
        
        # Scale intervals for mode detection (semitones from root)
        # Ionian (Major): 0, 2, 4, 5, 7, 9, 11
        # Dorian: 0, 2, 3, 5, 7, 9, 10
        # Phrygian: 0, 1, 3, 5, 7, 8, 10
        # Lydian: 0, 2, 4, 6, 7, 9, 11
        # Mixolydian: 0, 2, 4, 5, 7, 9, 10
        # Aeolian (Natural Minor): 0, 2, 3, 5, 7, 8, 10
        # Locrian: 0, 1, 3, 5, 6, 8, 10
        
        scale_templates = {
            'Ionian (Major)': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
            'Dorian': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
            'Phrygian': [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            'Lydian': [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            'Mixolydian': [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
            'Aeolian (Minor)': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
            'Locrian': [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
        }
        
        # Find best matching scale
        best_scale = 'Ionian (Major)'
        best_correlation = -1
        for scale_name, template in scale_templates.items():
            rotated = np.roll(template, key_idx)
            correlation = np.corrcoef(chroma_mean, rotated)[0, 1]
            if not np.isnan(correlation) and correlation > best_correlation:
                best_correlation = correlation
                best_scale = scale_name
        
        analysis['scale'] = best_scale
        
        # Set mode based on scale
        if 'Minor' in best_scale or best_scale in ['Dorian', 'Phrygian', 'Locrian']:
            analysis['mode'] = 'Minor'
        else:
            analysis['mode'] = 'Major'
        
        rms = librosa.feature.rms(y=y)[0]
        avg_rms = np.mean(rms)
        if avg_rms > 0.1:
            analysis['energy'] = 'High'
        elif avg_rms > 0.05:
            analysis['energy'] = 'Medium'
        else:
            analysis['energy'] = 'Low'
        chord_templates = {
            'Major': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
            'Minor': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
            '7th': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
        }
        possible_chords = []
        for key_i, key_name in enumerate(KEY_NAMES):
            for chord_type, template in chord_templates.items():
                rotated = np.roll(template, key_i)
                correlation = np.corrcoef(chroma_mean, rotated)[0, 1]
                if not np.isnan(correlation):
                    possible_chords.append((f"{key_name} {chord_type}", correlation))
        possible_chords.sort(key=lambda x: x[1], reverse=True)
        analysis['possible_chords'] = [c[0] for c in possible_chords[:4]]
        
        # Generate instrument-specific chord fingerings
        analysis['instrument_chords'] = generate_instrument_chords(analysis['possible_chords'])
        
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        zero_crossing = np.mean(librosa.feature.zero_crossing_rate(y))
        genre_hints = []
        if analysis['tempo'] > 120 and analysis['energy'] == 'High':
            genre_hints.append('Electronic/Dance')
        if analysis['tempo'] < 80 and analysis['energy'] == 'Low':
            genre_hints.append('Ballad/Slow')
        if zero_crossing > 0.1:
            genre_hints.append('Rock/Metal')
        if spectral_rolloff < 3000:
            genre_hints.append('Jazz/Blues')
        if not genre_hints:
            genre_hints.append('Pop/General')
        analysis['genre_hints'] = genre_hints[:3]
        instruments = []
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        if mfcc_mean[1] > 50:
            instruments.append('Vocals (likely)')
        if spectral_rolloff > 5000:
            instruments.append('Percussion')
        if spectral_rolloff < 2000 and analysis['energy'] == 'Low':
            instruments.append('Acoustic instruments')
        else:
            instruments.append('Mixed/Electronic')
        analysis['instruments'] = instruments[:3]
    except Exception as e:
        analysis['error'] = str(e)
    return analysis


def generate_instrument_chords(chords: List[str]) -> Dict[str, Dict[str, str]]:
    """Generate chord fingerings for different instruments."""
    # Guitar chord fingerings (standard tuning, fret positions)
    guitar_chords = {
        'C Major': 'x32010', 'C Minor': 'x35543', 'C 7th': 'x32310',
        'C# Major': 'x46664', 'C# Minor': 'x46654', 'C# 7th': 'x4342x',
        'D Major': 'xx0232', 'D Minor': 'xx0231', 'D 7th': 'xx0212',
        'D# Major': 'xx1343', 'D# Minor': 'xx1342', 'D# 7th': 'xx1323',
        'E Major': '022100', 'E Minor': '022000', 'E 7th': '020100',
        'F Major': '133211', 'F Minor': '133111', 'F 7th': '131211',
        'F# Major': '244322', 'F# Minor': '244222', 'F# 7th': '242322',
        'G Major': '320003', 'G Minor': '355333', 'G 7th': '320001',
        'G# Major': '466544', 'G# Minor': '466444', 'G# 7th': '464544',
        'A Major': 'x02220', 'A Minor': 'x02210', 'A 7th': 'x02020',
        'A# Major': 'x13331', 'A# Minor': 'x13321', 'A# 7th': 'x13131',
        'B Major': 'x24442', 'B Minor': 'x24432', 'B 7th': 'x21202',
    }
    
    # Piano chord notes
    piano_chords = {
        'C Major': 'C-E-G', 'C Minor': 'C-Eb-G', 'C 7th': 'C-E-G-Bb',
        'C# Major': 'C#-F-G#', 'C# Minor': 'C#-E-G#', 'C# 7th': 'C#-F-G#-B',
        'D Major': 'D-F#-A', 'D Minor': 'D-F-A', 'D 7th': 'D-F#-A-C',
        'D# Major': 'D#-G-A#', 'D# Minor': 'D#-F#-A#', 'D# 7th': 'D#-G-A#-C#',
        'E Major': 'E-G#-B', 'E Minor': 'E-G-B', 'E 7th': 'E-G#-B-D',
        'F Major': 'F-A-C', 'F Minor': 'F-Ab-C', 'F 7th': 'F-A-C-Eb',
        'F# Major': 'F#-A#-C#', 'F# Minor': 'F#-A-C#', 'F# 7th': 'F#-A#-C#-E',
        'G Major': 'G-B-D', 'G Minor': 'G-Bb-D', 'G 7th': 'G-B-D-F',
        'G# Major': 'G#-C-D#', 'G# Minor': 'G#-B-D#', 'G# 7th': 'G#-C-D#-F#',
        'A Major': 'A-C#-E', 'A Minor': 'A-C-E', 'A 7th': 'A-C#-E-G',
        'A# Major': 'A#-D-F', 'A# Minor': 'A#-C#-F', 'A# 7th': 'A#-D-F-G#',
        'B Major': 'B-D#-F#', 'B Minor': 'B-D-F#', 'B 7th': 'B-D#-F#-A',
    }
    
    # Ukulele chord fingerings (GCEA tuning)
    ukulele_chords = {
        'C Major': '0003', 'C Minor': '0333', 'C 7th': '0001',
        'C# Major': '1114', 'C# Minor': '1444', 'C# 7th': '1112',
        'D Major': '2220', 'D Minor': '2210', 'D 7th': '2223',
        'D# Major': '3331', 'D# Minor': '3321', 'D# 7th': '3334',
        'E Major': '4442', 'E Minor': '4432', 'E 7th': '1202',
        'F Major': '2010', 'F Minor': '1013', 'F 7th': '2310',
        'F# Major': '3121', 'F# Minor': '2124', 'F# 7th': '3424',
        'G Major': '0232', 'G Minor': '0231', 'G 7th': '0212',
        'G# Major': '5343', 'G# Minor': '1342', 'G# 7th': '1323',
        'A Major': '2100', 'A Minor': '2000', 'A 7th': '0100',
        'A# Major': '3211', 'A# Minor': '3111', 'A# 7th': '1211',
        'B Major': '4322', 'B Minor': '4222', 'B 7th': '2322',
    }
    
    result = {
        'guitar': {},
        'piano': {},
        'ukulele': {}
    }
    
    for chord in chords:
        if chord in guitar_chords:
            result['guitar'][chord] = guitar_chords[chord]
        if chord in piano_chords:
            result['piano'][chord] = piano_chords[chord]
        if chord in ukulele_chords:
            result['ukulele'][chord] = ukulele_chords[chord]
    
    return result


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SoundSight - Audio Analyzer & Waveform Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #ffffff;
        }
        .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
        header { text-align: center; margin-bottom: 40px; }
        .logo { font-size: 3rem; margin-bottom: 10px; }
        h1 {
            font-size: 2.5rem; font-weight: 700; margin-bottom: 15px;
            background: linear-gradient(90deg, #e94560, #ff6b6b);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .tagline { font-size: 1.1rem; color: #a0a0a0; font-weight: 300; }
        .card {
            background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
            border-radius: 20px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); margin-bottom: 30px;
        }
        .form-group { margin-bottom: 25px; }
        label { display: block; font-weight: 500; margin-bottom: 8px; color: #e0e0e0; }
        .label-hint { font-size: 0.85rem; color: #888; font-weight: 300; margin-left: 8px; }
        input[type="text"], input[type="file"] {
            width: 100%; padding: 14px 18px; border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px; background: rgba(255, 255, 255, 0.05); color: #ffffff;
            font-size: 1rem; transition: all 0.3s ease;
        }
        input[type="text"]:focus, input[type="file"]:focus {
            outline: none; border-color: #e94560; background: rgba(255, 255, 255, 0.08);
        }
        input[type="file"] { cursor: pointer; }
        input[type="file"]::file-selector-button {
            padding: 10px 20px; border: none; border-radius: 8px;
            background: linear-gradient(90deg, #e94560, #ff6b6b); color: white;
            font-weight: 500; cursor: pointer; margin-right: 15px; transition: transform 0.2s ease;
        }
        input[type="file"]::file-selector-button:hover { transform: scale(1.02); }
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 600px) { .row { grid-template-columns: 1fr; } }
        .checkbox-group {
            display: flex; align-items: center; gap: 12px; padding: 15px;
            background: rgba(255, 255, 255, 0.03); border-radius: 12px;
            cursor: pointer; transition: background 0.3s ease;
        }
        .checkbox-group:hover { background: rgba(255, 255, 255, 0.06); }
        input[type="checkbox"] { width: 22px; height: 22px; accent-color: #e94560; cursor: pointer; }
        .checkbox-label { font-weight: 400; color: #d0d0d0; }
        .submit-btn {
            width: 100%; padding: 18px 30px; border: none; border-radius: 12px;
            background: linear-gradient(90deg, #e94560, #ff6b6b); color: white;
            font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease;
            margin-top: 20px; text-transform: uppercase; letter-spacing: 1px;
        }
        .submit-btn:hover:not(:disabled) {
            transform: translateY(-2px); box-shadow: 0 15px 30px -5px rgba(233, 69, 96, 0.4);
        }
        .submit-btn:disabled { opacity: 0.7; cursor: not-allowed; }
        .progress-container { display: none; margin-top: 30px; }
        .progress-container.active { display: block; }
        .progress-bar {
            width: 100%; height: 8px; background: rgba(255, 255, 255, 0.1);
            border-radius: 10px; overflow: hidden; margin-bottom: 15px;
        }
        .progress-fill {
            height: 100%; background: linear-gradient(90deg, #e94560, #ff6b6b);
            border-radius: 10px; width: 0%; transition: width 0.3s ease;
            animation: pulse 1.5s ease-in-out infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        .progress-text { text-align: center; color: #a0a0a0; font-size: 0.95rem; }
        .progress-text .step { color: #e94560; font-weight: 600; }
        .results-container { display: none; }
        .results-container.active { display: block; animation: fadeIn 0.5s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .result-header {
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 25px; flex-wrap: wrap; gap: 15px;
        }
        .result-title { font-size: 1.5rem; font-weight: 600; color: #e94560; }
        .new-upload-btn {
            padding: 10px 25px; border: 2px solid #e94560; border-radius: 8px;
            background: transparent; color: #e94560; font-weight: 500;
            cursor: pointer; transition: all 0.3s ease;
        }
        .new-upload-btn:hover { background: #e94560; color: white; }
        .waveform-display {
            background: rgba(0, 0, 0, 0.3); border-radius: 15px;
            padding: 25px; margin-bottom: 25px; text-align: center;
        }
        .waveform-image {
            max-width: 100%; height: auto; border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        .download-btn {
            display: inline-block; margin-top: 20px; padding: 12px 30px;
            background: linear-gradient(90deg, #e94560, #ff6b6b); color: white;
            text-decoration: none; border-radius: 8px; font-weight: 500; transition: transform 0.2s ease;
        }
        .download-btn:hover { transform: scale(1.05); }
        .analysis-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin-top: 25px;
        }
        .analysis-card {
            background: rgba(255, 255, 255, 0.05); border-radius: 15px;
            padding: 20px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .analysis-icon { font-size: 2rem; margin-bottom: 10px; }
        .analysis-label {
            font-size: 0.85rem; color: #888; margin-bottom: 5px;
            text-transform: uppercase; letter-spacing: 1px;
        }
        .analysis-value { font-size: 1.4rem; font-weight: 600; color: #fff; }
        .analysis-value.highlight { color: #e94560; }
        .chord-list, .genre-list, .instrument-list {
            display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 10px;
        }
        .chord-tag, .genre-tag, .instrument-tag {
            background: rgba(233, 69, 96, 0.2); color: #e94560;
            padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 500;
        }
        .genre-tag { background: rgba(100, 200, 100, 0.2); color: #64c864; }
        .instrument-tag { background: rgba(100, 150, 255, 0.2); color: #6496ff; }
        .features {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-top: 30px;
        }
        .feature {
            background: rgba(255, 255, 255, 0.03); padding: 25px; border-radius: 15px;
            text-align: center; border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .feature-icon { font-size: 2.5rem; margin-bottom: 15px; }
        .feature h3 { font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; color: #e94560; }
        .feature p { font-size: 0.9rem; color: #888; line-height: 1.5; }
        footer { text-align: center; margin-top: 50px; padding: 20px; color: #666; font-size: 0.9rem; }
        footer a { color: #e94560; text-decoration: none; }
        footer a:hover { text-decoration: underline; }
        .error-message {
            background: rgba(233, 69, 96, 0.2); border: 1px solid #e94560;
            border-radius: 12px; padding: 20px; margin-top: 20px; color: #ff8a8a;
        }
        .error-message h3 { color: #e94560; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">🎵</div>
            <h1>SoundSight</h1>
            <p class="tagline">Analyze your music • Extract key, tempo & chords • Generate stunning waveforms</p>
        </header>
        <div class="card" id="uploadCard">
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Select MP3 File</label>
                    <input type="file" name="mp3" id="mp3File" accept=".mp3" required />
                </div>
                <div class="row">
                    <div class="form-group">
                        <label>Image Width <span class="label-hint">(pixels)</span></label>
                        <input type="text" name="width" id="width" value="{{ default_width }}" />
                    </div>
                    <div class="form-group">
                        <label>Image Height <span class="label-hint">(pixels)</span></label>
                        <input type="text" name="height" id="height" value="{{ default_height }}" />
                    </div>
                </div>
                <div class="row">
                    <div class="form-group">
                        <label>Waveform Color <span class="label-hint">(HEX)</span></label>
                        <input type="text" name="foreground" id="foreground" value="{{ default_foreground }}" />
                    </div>
                    <div class="form-group">
                        <label>Background Color <span class="label-hint">(blank=transparent)</span></label>
                        <input type="text" name="background" id="background" value="{{ default_background }}" />
                    </div>
                </div>
                <div class="row">
                    <label class="checkbox-group">
                        <input type="checkbox" name="flat" id="flat" />
                        <span class="checkbox-label">Draw flat-line sections</span>
                    </label>
                    <label class="checkbox-group">
                        <input type="checkbox" name="stereo" id="stereo" />
                        <span class="checkbox-label">Stereo waveform (L/R channels)</span>
                    </label>
                </div>
                <div class="row">
                    <label class="checkbox-group">
                        <input type="checkbox" name="analyze" id="analyze" checked />
                        <span class="checkbox-label">🎼 Analyze music (key, tempo, chords)</span>
                    </label>
                </div>
                <button type="submit" class="submit-btn" id="submitBtn">✨ Generate Waveform</button>
                <div class="progress-container" id="progressContainer">
                    <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
                    <div class="progress-text"><span class="step" id="progressStep">Uploading...</span></div>
                </div>
            </form>
        </div>
        <div class="results-container" id="resultsContainer">
            <div class="card">
                <div class="result-header">
                    <h2 class="result-title">🎉 Your Waveform is Ready!</h2>
                    <button class="new-upload-btn" onclick="resetForm()">↺ New Upload</button>
                </div>
                <div class="waveform-display">
                    <img id="waveformImage" class="waveform-image" src="" alt="Generated Waveform" />
                    <br>
                    <a id="downloadLink" class="download-btn" href="" download="waveform.png">⬇️ Download PNG</a>
                </div>
                <div id="analysisSection">
                    <h3 style="color: #e94560; margin-bottom: 20px; font-size: 1.3rem;">🎼 Music Analysis</h3>
                    <div class="analysis-grid" id="analysisGrid"></div>
                </div>
            </div>
        </div>
        <div class="features" id="featuresSection">
            <div class="feature"><div class="feature-icon">🎨</div><h3>Custom Colors</h3><p>Choose any color for your waveform and background</p></div>
            <div class="feature"><div class="feature-icon">🎹</div><h3>Music Analysis</h3><p>Detect key, tempo, chords, and musical characteristics</p></div>
            <div class="feature"><div class="feature-icon">🎧</div><h3>Stereo Support</h3><p>Visualize left and right audio channels separately</p></div>
            <div class="feature"><div class="feature-icon">⚡</div><h3>Fast Processing</h3><p>Optimized algorithms with real-time progress tracking</p></div>
            <div class="feature"><div class="feature-icon">🐳</div><h3>Docker Ready</h3><p>Deploy instantly with our production-ready Docker setup</p></div>
            <div class="feature"><div class="feature-icon">🖼️</div><h3>Transparent PNG</h3><p>Export with transparent backgrounds for easy integration</p></div>
        </div>
        <footer><p>Open source project • <a href="{{ github_url }}">View on GitHub</a></p></footer>
    </div>
    <script>
        const form = document.getElementById('uploadForm');
        const submitBtn = document.getElementById('submitBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressStep = document.getElementById('progressStep');
        const resultsContainer = document.getElementById('resultsContainer');
        const uploadCard = document.getElementById('uploadCard');
        const featuresSection = document.getElementById('featuresSection');
        const steps = [
            { text: 'Uploading file...', progress: 15 },
            { text: 'Converting audio...', progress: 35 },
            { text: 'Generating waveform...', progress: 55 },
            { text: 'Analyzing music...', progress: 75 },
            { text: 'Finalizing...', progress: 90 }
        ];
        let stepIndex = 0;
        let stepInterval = null;
        function startProgress() {
            progressContainer.classList.add('active');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            stepIndex = 0;
            updateStep();
            stepInterval = setInterval(() => {
                if (stepIndex < steps.length - 1) { stepIndex++; updateStep(); }
            }, 1500);
        }
        function updateStep() {
            progressFill.style.width = steps[stepIndex].progress + '%';
            progressStep.textContent = steps[stepIndex].text;
        }
        function stopProgress() {
            clearInterval(stepInterval);
            progressFill.style.width = '100%';
            progressStep.textContent = 'Complete!';
        }
        function showResults(data) {
            stopProgress();
            setTimeout(() => {
                uploadCard.style.display = 'none';
                featuresSection.style.display = 'none';
                resultsContainer.classList.add('active');
                document.getElementById('waveformImage').src = 'data:image/png;base64,' + data.waveform;
                document.getElementById('downloadLink').href = 'data:image/png;base64,' + data.waveform;
                if (data.analysis && data.analysis.analysis_available) {
                    displayAnalysis(data.analysis);
                    document.getElementById('analysisSection').style.display = 'block';
                } else {
                    document.getElementById('analysisSection').style.display = 'none';
                }
            }, 500);
        }
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        let currentInstrumentChords = {};
        function displayAnalysis(analysis) {
            const grid = document.getElementById('analysisGrid');
            currentInstrumentChords = analysis.instrument_chords || {};
            let html = '<div class="analysis-card"><div class="analysis-icon">🎵</div><div class="analysis-label">Musical Key</div><div class="analysis-value highlight">' + escapeHtml(analysis.key) + ' ' + escapeHtml(analysis.mode) + '</div></div>';
            html += '<div class="analysis-card"><div class="analysis-icon">🎼</div><div class="analysis-label">Scale/Mode</div><div class="analysis-value">' + escapeHtml(analysis.scale || 'Unknown') + '</div></div>';
            html += '<div class="analysis-card"><div class="analysis-icon">🥁</div><div class="analysis-label">Tempo</div><div class="analysis-value">' + escapeHtml(String(analysis.tempo)) + ' BPM</div></div>';
            html += '<div class="analysis-card"><div class="analysis-icon">⚡</div><div class="analysis-label">Energy</div><div class="analysis-value">' + escapeHtml(analysis.energy) + '</div></div>';
            html += '<div class="analysis-card"><div class="analysis-icon">⏱️</div><div class="analysis-label">Duration</div><div class="analysis-value">' + escapeHtml(formatDuration(analysis.duration)) + '</div></div>';
            if (analysis.possible_chords && analysis.possible_chords.length > 0) {
                html += '<div class="analysis-card" style="grid-column: span 2;"><div class="analysis-icon">🎹</div><div class="analysis-label">Possible Chords</div><div class="chord-list">';
                analysis.possible_chords.forEach(c => { html += '<span class="chord-tag">' + escapeHtml(c) + '</span>'; });
                html += '</div></div>';
            }
            if (analysis.instrument_chords && Object.keys(analysis.instrument_chords).length > 0) {
                html += '<div class="analysis-card" style="grid-column: span 2;"><div class="analysis-icon">🎸</div><div class="analysis-label">Instrument Chords</div>';
                html += '<div style="margin-top:10px;"><select id="instrumentSelect" onchange="showInstrumentChords()" style="padding:8px 15px;border-radius:8px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);color:#fff;font-size:0.9rem;cursor:pointer;">';
                html += '<option value="guitar">🎸 Guitar</option>';
                html += '<option value="piano">🎹 Piano</option>';
                html += '<option value="ukulele">🪕 Ukulele</option>';
                html += '</select></div>';
                html += '<div id="instrumentChordDisplay" style="margin-top:15px;"></div>';
                html += '</div>';
            }
            if (analysis.genre_hints && analysis.genre_hints.length > 0) {
                html += '<div class="analysis-card"><div class="analysis-icon">🎭</div><div class="analysis-label">Genre Hints</div><div class="genre-list">';
                analysis.genre_hints.forEach(g => { html += '<span class="genre-tag">' + escapeHtml(g) + '</span>'; });
                html += '</div></div>';
            }
            if (analysis.instruments && analysis.instruments.length > 0) {
                html += '<div class="analysis-card"><div class="analysis-icon">🎻</div><div class="analysis-label">Detected Instruments</div><div class="instrument-list">';
                analysis.instruments.forEach(i => { html += '<span class="instrument-tag">' + escapeHtml(i) + '</span>'; });
                html += '</div></div>';
            }
            grid.innerHTML = html;
            setTimeout(() => showInstrumentChords(), 100);
        }
        function showInstrumentChords() {
            const select = document.getElementById('instrumentSelect');
            const display = document.getElementById('instrumentChordDisplay');
            if (!select || !display) return;
            const instrument = select.value;
            const chords = currentInstrumentChords[instrument] || {};
            if (Object.keys(chords).length === 0) {
                display.innerHTML = '<p style="color:#888;font-size:0.9rem;">No chord data available for this instrument.</p>';
                return;
            }
            let html = '<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;">';
            for (const [chord, fingering] of Object.entries(chords)) {
                html += '<div style="background:rgba(233,69,96,0.15);padding:10px 15px;border-radius:10px;text-align:center;">';
                html += '<div style="font-weight:600;color:#e94560;margin-bottom:5px;">' + escapeHtml(chord) + '</div>';
                html += '<div style="font-family:monospace;font-size:0.85rem;color:#ccc;">' + escapeHtml(fingering) + '</div>';
                html += '</div>';
            }
            html += '</div>';
            display.innerHTML = html;
        }
        function formatDuration(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return mins + ':' + secs.toString().padStart(2, '0');
        }
        function showError(message) {
            stopProgress();
            progressContainer.classList.remove('active');
            submitBtn.disabled = false;
            submitBtn.textContent = '✨ Generate Waveform';
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.innerHTML = '<h3>⚠️ Error</h3><p>' + escapeHtml(message) + '</p>';
            const existingError = uploadCard.querySelector('.error-message');
            if (existingError) existingError.remove();
            uploadCard.querySelector('form').appendChild(errorDiv);
            setTimeout(() => errorDiv.remove(), 10000);
        }
        function resetForm() {
            resultsContainer.classList.remove('active');
            uploadCard.style.display = 'block';
            featuresSection.style.display = 'grid';
            progressContainer.classList.remove('active');
            submitBtn.disabled = false;
            submitBtn.textContent = '✨ Generate Waveform';
            form.reset();
            document.getElementById('width').value = '{{ default_width }}';
            document.getElementById('height').value = '{{ default_height }}';
            document.getElementById('foreground').value = '{{ default_foreground }}';
            document.getElementById('background').value = '{{ default_background }}';
            document.getElementById('analyze').checked = true;
        }
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('mp3File');
            if (!fileInput.files[0]) { showError('Please select an MP3 file'); return; }
            startProgress();
            const formData = new FormData();
            formData.append('mp3', fileInput.files[0]);
            formData.append('width', document.getElementById('width').value);
            formData.append('height', document.getElementById('height').value);
            formData.append('foreground', document.getElementById('foreground').value);
            formData.append('background', document.getElementById('background').value);
            formData.append('flat', document.getElementById('flat').checked ? 'on' : '');
            formData.append('stereo', document.getElementById('stereo').checked ? 'on' : '');
            formData.append('analyze', document.getElementById('analyze').checked ? 'on' : '');
            try {
                const response = await fetch('/api/generate', { method: 'POST', body: formData });
                const data = await response.json();
                if (data.success) { showResults(data); } else { showError(data.error || 'An error occurred'); }
            } catch (error) { showError('Network error. Please try again.'); }
        });
    </script>
</body>
</html>
'''


@app.route('/', methods=['GET'])
def index():
    return render_template_string(
        HTML_TEMPLATE,
        default_width=DEFAULT_WIDTH,
        default_height=DEFAULT_HEIGHT,
        default_foreground=DEFAULT_FOREGROUND,
        default_background=DEFAULT_BACKGROUND,
        github_url=GITHUB_URL
    )


@app.route('/api/generate', methods=['POST'])
def api_generate():
    if 'mp3' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    mp3_file = request.files['mp3']
    if mp3_file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    if not mp3_file.filename.lower().endswith('.mp3'):
        return jsonify({'success': False, 'error': 'Please upload an MP3 file'})
    try:
        width = int(request.form.get('width', DEFAULT_WIDTH))
        if width <= 0:
            width = DEFAULT_WIDTH
    except ValueError:
        width = DEFAULT_WIDTH
    try:
        height = int(request.form.get('height', DEFAULT_HEIGHT))
        if height <= 0:
            height = DEFAULT_HEIGHT
    except ValueError:
        height = DEFAULT_HEIGHT
    foreground = request.form.get('foreground', DEFAULT_FOREGROUND)
    background = request.form.get('background', DEFAULT_BACKGROUND)
    draw_flat = request.form.get('flat') == 'on'
    stereo = request.form.get('stereo') == 'on'
    do_analysis = request.form.get('analyze') == 'on'
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmpname = hashlib.md5(str(time.time()).encode()).hexdigest()[:10]
        mp3_path = os.path.join(tmp_dir, f"{tmpname}_o.mp3")
        mp3_file.save(mp3_path)
        wavs_to_process = []
        try:
            if stereo:
                wav_left = os.path.join(tmp_dir, f"{tmpname}_l.wav")
                wav_right = os.path.join(tmp_dir, f"{tmpname}_r.wav")
                convert_mp3_to_wav(mp3_path, wav_left, stereo=True, channel='left')
                convert_mp3_to_wav(mp3_path, wav_right, stereo=True, channel='right')
                wavs_to_process = [wav_left, wav_right]
            else:
                wav_path = os.path.join(tmp_dir, f"{tmpname}.wav")
                convert_mp3_to_wav(mp3_path, wav_path, stereo=False)
                wavs_to_process = [wav_path]
            img = generate_waveform_image(
                wavs_to_process, width=width, height=height,
                foreground=foreground if foreground else DEFAULT_FOREGROUND,
                background=background, draw_flat=draw_flat
            )
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
            analysis = {}
            if do_analysis:
                analysis = analyze_music(mp3_path)
            return jsonify({'success': True, 'waveform': img_base64, 'analysis': analysis})
        except RuntimeError as e:
            return jsonify({'success': False, 'error': 'FFmpeg not found. Please install FFmpeg to process audio files.'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
