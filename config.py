"""Project settings. Change values here instead of inside the code."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"

# --- Audio format ---
# Whisper (Week 2) expects 16 kHz mono audio, so we record in that format from day one.
SAMPLE_RATE = 16000   # samples per second (Hz)
CHANNELS = 1          # 1 = mono, 2 = stereo
DTYPE = "int16"       # 16-bit samples, the standard for WAV files

# --- Recording ---
RECORD_SECONDS = 5

# --- Devices ---
# None = use the system default. You can also use a device number (e.g. 3)
# or part of a device name (e.g. "USB"). Run mic_tester.py -> option 1 to see them.
INPUT_DEVICE = None
OUTPUT_DEVICE = None

# --- Level checks (in dBFS: 0 is the loudest possible, lower numbers are quieter) ---
TOO_QUIET_DBFS = -40.0
