import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer

# Path to the extracted folder inside models/
MODEL_PATH = "asr/models/vosk-model-small-en-us-0.15"

if not os.path.exists(MODEL_PATH):
    print(f"Model path '{MODEL_PATH}' not found. Verify the extracted folder name.")
    exit(1)

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8000
)
stream.start_stream()

print("Listening...")

try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print(f"Recognized: {text}")
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()