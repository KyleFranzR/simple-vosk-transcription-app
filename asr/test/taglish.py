import json
import pyaudio
from vosk import Model, KaldiRecognizer

# Load both models
model_en = Model("models/vosk-model-small-en-us-0.15")
model_tl = Model("models/vosk-model-tl-ph-generic-0.6")

rec_en = KaldiRecognizer(model_en, 16000)
rec_tl = KaldiRecognizer(model_tl, 16000)

# Enable word-level confidence output
rec_en.SetWords(True)
rec_tl.SetWords(True)

def get_avg_confidence(result_json):
    """Calculates the average confidence score from Vosk result JSON."""
    data = json.loads(result_json)
    words = data.get("result", [])
    if not words:
        return 0.0, data.get("text", "")
    
    total_conf = sum(w.get("conf", 0.0) for w in words)
    avg_conf = total_conf / len(words)
    return avg_conf, data.get("text", "")

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8000
)
stream.start_stream()

print("Listening... (Merging EN and TL outputs based on confidence)")

try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        
        # Feed same audio to both recognizers
        got_en = rec_en.AcceptWaveform(data)
        got_tl = rec_tl.AcceptWaveform(data)
        
        if got_en or got_tl:
            conf_en, text_en = get_avg_confidence(rec_en.Result())
            conf_tl, text_tl = get_avg_confidence(rec_tl.Result())
            
            # Select the output with higher confidence
            if conf_en > conf_tl and text_en:
                print(f"Recognized: {text_en} (EN - conf: {conf_en:.2f})")
            elif text_tl:
                print(f"Recognized: {text_tl} (TL - conf: {conf_tl:.2f})")

except KeyboardInterrupt:
    print("\nStopped.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()