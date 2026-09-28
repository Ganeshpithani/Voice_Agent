"""Access to sounddevice, plus helpers to list audio devices."""

from audio.exceptions import DeviceError

# sounddevice needs the PortAudio system library. If it is missing, importing
# sounddevice raises OSError. We catch it here so the rest of the program can
# still run (e.g. the WAV tests) and show a helpful message later.
try:
    import sounddevice as sd
    _import_error = None
except OSError as exc:
    sd = None
    _import_error = exc


def require_sounddevice():
    """Return the sounddevice module, or raise DeviceError with a fix hint."""
    if sd is None:
        raise DeviceError(
            "PortAudio library not found.\n"
            "  Linux:   sudo apt install libportaudio2\n"
            "  macOS:   brew install portaudio\n"
            "  Windows: pip install --force-reinstall sounddevice"
        ) from _import_error
    return sd


def list_devices() -> list[dict]:
    """Return all audio devices as a list of simple dicts."""
    sd_mod = require_sounddevice()
    devices = []
    for index, info in enumerate(sd_mod.query_devices()):
        devices.append({
            "index": index,
            "name": info["name"],
            "inputs": info["max_input_channels"],
            "outputs": info["max_output_channels"],
            "default_rate": int(info["default_samplerate"]),
        })
    return devices


def print_devices() -> None:
    """Print a readable table of devices. '>' marks the default input, '<' the default output."""
    sd_mod = require_sounddevice()
    default_in, default_out = sd_mod.default.device
    print(f"{'':2} {'#':>3}  {'In':>3} {'Out':>3} {'Rate':>6}  Name")
    for d in list_devices():
        mark = (">" if d["index"] == default_in else " ") + ("<" if d["index"] == default_out else " ")
        print(f"{mark} {d['index']:>3}  {d['inputs']:>3} {d['outputs']:>3} {d['default_rate']:>6}  {d['name']}")
