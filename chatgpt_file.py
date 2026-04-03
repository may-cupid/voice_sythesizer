import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter


# -----------------------------
# Settings
# -----------------------------

fs = 44100          # Sample rate
duration = 1.0      # seconds
f0 = 140            # fundamental frequency (voice pitch)


# -----------------------------
# Vowel Formants
# -----------------------------

vowels = {
    "A": [730, 1090, 2440],
    "E": [530, 1840, 2480],
    "I": [270, 2290, 3010],
    "O": [570, 840, 2410],
    "U": [300, 870, 2240]
}


# -----------------------------
# Bandpass Filter
# -----------------------------

def bandpass_filter(signal, center_freq, bandwidth=120):

    low = (center_freq - bandwidth) / (fs/2)
    high = (center_freq + bandwidth) / (fs/2)

    b, a = butter(2, [low, high], btype='band')
    return lfilter(b, a, signal)


# -----------------------------
# Glottal Source (Voice Generator)
# -----------------------------

def glottal_source():

    t = np.linspace(0, duration, int(fs * duration))

    # Add harmonics for realism
    source = sum(
        np.sin(2 * np.pi * f0 * n * t) / n
        for n in range(1, 25)
    )

    return source


# -----------------------------
# Vowel Synthesizer
# -----------------------------

def synthesize_vowel(formants):

    source = glottal_source()

    vowel = np.zeros_like(source)

    for f in formants:
        vowel += bandpass_filter(source, f)

    vowel /= np.max(np.abs(vowel))

    return vowel


# -----------------------------
# Plot Function
# -----------------------------

def plot_waveform(signal, name):

    plt.figure()
    plt.plot(signal[:2000])
    plt.title(f"Waveform: {name}")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    plt.show()


# -----------------------------
# Main Program
# -----------------------------

for name, formants in vowels.items():

    print(f"Playing vowel: {name}")

    sound = synthesize_vowel(formants)

    # Play sound
    sd.play(sound, fs)
    sd.wait()

    # Save file
    filename = f"vowel_{name}.wav"
    sf.write(filename, sound, fs)

    # Plot waveform
    plot_waveform(sound, name)


print("Done!")