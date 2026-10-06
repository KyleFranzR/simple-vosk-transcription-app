import json
import time
import pyaudio
from vosk import Model, KaldiRecognizer

MODEL_PATH = "asr/models/vosk-model-en-us-0.22-lgraph"

def listen(app):
    """Listens to microphone input efficiently when app.is_recording is True."""
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=4000
    )
    stream.start_stream()

    def safe_unlock():
        unlock_fn = getattr(app, "unlock_ui", None)
        if callable(unlock_fn):
            unlock_fn()

    was_recording = False

    try:
        while True:
            # Check for process cancellation
            if getattr(app, "cancel_event", None) and app.cancel_event.is_set() and getattr(app, "is_busy", False):
                recognizer.Reset()
                if hasattr(app, "after"):
                    app.after(0, app.set_status, "Status: Speech processing cancelled", "red")
                safe_unlock()

            is_recording = getattr(app, "is_recording", False)
            is_busy = getattr(app, "is_busy", False)

            if is_recording:
                # Flush stale buffer when user starts speaking
                if not was_recording:
                    while stream.get_read_available() > 0:
                        stream.read(stream.get_read_available(), exception_on_overflow=False)
                    was_recording = True

                data = stream.read(4000, exception_on_overflow=False)
                if len(data) == 0:
                    continue

                if recognizer.AcceptWaveform(data):
                    res = json.loads(recognizer.Result())
                    text = res.get("text", "")
                    if text and hasattr(app, "after"):
                        app.after(0, app.append_transcription, text)

            elif is_busy and was_recording:
                # Process final remaining audio on key release
                was_recording = False
                final_res = json.loads(recognizer.FinalResult())
                text = final_res.get("text", "")
                
                if hasattr(app, "cancel_event") and not app.cancel_event.is_set():
                    if text and hasattr(app, "after"):
                        app.after(0, app.append_transcription, text)
                    if hasattr(app, "after"):
                        app.after(0, app.set_status, "Status: Idle (Hold SPACE to speak, Double SPACE to clear)", "gray")
                
                safe_unlock()

            else:
                # Idle state: sleep briefly to prevent high CPU usage and lag
                was_recording = False
                time.sleep(0.05)

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()