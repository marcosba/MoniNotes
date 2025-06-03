# MoniNotes
A lightweight Python script that listens to your microphone, detects voice activity, and automatically records and saves voice segments as MP3 files. When silence is detected for a few seconds, the recording stops and the file is saved.
Sure! Here's a clean and straightforward **README.md in English** for your voice recording script:

## Features

* ✅ Automatically starts/stops recording based on voice detection.
* 💾 Saves recordings as `.mp3` (converted from `.wav`).
* 🔊 Real-time volume monitoring.
* 🛑 Tray icon with pause, resume, and exit options.
* 📁 Recordings are saved in folders named by date.

## Requirements

Install dependencies:

```bash
pip install sounddevice numpy scipy pydub colorama pystray pillow
```

Also, make sure you have `ffmpeg` installed and accessible from your system path (required by `pydub` for MP3 conversion).

## How It Works

* Listens continuously using your microphone.
* Starts recording when voice exceeds a threshold (`THRESHOLD`).
* Stops and saves the audio after `SILENCE_LIMIT` seconds of silence.
* Keeps a buffer of audio chunks to avoid missing anything at the start.
* Shows volume feedback and status in the terminal.

## Usage

1. Set your microphone index in the line:

   ```python
   MICROFONO_INDEX = 2
   ```

   You can find your device index using:

   ```python
   import sounddevice as sd
   print(sd.query_devices())
   ```

2. Place your `idle.ico` and `recording.ico` in the same folder.

3. Run the script:

   ```bash
   python voice_recorder.py
   ```

4. Use the tray icon to **pause**, **resume**, or **exit**.

## Output

* Audio files are saved in a folder named with the current date (e.g., `2025-06-03`).
* Each file is named with a timestamp: `YYYYMMDD_HHMMSS.mp3`.

## Configuration

You can tweak these values to adjust behavior:

```python
THRESHOLD = 0.008           # Minimum volume to detect voice
SILENCE_LIMIT = 5           # Seconds of silence before stopping
MIN_SILENCE_TRIGGER = 0.5   # Seconds of silence before starting countdown
RATE = 44100                # Sample rate
CHUNK = 1024                # Size of audio chunks
```

## Notes

* Works best in quiet environments.
* The script runs indefinitely until manually stopped or exited via tray.
* Requires permission to access microphone and system tray (depending on OS).

---

Let me know if you want it in Spanish too, or if you'd like to package this into an installer or executable.
