"""Record audio from the microphone."""

import math
import time

import numpy as np

import config
from audio.devices import require_sounddevice
from audio.exceptions import DeviceError
from audio.levels import level_bar, rms_dbfs


def record(
    seconds: float = config.RECORD_SECONDS,
    sample_rate: int = config.SAMPLE_RATE,
    channels: int = config.CHANNELS,
    device=config.INPUT_DEVICE,
) -> np.ndarray:
    """Record a fixed number of seconds. Returns int16 audio of shape (frames, channels)."""
    if seconds <= 0:
        raise ValueError("seconds must be greater than 0")

    sd = require_sounddevice()
    frames = int(seconds * sample_rate)
    try:
        # Check first, so we get a clear error if the mic does not support these settings.
        sd.check_input_settings(device=device, samplerate=sample_rate,
                                channels=channels, dtype=config.DTYPE)
        audio = sd.rec(frames, samplerate=sample_rate, channels=channels,
                       dtype=config.DTYPE, device=device)
        sd.wait()  # block until recording is finished
    except (sd.PortAudioError, ValueError) as exc:
        raise DeviceError(f"Could not record from device {device!r}: {exc}") from exc
    return audio


def monitor_levels(
    seconds: float = 10,
    sample_rate: int = config.SAMPLE_RATE,
    device=config.INPUT_DEVICE,
) -> float:
    """Show a live loudness bar for the mic. Returns the loudest level seen (dBFS).

    Uses a stream with a callback: sounddevice calls `callback` many times per second
    with a small block of new audio. We only store the level there (callbacks must be fast)
    and print it from the main loop.
    """
    sd = require_sounddevice()
    state = {"db": -math.inf, "max_db": -math.inf, "problems": 0}

    def callback(indata, frames, time_info, status):
        if status:  # e.g. input overflow = we were too slow to read audio
            state["problems"] += 1
        db = rms_dbfs(indata)
        state["db"] = db
        state["max_db"] = max(state["max_db"], db)

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype=config.DTYPE,
                            device=device, callback=callback):
            end = time.monotonic() + seconds
            while time.monotonic() < end:
                print("\r" + level_bar(state["db"]), end="", flush=True)
                time.sleep(0.05)
    except (sd.PortAudioError, ValueError) as exc:
        raise DeviceError(f"Could not open mic {device!r}: {exc}") from exc
    finally:
        print()

    if state["problems"]:
        print(f"Note: {state['problems']} stream warnings (audio blocks were dropped).")
    return state["max_db"]
