import sys
sys.dont_write_bytecode = True

import numpy as np
import sounddevice as sd
import time
from scipy import signal

from parameters import f0, FormantController


def synthesize_speech():
    """Synthesize speech using formant filtering of a buzz source"""

    fc = FormantController()

    formant_list = fc.load_preset("male", "A")[0]
    band_list = fc.load_preset("male", "A")[1]

    # Formant frequencies in Hz
    F = np.array(formant_list)
    # Formant bandwidths in Hz
    B = np.array(band_list)

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
    #f0 = f0
    w0T = 2 * np.pi * f0 / fs

    
    # Number of harmonics
    nharm = int(np.floor((fs/2) / f0))
    nsamps = fs  # 1 second of audio
    
    # Generate buzzy source signal (sum of harmonics)
    n = np.arange(nsamps)
    sig = np.zeros(nsamps)
    for i in range(1, nharm + 1):
        sig += np.cos(i * w0T * n)  #cos makes sense, since the constants we got from previous calcs were negative
    

    # Normalize
    sig = sig / np.max(np.abs(sig))
    
    # Apply formant filter
    # Filter the signal using the denominator coefficients A
    # scipy.signal.lfilter is the equivalent of filter(B_coeff, A, sig)
  
    speech = signal.lfilter(B_coeff, A, sig)
    
    #vibrato

    """
    speech = 
    Fs 
    t = np.arange(0,0.2,1/Fs) # Time vector

    f0_1 = F # Signal frequency-1 to construct message signal
    fm2 = 45 # Signal frequency-2 to construct message signal
    b = 1 # modulation index


    # Normalize speech for playback
    speech = speech / np.max(np.abs(speech))
    """

    """
    print("Done!")
    
    print("Playing speech (ahh)...")


    """
    sd.play(speech, fs)
    time.sleep(1)  # Wait for playback to finish

    return sig, speech 


synthesize_speech()
