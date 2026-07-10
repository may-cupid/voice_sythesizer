#!/usr/bin/env python3
"""
Formant Synthesis Program
Converts MATLAB/Jupyter code to standalone Python executable
"""

import numpy as np
import sounddevice as sd
import time

def synthesize_speech():
    """Synthesize speech using formant filtering of a buzz source"""
    
    # Formant frequencies in Hz
    F = np.array([700, 1220, 2600])
    # Formant bandwidths in Hz
    B = np.array([130, 70, 160])
    
    # Sampling rate in Hz
    fs = 8192
    
    # Pole radii and angles
    R = np.exp(-np.pi * B / fs)
    theta = 2 * np.pi * F / fs
    poles = R * np.exp(1j * theta)
    
    # Convert poles to filter coefficients
    # zp2tf equivalent: poles and their conjugates
    all_poles = np.concatenate([poles, np.conj(poles)])
    A = np.poly(all_poles)  # Denominator coefficients
    B_coeff = np.array([1.0])  # Numerator coefficients (no zeros)
    
    # Ensure A is real (should be, but numerical errors might occur)
    A = np.real(A)
    
    # Fundamental frequency in Hz
    f0 = 200
    w0T = 2 * np.pi * f0 / fs
    
    # Number of harmonics
    nharm = int(np.floor((fs/2) / f0))
    nsamps = fs  # 1 second of audio
    
    # Generate buzzy source signal (sum of harmonics)
    n = np.arange(nsamps)
    sig = np.zeros(nsamps)
    for i in range(1, nharm + 1):
        sig += np.cos(i * w0T * n)
    
    # Normalize
    sig = sig / np.max(np.abs(sig))
    
    # Apply formant filter
    # Filter the signal using the denominator coefficients A
    # scipy.signal.lfilter is the equivalent of filter(B_coeff, A, sig)
    from scipy import signal
    speech = signal.lfilter(B_coeff, A, sig)
    
    # Normalize speech for playback
    speech = speech / np.max(np.abs(speech))
    
    # Play the sounds (buzz then "ahh")
    print("Playing buzz source...")
    sd.play(sig, fs)
    time.sleep(1)  # Wait for playback to finish
    
    print("Playing speech (ahh)...")
    sd.play(speech, fs)
    time.sleep(1)  # Wait for playback to finish
    
    # Also concatenate them for comparison
    combined = np.concatenate([sig, speech])
    combined = combined / np.max(np.abs(combined))
    
    print("Playing combined (buzz + ahh)...")
    sd.play(combined, fs)
    time.sleep(2)
    
    print("Done!")
    
    return sig, speech

if __name__ == "__main__":
    print("Formant Synthesis Program")
    print("=" * 30)
    print("Synthesizing speech...")
    
    try:
        sig, speech = synthesize_speech()
        print(f"Signal length: {len(sig)} samples")
        print(f"Sampling rate: 8192 Hz")
        print(f"Duration: {len(sig)/8192:.2f} seconds")
        
        # Optional: Save to WAV file
        from scipy.io import wavfile
        wavfile.write('buzz.wav', 8192, (sig * 32767).astype(np.int16))
        wavfile.write('speech_ahh.wav', 8192, (speech * 32767).astype(np.int16))
        print("Audio files saved: buzz.wav and speech_ahh.wav")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        print("\nIf you see audio errors, try:")
        print("1. Make sure your audio device is working")
        print("2. Install required packages: pip install numpy scipy sounddevice")