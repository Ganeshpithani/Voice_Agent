"""Custom errors for the audio package.

Having our own error types lets main code catch "any audio problem"
with one `except AudioError:` line.
"""


class AudioError(Exception):
    """Base class for all audio errors."""


class DeviceError(AudioError):
    """Microphone or speaker is missing, busy, or does not support the settings."""


class WavFileError(AudioError):
    """WAV file is missing, broken, or in a format we do not support."""
