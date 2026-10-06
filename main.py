import threading
from gui import TranscriptionApp
from asr.engine import listen

def main():
    app = TranscriptionApp()

    audio_thread = threading.Thread(
        target=listen, 
        args=(app,), 
        daemon=True
    )
    audio_thread.start()

    app.mainloop()

if __name__ == "__main__":
    main()