from __future__ import annotations

import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
VOICE_THRESHOLD = 0.020
END_SILENCE_SECONDS = 0.40
MAX_RECORD_SECONDS = 5.0
POLL_INTERVAL = 0.03

_whisper_model = WhisperModel("base", compute_type="int8")


def record_audio(fs: int = SAMPLE_RATE) -> np.ndarray:
    print("Ouvindo...")

    audio_chunks: list[np.ndarray] = []
    speech_started = False
    silence_started_at: float | None = None
    started_at = time.time()

    def callback(indata, frames, time_info, status):
        nonlocal speech_started, silence_started_at

        chunk = indata.copy().flatten()
        volume = float(np.abs(chunk).mean())

        if not speech_started:
            if volume >= VOICE_THRESHOLD:
                speech_started = True
                audio_chunks.append(chunk)
            return

        audio_chunks.append(chunk)

        if volume < VOICE_THRESHOLD:
            if silence_started_at is None:
                silence_started_at = time.time()
        else:
            silence_started_at = None

    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        while True:
            elapsed = time.time() - started_at

            if elapsed >= MAX_RECORD_SECONDS:
                break

            if speech_started and silence_started_at:
                if (time.time() - silence_started_at) >= END_SILENCE_SECONDS:
                    break

            time.sleep(POLL_INTERVAL)

    if not audio_chunks:
        return np.array([], dtype=np.float32)

    print("Processando...")
    return np.concatenate(audio_chunks)


def transcribe(audio: np.ndarray) -> str:
    if audio.size == 0:
        return ""

    segments, _ = _whisper_model.transcribe(
        audio,
        language="pt",
        beam_size=1,
        best_of=1,
        vad_filter=True,
        condition_on_previous_text=False,
    )

    text_parts = [segment.text.strip() for segment in segments if segment.text.strip()]
    return " ".join(text_parts)