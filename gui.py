import os
import time
import threading
import customtkinter as ctk
from tkinter import filedialog
from services.docu_proc import extract_document_text
from services.image_proc import extract_text_from_image
from services.media_proc import extract_transcription_from_media

class TranscriptionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vosk Speech Transcription")
        self.geometry("600x500")

        self.is_editable = False
        self.is_recording = False
        self.is_busy = False  # Track global processing lock state
        self.space_pressed = False
        self.last_space_press_time = 0
        
        # Cancellation Event for background threads
        self.cancel_event = threading.Event()
        
        # Timer IDs and Delay Configurations
        self.listen_timer = None
        self.release_timer = None
        self.HOLD_DELAY_MS = 250    # Delay before listening starts
        self.RELEASE_DELAY_MS = 300 # Delay before listening ends after key release
        self.selected_file_path = None

        # UI Layout - Header Row
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(padx=20, pady=(15, 5), fill="x")

        self.label = ctk.CTkLabel(self.header_frame, text="Live Transcription", font=("Arial", 16, "bold"))
        self.label.pack(side="left", anchor="n")

        # Right control panel containing Select File & Cancel buttons stacked vertically
        self.button_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.button_container.pack(side="right")

        self.file_button = ctk.CTkButton(
            self.button_container, 
            text="Select File", 
            width=110,
            command=self.open_file_picker
        )
        self.file_button.pack(pady=(0, 5))

        self.cancel_button = ctk.CTkButton(
            self.button_container, 
            text="Cancel Process", 
            width=110,
            fg_color="#D32F2F",
            hover_color="#9A0007",
            command=self.cancel_current_process,
            state="disabled"
        )
        self.cancel_button.pack()

        self.status_label = ctk.CTkLabel(
            self, 
            text="Status: Idle (Hold SPACE to speak, Double SPACE to clear)", 
            font=("Arial", 12), 
            text_color="gray"
        )
        self.status_label.pack(padx=20, pady=(0, 5), anchor="w")

        # Textbox
        self.textbox = ctk.CTkTextbox(self, width=560, height=230, wrap="word")
        self.textbox.pack(padx=20, pady=10)
        self.textbox.configure(state="disabled")

        # Edit Button
        self.edit_button = ctk.CTkButton(
            self, 
            text="Enable Edit", 
            command=self.toggle_edit_mode
        )
        self.edit_button.pack(padx=20, pady=10)

        # Key Bindings
        self.bind("<KeyPress-space>", self.on_space_press)
        self.bind("<KeyRelease-space>", self.on_space_release)

    def set_processing_lock(self, locked: bool):
        """Locks or unlocks user controls during any audio, document, image, or video processing."""
        self.is_busy = locked
        if locked:
            self.file_button.configure(state="disabled")
            self.edit_button.configure(state="disabled")
            self.cancel_button.configure(state="normal")
        else:
            self.file_button.configure(state="normal")
            self.edit_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            self.cancel_event.clear()

    def unlock_ui(self):
        """Thread-safe UI unlock call."""
        self.after(0, self.set_processing_lock, False)

    def cancel_current_process(self):
        """Signals cancellation to running tasks and restores UI controls."""
        if self.is_busy:
            self.cancel_event.set()
            self.set_status("Status: Cancelling process...", "red")

    def open_file_picker(self):
        """Opens file dialog and runs extraction in a background thread."""
        if self.is_busy:
            return

        supported_filetypes = [
            ("All Supported Files", "*.docx *.doc *.pdf *.bmp *.jpeg *.jpg *.png *.wav *.mp3 *.aac *.flac *.m4a *.ogg *.mp4 *.mkv *.avi *.mov *.flv"),
            ("Media Files (Audio/Video)", "*.wav *.mp3 *.aac *.flac *.m4a *.ogg *.mp4 *.mkv *.avi *.mov *.flv"),
            ("Image Files", "*.bmp *.jpeg *.jpg *.png"),
            ("Document Files", "*.docx *.doc *.pdf"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=supported_filetypes
        )
        
        if file_path:
            self.selected_file_path = file_path
            self.cancel_event.clear()
            self.set_processing_lock(True)
            
            threading.Thread(
                target=self._process_file_worker, 
                args=(file_path,), 
                daemon=True
            ).start()

    def _process_file_worker(self, file_path: str):
        """Worker thread for running OCR/ASR file extraction with guaranteed cleanup."""
        ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        
        doc_exts = [".docx", ".doc", ".pdf"]
        img_exts = [".bmp", ".jpeg", ".jpg", ".png"]
        media_exts = [".wav", ".mp3", ".aac", ".flac", ".m4a", ".ogg", ".mp4", ".mkv", ".avi", ".mov", ".flv"]

        if ext in doc_exts:
            category = "Document"
        elif ext in img_exts:
            category = "Image (OCR)"
        elif ext in media_exts:
            category = "Media (ASR)"
        else:
            category = "File"

        self.after(0, self.set_status, f"Status: Processing {category} ('{file_name}')...", "orange")

        try:
            extracted_text = ""
            if ext in doc_exts:
                extracted_text = extract_document_text(file_path, self.cancel_event)
            elif ext in img_exts:
                extracted_text = extract_text_from_image(file_path, self.cancel_event)
            elif ext in media_exts:
                extracted_text = extract_transcription_from_media(file_path, self.cancel_event)
            else:
                self.after(0, self.set_status, f"Status: Unsupported format '{ext}'", "red")
                return

            if self.cancel_event.is_set():
                self.after(0, self.set_status, f"Status: {category} processing cancelled", "red")
            elif extracted_text and extracted_text.strip():
                self.after(0, self.append_transcription, extracted_text.strip())
                self.after(0, self.set_status, f"Status: {category} processed successfully", "green")
            else:
                self.after(0, self.set_status, f"Status: Selected {category.lower()} contains no readable text", "red")
        except Exception as e:
            if self.cancel_event.is_set():
                self.after(0, self.set_status, f"Status: {category} processing cancelled", "red")
            else:
                print(f"Error processing file: {e}")
                self.after(0, self.set_status, f"Status: Failed to process {category.lower()}", "red")
        finally:
            self.unlock_ui()

    def on_space_press(self, event):
        if self.is_editable or self.space_pressed or self.is_busy:
            return

        current_time = time.time()
        if current_time - self.last_space_press_time < 0.3:
            self.clear_textbox()

        self.last_space_press_time = current_time
        self.space_pressed = True

        if self.release_timer is not None:
            self.after_cancel(self.release_timer)
            self.release_timer = None

        self.listen_timer = self.after(self.HOLD_DELAY_MS, self.start_listening)

    def start_listening(self):
        if self.space_pressed and not self.is_editable and not self.is_busy:
            self.is_recording = True
            self.set_status("Status: Listening...", "green")

    def on_space_release(self, event):
        if self.is_editable or self.is_busy:
            return

        self.space_pressed = False

        if self.listen_timer is not None:
            self.after_cancel(self.listen_timer)
            self.listen_timer = None

        if self.is_recording:
            if self.release_timer is not None:
                self.after_cancel(self.release_timer)
            
            self.release_timer = self.after(self.RELEASE_DELAY_MS, self.stop_listening)

    def stop_listening(self):
        self.is_recording = False
        self.release_timer = None
        self.set_processing_lock(True)
        self.set_status("Status: Processing audio...", "orange")

    def set_status(self, text: str, color: str):
        self.status_label.configure(text=text, text_color=color)

    def clear_textbox(self):
        if self.is_busy:
            return
        current_state = self.textbox.cget("state")
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        if not self.is_editable:
            self.textbox.configure(state="disabled")

    def toggle_edit_mode(self):
        if self.is_busy:
            return
        self.is_editable = not self.is_editable
        if self.is_editable:
            self.textbox.configure(state="normal")
            self.edit_button.configure(text="Stop Editing (Lock)")
            self.set_status("Status: Editing Enabled (Speech Recognition Disabled)", "blue")
        else:
            self.textbox.configure(state="disabled")
            self.edit_button.configure(text="Enable Edit")
            self.set_status("Status: Idle (Hold SPACE to speak, Double SPACE to clear)", "gray")

    def append_transcription(self, text: str):
        current_state = self.textbox.cget("state")
        if current_state == "disabled":
            self.textbox.configure(state="normal")

        self.textbox.insert("end", text + " ")
        self.textbox.see("end")

        if not self.is_editable:
            self.textbox.configure(state="disabled")