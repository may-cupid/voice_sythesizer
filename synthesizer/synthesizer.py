import sys
sys.dont_write_bytecode = True

import numpy as np
from scipy import signal

from params import DEFAULT_EFFECTS, DEFAULT_SETTINGS


import sounddevice as sd
import time



SAMPLE_RATE = 8192



def generate_speech(synth_kwargs : dict):
    """Generate a loopable synthesised vowel signal.

    Parameters
    ----------
    gender : str
        Either 'male' or 'female'.
    vowel : str | dict
        A vowel name or a serialized FormantController dictionary.
    f0 : float
        Fundamental frequency in Hz.
    effects : dict | None
        Optional effect settings. Supported keys are listed in DEFAULT_EFFECTS.
    fs : int
        Sampling rate used for synthesis.
    """

    synthesizer_settings = synth_kwargs

    effects = synthesizer_settings.get("effects")
    print(effects)

    if effects is None:
        effects = DEFAULT_EFFECTS

    fs = SAMPLE_RATE

    formant_list = list(synthesizer_settings.get("vowel", {}).get("formant_list"))
    band_list = list(synthesizer_settings.get("vowel",{}).get("band_list"))

    print(formant_list,band_list)

    
    f0 = synthesizer_settings.get("f0")

    F = np.array(formant_list)
    B = np.array(band_list)

    R = np.exp(-np.pi * B / fs)
    theta = 2 * np.pi * F / fs
    poles = R * np.exp(1j * theta)

    all_poles = np.concatenate([poles, np.conj(poles)])
    A = np.poly(all_poles) 
    A = np.real(A) #ensure A is real
    B_coeff = np.array([1.0])

    if f0 <= 0:
        raise ValueError("f0 must be greater than zero.")
    else:
        f0 = f0

    w0T = 2 * np.pi * f0 / fs

    nharm = int(np.floor((fs / 2) / f0))
    
    nsamps = fs
    n = np.arange(nsamps)
    sig = np.zeros(nsamps)

    for harmonic in range(1, nharm + 1):
        sig += np.cos(harmonic * w0T * n)

    sig = sig / np.max(np.abs(sig))

    if effects.get("vibrato_enabled", False):
        vibrato_depth = float(effects.get("vibrato_depth", 12.0))
        vibrato_rate = float(effects.get("vibrato_rate", 5.0))
        modulation = 1.0 + (vibrato_depth / max(f0, 1.0)) * np.sin(2 * np.pi * vibrato_rate * n / fs)
        sig = sig * modulation


    speech = signal.lfilter(B_coeff, A, sig)

    """
    peak = np.max(np.abs(speech))
    if peak > 0:
        speech = speech / peak
    """

    speech = speech / np.max(np.abs(speech))
    gain = float(effects.get("gain", 1.0))

    speech = speech / np.max(np.abs(speech))
    """
    sd.play(speech, fs)
    time.sleep(1)  # Wait for playback to finish
    """

    speech_sound_file = np.clip(speech * gain, -1.0, 1.0).astype(np.float32)

    return speech_sound_file



