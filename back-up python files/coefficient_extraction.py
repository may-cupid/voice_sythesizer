import os
import numpy as np
import librosa

# -------- USER INPUT --------
folder_path = "voice_recordings"

# Frequencies you want to measure (Hz)
harmonics = [
                440
             
             
             ]

# ----------------------------

# Find WAV file
wav_files = [f for f in os.listdir(folder_path) if f.endswith(".wav")]

if not wav_files:
    raise ValueError("No WAV files found.")

file_path = os.path.join(folder_path, wav_files[0])
print(f"Loading: {file_path}")

# Load audio
y, sr = librosa.load(file_path, sr=None)

# Optional: window to reduce spectral leakage
window = np.hanning(len(y))
y = y * window

# FFT
fft = np.fft.fft(y)
frequencies = np.fft.fftfreq(len(fft), 1/sr)
magnitudes = np.abs(fft)

# Only positive frequencies
half = len(fft) // 2
frequencies = frequencies[:half]
magnitudes = magnitudes[:half]


print("\nTarget Frequency Amplitudes:\n")

# Find amplitude for each requested frequency
for target in harmonics:
    index = np.argmin(np.abs(frequencies - target))
    freq = frequencies[index]
    amp = magnitudes[index]

    print(f"Target: {target:.2f} Hz | Found: {freq:.2f} Hz | Amplitude: {amp:.6f}")