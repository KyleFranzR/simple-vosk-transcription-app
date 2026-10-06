import os
import re
import json
import wave
import subprocess
import tempfile
from typing import Optional
from threading import Event
from vosk import Model, KaldiRecognizer

MODEL_PATH = "asr/models/vosk-model-en-us-0.22-lgraph"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg.exe")


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def convert_media_to_pcm_wav(input_file_path: str, output_wav_path: str):
    ffmpeg_bin = FFMPEG_PATH if os.path.exists(FFMPEG_PATH) else "ffmpeg"
    
    command = [
        ffmpeg_bin,
        "-y",
        "-i", input_file_path,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_wav_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed: {result.stderr.decode('utf-8')}")


def extract_transcription_from_media(file_path: str, cancel_event: Optional[Event] = None) -> str:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Vosk model path '{MODEL_PATH}' not found.")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        temp_wav_path = temp_wav.name

    try:
        if cancel_event and cancel_event.is_set():
            return ""

        convert_media_to_pcm_wav(file_path, temp_wav_path)

        wf = wave.open(temp_wav_path, "rb")
        model = Model(MODEL_PATH)
        recognizer = KaldiRecognizer(model, wf.getframerate())

        results = []
        while True:
            if cancel_event and cancel_event.is_set():
                wf.close()
                return ""
                
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                res = json.loads(recognizer.Result())
                text = res.get("text", "")
                if text:
                    results.append(text)

        final_res = json.loads(recognizer.FinalResult())
        final_text = final_res.get("text", "")
        if final_text:
            results.append(final_text)

        wf.close()
        full_text = " ".join(results)
        return clean_text(full_text)

    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)