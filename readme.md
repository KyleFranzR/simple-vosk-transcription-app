# Vosk Speech Transcription App

A Python desktop application built with **CustomTkinter** and **Vosk** for offline real-time speech recognition, optical character recognition (OCR), and document text extraction.

---

## Features

* **Live Speech-to-Text**: Hold `SPACE` to record audio and convert speech to text offline using Vosk.
* **Text Area Editing**: Toggle edit mode to modify or correct transcribed text directly.
* **Double-Tap Clear**: Double-press `SPACE` to quickly reset the text area.
* **Document & Media Processing**: Extract text from `.docx`, `.pdf`, image files (OCR), and audio/video files.
* **Process Control**: Cancel long-running extraction or audio processing at any time.

---

## Project Structure

```text
.
├── asr/
│   ├── models/
│   │   └── vosk-model-en-us-0.22-lgraph/   # Vosk language model directory
│   └── engine.py                          # Speech recognition processing engine
├── services/
│   ├── docu_proc.py                       # Document text extraction (.docx, .pdf)
│   ├── image_proc.py                      # OCR image processing (.png, .jpg, etc.)
│   ├── media_proc.py                      # Audio/video transcription
│   ├── tesseract/                         # Local Tesseract OCR binaries
│   └── ffmpeg.exe                         # Local FFmpeg binary
├── gui.py                                 # CustomTkinter GUI implementation
├── main.py                                # Main application entry point
├── pyproject.toml                         # Project configuration and dependencies
├── .gitignore
└── README.md

```

---

## Prerequisites

* **Python**: Version 3.9 to 3.11 recommended.
* **PortAudio**: Required by `PyAudio` for microphone input capture.
* **macOS**: `brew install portaudio`
* **Linux (Ubuntu/Debian)**: `sudo apt-get install portaudio19-dev python3-pyaudio`
* **Windows**: PyAudio wheel dependencies are handled automatically via pip.



---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/vosk-speech-transcription.git
cd vosk-speech-transcription

```

### 2. Create and Activate a Virtual Environment

* **macOS / Linux**:
```bash
python3 -m venv venv
source venv/bin/activate

```


* **Windows**:
```cmd
python -m venv venv
venv\Scripts\activate

```



### 3. Install Dependencies from `pyproject.toml`

Install the project along with its dependencies using `pip`:

```bash
pip install .

```

*For editable development mode:*

```bash
pip install -e .

```

---

## External Binaries & Models Setup

Because large binaries and models are excluded from version control, you must place them inside the project directories before running the app.

### 1. Tesseract OCR

* Download the Tesseract binaries for your operating system.
* Place the folder inside `services/` so the path resolves to:
```text
services/Tesseract-OCR/

```



### 2. FFmpeg Binary

* Download the static FFmpeg executable for your OS.
* Place `ffmpeg.exe` (or `ffmpeg` on macOS/Linux) directly inside `services/`:
```text
services/ffmpeg.exe

```



### 3. Vosk Speech Model

1. Download [vosk-model-en-us-0.22-lgraph.zip](https://www.google.com/search?q=https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip).
2. Extract the zip file into `asr/models/` so the path looks like this:
```text
asr/models/vosk-model-en-us-0.22-lgraph/

```



---

## Running the Application

Launch the application using Python:

```bash
python main.py

```

---

## Usage Guide

| Action | Controls / Steps |
| --- | --- |
| **Live Recording** | Press and **hold `SPACE**` to speak into the microphone. Release `SPACE` to process audio. |
| **Clear Text** | **Double-press `SPACE**` quickly to clear the textbox. |
| **Manual Editing** | Click **Enable Edit** to unlock text editing. Click **Stop Editing (Lock)** when finished. |
| **File Extraction** | Click **Select File** to load text from documents (`.docx`, `.pdf`), images, or media files. |
| **Cancel Task** | Click **Cancel Process** to stop active file processing or speech recognition. |

---

## Troubleshooting

* **Microphone Access Error**: Ensure your operating system grants microphone access permissions to Python/Terminal.
* **Missing Binary Errors**: Double-check that `ffmpeg.exe` and `tesseract/` are located inside `services/`, and that the Vosk model directory matches the path inside `asr/engine.py`.