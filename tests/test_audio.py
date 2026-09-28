"""Tests that work without a microphone. Run: python -m pytest"""

import math

import numpy as np
import pytest

from audio.exceptions import WavFileError
from audio.levels import audio_stats, level_bar, rms_dbfs
from audio.player import make_tone
from audio.wav_io import load_wav, save_wav, wav_info


def test_wav_round_trip(tmp_path):
    audio = make_tone(seconds=0.5, sample_rate=16000)
    path = save_wav(audio, tmp_path / "tone.wav", 16000)

    loaded, rate = load_wav(path)
    assert rate == 16000
    assert loaded.shape == (8000, 1)
    assert np.array_equal(loaded[:, 0], audio)


def test_wav_info(tmp_path):
    audio = np.zeros((16000, 2), dtype=np.int16)  # 1 s of stereo silence
    path = save_wav(audio, tmp_path / "stereo.wav", 16000)
    info = wav_info(path)
    assert info["channels"] == 2
    assert info["bit_depth"] == 16
    assert info["duration_s"] == pytest.approx(1.0)


def test_save_rejects_float_audio(tmp_path):
    with pytest.raises(ValueError):
        save_wav(np.zeros(100, dtype=np.float32), tmp_path / "x.wav", 16000)


def test_missing_and_broken_files(tmp_path):
    with pytest.raises(WavFileError):
        load_wav(tmp_path / "does_not_exist.wav")
    bad = tmp_path / "bad.wav"
    bad.write_text("this is not audio")
    with pytest.raises(WavFileError):
        load_wav(bad)


def test_levels():
    assert math.isinf(rms_dbfs(np.zeros(1000, dtype=np.int16)))
    # A full-scale sine wave has RMS of about -3 dBFS.
    tone = make_tone(volume=1.0)
    assert rms_dbfs(tone) == pytest.approx(-3.0, abs=0.2)


def test_clipping_detected():
    audio = np.array([0, 32767, -32768, 100], dtype=np.int16)
    assert audio_stats(audio, 16000)["clipped"] == 2


def test_level_bar_handles_silence():
    assert "-inf" in level_bar(-math.inf)
