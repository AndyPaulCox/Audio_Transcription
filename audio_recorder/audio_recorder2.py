import threading
import tkinter as tk
from tkinter import ttk  # Import ttk module for Progressbar
import pyaudio
import wave
import os
import numpy as np
from datetime import datetime

# Ensure the save path exists, create if it does not
save_path = '/Users/apcox/AWS_S3/Input/'  # Update this path to where you want to save recordings
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Create a flag to control recording
record_audio_flag = threading.Event()

def record_audio(filename, fs=44100, channels=1, update_gui_callback=None):
    print("Recording started...")
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=fs, input=True, frames_per_buffer=1024)
    frames = []

    while record_audio_flag.is_set():
        data = stream.read(1024, exception_on_overflow=False)
        frames.append(data)
        # Calculate peak volume of the current chunk of audio data
        peak_volume = np.max(np.abs(np.frombuffer(data, dtype=np.int16)))
        if update_gui_callback:
            # Normalize peak volume for simple visualization (adjust the denominator as needed)
            normalized_peak = min(peak_volume / 32768.0, 1)  # 32768.0 is the max value for int16
            update_gui_callback(normalized_peak * 100)  # Multiply by 100 for percentage representation

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    print("Recording stopped and saved.")

class RecorderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Audio Recorder")
        self.record_button = tk.Button(master, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack()
        
        # Create and configure a custom style for the progress bar
        style = ttk.Style(master)
        style.theme_use('default')  # Use the default theme as a base
        style.configure("Red.Horizontal.TProgressbar", background='red', thickness=20)  # Define custom style with red color and increased thickness
        
        # Add a progress bar as a sound level indicator
        self.progress_bar = ttk.Progressbar(master, style="Red.Horizontal.TProgressbar", orient="horizontal",length=200, mode="determinate")
        self.progress_bar.pack()

    def toggle_recording(self):
        if record_audio_flag.is_set():
            record_audio_flag.clear()
            self.record_button.config(text="Start Recording", bg="systemButtonFace")
            self.progress_bar['value'] = 0  # Reset progress bar
        else:
            record_audio_flag.set()
            self.record_button.config(text="Stop Recording", bg="red")
            filename = os.path.join(save_path, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.wav')
            threading.Thread(target=record_audio, args=(filename, 44100, 1, self.update_sound_indicator)).start()

    def update_sound_indicator(self, level):
        self.progress_bar['value'] = level

def main():
    root = tk.Tk()
    root.title("Audio Recorder")
    root.geometry("300x100")  # Adjust the window size
    app = RecorderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
