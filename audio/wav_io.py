"""Save and load WAV files using Python's built-in `wave` module."""

import wave
from pathlib import Path

import numpy as np

from audio.exceptions import WavFileError

SAMPLE_WIDTH_BYTES = 2  # int16 = 2 bytes per sample


def save_wav(audio: np.ndarray, path: str | Path, sample_rate: int) -> Path:
    """Save int16 audio to a WAV file. Returns the path it was saved to.

    audio shape: (frames,) for mono or (frames, channels).
    """
    if audio.dtype != np.int16:
        raise ValueError(f"Expected int16 audio, got {audio.dtype}")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    channels = 1 if audio.ndim == 1 else audio.shape[1]

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(SAMPLE_WIDTH_BYTES)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return path


def load_wav(path: str | Path) -> tuple[np.ndarray, int]:
    """Load a 16-bit WAV file. Returns (audio, sample_rate).

    audio shape is always (frames, channels).
    """
    path = Path(path)
    try:
        with wave.open(str(path), "rb") as wf:
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            sample_rate = wf.getframerate()
            raw = wf.readframes(wf.getnframes())
    except FileNotFoundError as exc:
        raise WavFileError(f"File not found: {path}") from exc
    except (wave.Error, EOFError) as exc:
        raise WavFileError(f"Not a valid WAV file: {path} ({exc})") from exc

    if width != SAMPLE_WIDTH_BYTES:
        raise WavFileError(f"Only 16-bit WAV is supported, this file is {width * 8}-bit")

    audio = np.frombuffer(raw, dtype=np.int16).reshape(-1, channels)
    return audio, sample_rate


def wav_info(path: str | Path) -> dict:
    """Return basic facts about a WAV file without loading all the audio."""
    try:
        with wave.open(str(path), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return {
                "channels": wf.getnchannels(),
                "sample_rate": rate,
                "bit_depth": wf.getsampwidth() * 8,
                "frames": frames,
                "duration_s": frames / rate if rate else 0.0,
                "size_kb": Path(path).stat().st_size / 1024,
            }
    except FileNotFoundError as exc:
        raise WavFileError(f"File not found: {path}") from exc
    except (wave.Error, EOFError) as exc:
        raise WavFileError(f"Not a valid WAV file: {path} ({exc})") from exc
