"""
Audio utilities for Thomas Demo
Validation, format conversion and preprocessing of uploaded audio files
Supported formats: wav, mp3, mp4, m4a, ogg, flac, aac
"""

import os
import subprocess
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from datetime import datetime
import config

SUPPORTED_FORMATS = [".wav", ".mp3", ".mp4", ".m4a", ".ogg", ".flac", ".aac", ".mpeg", ".mpga"]


def convert_to_wav(input_path: str, output_path: str) -> bool:
    """Convert any audio format to 16kHz mono WAV using ffmpeg."""
    try:
        result = subprocess.run([
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-sample_fmt", "s16",
            output_path
        ], capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except Exception:
        return False


def validate_and_save(uploaded_file, upload_dir: str) -> tuple[bool, any]:
    """
    Validate uploaded audio file, convert to WAV if needed, and save it.

    Returns:
        (True, dict) on success
        (False, str) error message on failure
    """
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        return False, f"Unsupported format. Supported: {', '.join(SUPPORTED_FORMATS)}"

    # Save original upload to temp
    temp_path = os.path.join(upload_dir, f"temp_{uploaded_file.name}")
    try:
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    except Exception as e:
        return False, f"Could not write file: {str(e)}"

    try:
        # Convert to WAV if not already
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in uploaded_file.name)
        wav_name = f"{timestamp}_{Path(safe_name).stem}.wav"
        wav_path = os.path.join(upload_dir, wav_name)

        if suffix != ".wav":
            success = convert_to_wav(temp_path, wav_path)
            os.remove(temp_path)
            if not success:
                return False, "Could not convert file to WAV. Make sure ffmpeg is installed."
        else:
            os.rename(temp_path, wav_path)

        # Load and validate
        audio, sr = librosa.load(wav_path, sr=None, mono=True)
        duration = librosa.get_duration(y=audio, sr=sr)
        file_size = os.path.getsize(wav_path)

        if duration < config.MIN_DURATION:
            os.remove(wav_path)
            return False, f"Audio too short (minimum {config.MIN_DURATION}s, uploaded: {duration:.1f}s)"

        if duration > config.MAX_DURATION:
            os.remove(wav_path)
            return False, f"Audio too long (maximum {config.MAX_DURATION}s, uploaded: {duration:.1f}s)"

        if sr < config.MIN_SAMPLE_RATE:
            os.remove(wav_path)
            return False, f"Sample rate too low (minimum {config.MIN_SAMPLE_RATE}Hz, uploaded: {sr}Hz)"

        return True, {
            "path": wav_path,
            "filename": wav_name,
            "original_filename": uploaded_file.name,
            "duration": round(duration, 2),
            "sample_rate": sr,
            "file_size": file_size,
            "channels": 1
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False, f"Could not read audio file: {str(e)}"


def get_waveform_data(audio_path: str, num_points: int = 200) -> list[float]:
    try:
        audio, sr = librosa.load(audio_path, sr=None, mono=True)
        chunk_size = max(1, len(audio) // num_points)
        waveform = [
            float(np.abs(audio[i:i + chunk_size]).mean())
            for i in range(0, len(audio) - chunk_size, chunk_size)
        ]
        max_val = max(waveform) if waveform else 1
        if max_val > 0:
            waveform = [v / max_val for v in waveform]
        return waveform[:num_points]
    except Exception:
        return [0.0] * num_points


def format_duration(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


def format_file_size(bytes_size: int) -> str:
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"