"""Play audio through the speakers."""

from pathlib import Path

import numpy as np

import config
from audio.devices import require_sounddevice
from audio.exceptions import DeviceError
from audio.wav_io import load_wav


def play(audio: np.ndarray, sample_rate: int, device=config.OUTPUT_DEVICE) -> None:
    """Play audio and wait until it finishes."""
    sd = require_sounddevice()
    try:
        sd.play(audio, samplerate=sample_rate, device=device)
        sd.wait()
    except (sd.PortAudioError, ValueError) as exc:
        raise DeviceError(f"Could not play on device {device!r}: {exc}") from exc


def play_wav(path: str | Path, device=config.OUTPUT_DEVICE) -> None:
    """Load a WAV file and play it."""
    audio, sample_rate = load_wav(path)
    play(audio, sample_rate, device)


def make_tone(freq_hz: float = 440.0, seconds: float = 1.0,
              sample_rate: int = config.SAMPLE_RATE, volume: float = 0.3) -> np.ndarray:
    """Create a sine-wave beep as int16 audio. Good for testing speakers without a mic."""
    t = np.arange(int(seconds * sample_rate)) / sample_rate
    wave = volume * np.sin(2 * np.pi * freq_hz * t)
    # Short fade in/out to avoid "click" sounds at the start and end.
    fade = min(int(0.01 * sample_rate), len(wave) // 2)
    if fade:
        ramp = np.linspace(0, 1, fade)
        wave[:fade] *= ramp
        wave[-fade:] *= ramp[::-1]
    return (wave * 32767).astype(np.int16)
