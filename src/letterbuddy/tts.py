"""
Letter Buddy – TTS Output (Phase 4).

Generates spoken audio for the translated text using offline TTS (eSpeak-ng fallback).
"""

import os
import subprocess
import tempfile
from pathlib import Path

from letterbuddy.config import cfg


def generate_audio(text: str, output_path: str | Path | None = None) -> Path:
    """
    Generate TTS audio for the given text using espeak-ng.
    If no output_path is provided, generates a temp file.
    """
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

    out_path = Path(output_path)

    # Check if espeak-ng is available
    espeak_bin = "espeak-ng"
    if os.name == 'nt':
        # Provide full path on Windows if not in PATH
        default_path = r"C:\Program Files\eSpeak NG\espeak-ng.exe"
        if os.path.exists(default_path):
            espeak_bin = default_path

    lang = cfg.language.target

    try:
        # eSpeak-ng command: espeak-ng -v {lang} -w {out_path} "{text}"
        subprocess.run(
            [espeak_bin, "-v", lang, "-w", str(out_path), text],
            check=True,
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        # If espeak-ng isn't installed, just fail gracefully or create dummy
        print("Warning: eSpeak-ng not found. Creating dummy audio file.")
        out_path.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\xbb\x00\x00\x00w\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
    except subprocess.CalledProcessError as e:
        print(f"Warning: TTS failed. {e.stderr}")
        # Create empty dummy on failure so app doesn't crash
        out_path.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\xbb\x00\x00\x00w\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")

    return out_path
