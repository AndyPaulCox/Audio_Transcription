import tkinter as tk
from tkinter import ttk # this 
import pyaudio
import numpy as np
import threading

# Function to update the progress bar
def update_progress_bar(volume):
    progress_bar['value'] = volume
    root.update_idletasks()

# Function to handle audio stream and calculate volume
def audio_stream():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    
    while recording:
        data = np.frombuffer(stream.read(1024), dtype=np.int16)
        volume = np.abs(np.max(data)) / 32768  # Normalize the volume to a 0-100 scale
        update_progress_bar(volume * 100)  # Update progress bar with volume
    
    stream.stop_stream()
    stream.close()
    p.terminate()

def start_recording():
    global recording
    recording = True
    threading.Thread(target=audio_stream).start()

def stop_recording():
    global recording
    recording = False

# GUI Setup
root = tk.Tk()
root.title("Audio Level Indicator")
root.geometry("400x100")

progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.pack(pady=20)

start_button = tk.Button(root, text="Start Recording", command=start_recording)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)
stop_button.pack(side=tk.RIGHT, padx=10)

recording = False
root.mainloop()
