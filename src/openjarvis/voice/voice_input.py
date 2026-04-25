# src/openjarvis/voice/voice_input.py

from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np


def record_audio(duration=5, fs=16000):
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return audio.flatten()


def transcribe(audio):
    model = WhisperModel("small")
    segments, _ = model.transcribe(
        audio,
        language="pt",
        beam_size=5,
        best_of=5
)

    text = ""
    for segment in segments:
        text += segment.text

    return text