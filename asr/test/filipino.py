import json
import pyaudio
from vosk import Model, KaldiRecognizer

# Path to the extracted folder inside models/
MODEL_PATH = "models/vosk-model-tl-ph-generic-0.6"

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