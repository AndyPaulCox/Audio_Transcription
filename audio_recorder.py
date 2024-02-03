import tkinter as tk
import sounddevice as sd
import numpy as np
import wave
from datetime import datetime
import os
import threading

# Ensure the save path exists, create if it does not
save_path = '/Users/apcox/AWS_S3/Input/'
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Create a flag to control recording
record_audio_flag = threading.Event()

def record_audio(filename, fs, channels, sound_level_callback):
    print("Recording...")
    
    audio_data = []
    
    def callback(indata, frames, time, status):
        if status:
            print(f"Error in audio recording: {status}")
    
        if record_audio_flag.is_set():
            audio_data.append(indata.copy())
            
            # Calculate sound level (you can adjust the threshold as needed)
            sound_level = np.max(np.abs(indata))
            sound_level_callback(sound_level)
    
    with sd.InputStream(callback=callback, channels=channels, samplerate=fs, device=4): 
        record_audio_flag.wait()
    
    print("Recording stopped.")
    
    if audio_data:
        # Combine recorded audio blocks
        audio_data = np.concatenate(audio_data, axis=0)
        
        # Save as WAV file
        wav_file = filename.replace('.mp3', '.wav')
        with wave.open(wav_file, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(fs)
            wf.writeframes(np.int16(audio_data * 32767))  # Convert to 16-bit before saving
        
        print(f"Audio saved as {wav_file}")
    else:
        print("No audio data recorded.")

class RecorderGUI:
    def __init__(self, master):
        self.master = master
        self.recording = False
        self.button = tk.Button(master, text="Start Recording", command=self.toggle_recording, bg="black", fg="blue")
        self.button.pack(pady=20, padx=20)
        self.fs = 44100  # Sample rate
        self.channels = 1  # Stereo
        #sd.default.device = 2  # Change '0' to the device index you want to use
        
        self.sound_indicator = tk.Label(master, text="Sound Level: 0", bg="green", fg="white")
        self.sound_indicator.pack(pady=10)
        
        self.sound_threshold = 0.1  # Adjust the threshold as needed

    def toggle_recording(self):
        if self.recording:
            self.recording = False
            self.button.config(text="Start Recording", bg="black")
            # Set the flag to stop recording
            record_audio_flag.set()
        else:
            self.recording = True
            self.button.config(text="Stop Recording", bg="red")
            self.start_recording()

    def update_sound_indicator(self, sound_level):
        if sound_level >= self.sound_threshold:
            self.sound_indicator.config(bg="red")
        else:
            self.sound_indicator.config(bg="green")
        self.sound_indicator.config(text=f"Sound Level: {sound_level:.2f}")

    def start_recording(self):
        if self.recording:
            filename = os.path.join(save_path, datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.mp3')
            threading.Thread(target=record_audio, args=(filename, self.fs, self.channels, self.update_sound_indicator)).start()

def main():
    root = tk.Tk()
    app = RecorderGUI(root)
    root.title("Audio Recorder")
    root.geometry("200x150")
    root.mainloop()

if __name__ == "__main__":
    main()
