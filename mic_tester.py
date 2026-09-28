"""Week 1 mini project: microphone recorder and playback tester.

Run from the project folder:
    python mic_tester.py
"""

import math
from datetime import datetime

import config
from audio.devices import print_devices, require_sounddevice
from audio.exceptions import AudioError
from audio.levels import audio_stats
from audio.player import make_tone, play, play_wav
from audio.recorder import monitor_levels, record
from audio.wav_io import save_wav, wav_info

MENU = """
=== Mic Recorder & Playback Tester ===
 1. List audio devices
 2. Play test tone (check speakers)
 3. Live mic level meter (check mic)
 4. Record and save WAV
 5. Play last recording
 6. Show last recording info
 0. Quit
"""


def fmt_db(db: float) -> str:
    return "-inf" if math.isinf(db) else f"{db:.1f}"


def ask_seconds(default: float) -> float:
    """Ask the user for a number of seconds. Empty input = default."""
    text = input(f"Seconds [{default}]: ").strip()
    if not text:
        return default
    seconds = float(text)  # raises ValueError for bad input; caught in main()
    if not 0 < seconds <= 300:
        raise ValueError("Please enter a number between 0 and 300")
    return seconds


def check_quality(stats: dict) -> None:
    """Print simple advice based on the recording levels."""
    if stats["clipped"] > 0:
        print(f"  Warning: {stats['clipped']} clipped samples. Too loud - move back or lower mic gain.")
    if stats["rms_dbfs"] < config.TOO_QUIET_DBFS:
        print("  Warning: very quiet. Check the right mic is selected, it is not muted, "
              "and speak closer.")
    if stats["clipped"] == 0 and stats["rms_dbfs"] >= config.TOO_QUIET_DBFS:
        print("  Levels look OK.")


def do_record() -> str:
    seconds = ask_seconds(config.RECORD_SECONDS)
    input("Press Enter, then speak...")
    print(f"Recording {seconds}s at {config.SAMPLE_RATE} Hz, {config.CHANNELS} channel(s)...")
    audio = record(seconds)
    print("Done.")

    path = config.TEMP_DIR / f"recording_{datetime.now():%Y%m%d_%H%M%S}.wav"
    save_wav(audio, path, config.SAMPLE_RATE)
    print(f"Saved: {path}")

    stats = audio_stats(audio, config.SAMPLE_RATE)
    print(f"  Peak: {fmt_db(stats['peak_dbfs'])} dBFS | "
          f"Average: {fmt_db(stats['rms_dbfs'])} dBFS")
    check_quality(stats)
    return str(path)


def show_info(path: str) -> None:
    info = wav_info(path)
    print(f"File:        {path}")
    print(f"Duration:    {info['duration_s']:.2f} s")
    print(f"Sample rate: {info['sample_rate']} Hz")
    print(f"Channels:    {info['channels']}")
    print(f"Bit depth:   {info['bit_depth']}-bit")
    print(f"Size:        {info['size_kb']:.1f} KB")


def main() -> None:
    last_path = None

    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                print_devices()
            elif choice == "2":
                print("Playing 440 Hz beep...")
                play(make_tone(), config.SAMPLE_RATE)
            elif choice == "3":
                print("Speak now. Normal speech should reach about -30 to -10 dBFS.")
                max_db = monitor_levels(seconds=8)
                print(f"Loudest level: {fmt_db(max_db)} dBFS")
            elif choice == "4":
                last_path = do_record()
            elif choice in ("5", "6"):
                if last_path is None:
                    print("No recording yet. Use option 4 first.")
                elif choice == "5":
                    print("Playing...")
                    play_wav(last_path)
                else:
                    show_info(last_path)
            elif choice == "0":
                print("Bye!")
                break
            else:
                print("Unknown option.")

        except AudioError as exc:
            print(f"Audio error: {exc}")
        except ValueError as exc:
            print(f"Bad input: {exc}")
        except KeyboardInterrupt:
            # Ctrl+C during recording/playback: stop audio, go back to menu.
            try:
                require_sounddevice().stop()
            except AudioError:
                pass
            print("\nStopped.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):  # Ctrl+C or end of input at a prompt
        print("\nBye!")
