import threading
import tkinter as tk
import pyaudio
import wave
import os
import numpy as np
from datetime import datetime

#  This script works, but need to go iinto sound and set USB Audio device as the input mode

# Ensure the save path exists, create if it does not
save_path = '/Users/apcox/AWS_S3/Input/'  # Make sure to update this path to a valid one
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
        # Calculate the RMS of the current chunk of audio data
        rms = np.sqrt(np.mean(np.square(np.frombuffer(data, dtype=np.int16))))
        if update_gui_callback:
            # Normalize RMS for simple visualization
            normalized_rms = min(rms / 2000, 1)  # Adjust the denominator as needed
            update_gui_callback(normalized_rms)

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
        
        # Add a canvas as a sound level indicator
        self.canvas = tk.Canvas(master, width=100, height=20, bg='red')
        self.canvas.pack()

    def toggle_recording(self):
        if record_audio_flag.is_set():
            record_audio_flag.clear()
            self.record_button.config(text="Start Recording", bg="black")
            self.canvas.config(bg='red')  # Reset indicator color
        else:
            record_audio_flag.set()
            self.record_button.config(text="Stop Recording", bg="red")
            filename = os.path.join(save_path, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.wav')
            threading.Thread(target=record_audio, args=(filename, 44100, 1, self.update_sound_indicator)).start()

    def update_sound_indicator(self, level):
        color = 'green' if level > 0.1 else 'red'  # Change threshold as needed
        self.canvas.config(bg=color)

def main():
    root = tk.Tk()
    app = RecorderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
