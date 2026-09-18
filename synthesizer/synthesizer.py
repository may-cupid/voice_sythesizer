import sys
sys.dont_write_bytecode = True

import numpy as np
from scipy import signal

from parameters import FormantController


import sounddevice as sd
import time



SAMPLE_RATE = 8192

DEFAULT_EFFECTS = {
    "vibrato_enabled": False,
    "vibrato_depth": 12.0,
    "vibrato_rate": 5.0,
    "gain": 1.0,
    "noise_level": 0.0,
    "formant_shift": 0.0,
}

def generate_speech(gender: str = "female", vowel="A", f0: float = 200.0, effects=None, fs: int = SAMPLE_RATE):
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

    if effects is None:
        effects = {}

    effect_values = DEFAULT_EFFECTS.copy()
    effect_values.update(effects)

    fc = FormantController(gender=gender, vowel=vowel)
    formant_list = list(fc.formant_list)
    band_list = list(fc.band_list)

    formant_shift = float(effect_values.get("formant_shift", 0.0))
    if formant_shift != 0:
        formant_list = [frequency * (1 + formant_shift) for frequency in formant_list]

    F = np.array(formant_list, dtype=float)
    B = np.array(band_list, dtype=float)

    R = np.exp(-np.pi * B / fs)
    theta = 2 * np.pi * F / fs
    poles = R * np.exp(1j * theta)

    all_poles = np.concatenate([poles, np.conj(poles)])
    A = np.real(np.poly(all_poles))
    B_coeff = np.array([1.0])

    if f0 <= 0:
        raise ValueError("f0 must be greater than zero.")

    nsamps = fs
    n = np.arange(nsamps)
    w0T = 2 * np.pi * f0 / fs

    nharm = int(np.floor((fs / 2) / f0))
    sig = np.zeros(nsamps, dtype=float)

    for harmonic in range(1, nharm + 1):
        sig += (1 / harmonic) * np.cos(harmonic * w0T * n)

    sig = sig / np.max(np.abs(sig))

    if effect_values.get("vibrato_enabled", False):
        vibrato_depth = float(effect_values.get("vibrato_depth", 12.0))
        vibrato_rate = float(effect_values.get("vibrato_rate", 5.0))
        modulation = 1.0 + (vibrato_depth / max(f0, 1.0)) * np.sin(2 * np.pi * vibrato_rate * n / fs)
        sig = sig * modulation

    noise_level = float(effect_values.get("noise_level", 0.0))
    if noise_level > 0:
        sig = sig + (np.random.default_rng(0).normal(0, noise_level, size=nsamps))


    speech = signal.lfilter(B_coeff, A, sig)

    """
    peak = np.max(np.abs(speech))
    if peak > 0:
        speech = speech / peak
    """

    speech = speech / np.max(np.abs(speech))
    gain = float(effect_values.get("gain", 1.0))

    speech = speech / np.max(np.abs(speech))

    sd.play(speech, fs)
    time.sleep(1)  # Wait for playback to finish


    speech_sound_file = np.clip(speech * gain, -1.0, 1.0).astype(np.float32)

    return speech_sound_file, speech, fs




def synthesize_speech(gender: str = "female", vowel: str = "A", f0: float = 200.0, effects=None):
    """Backward-compatible wrapper used by the new GUI and any old callers."""
    return generate_speech(gender=gender, vowel=vowel, f0=f0, effects=effects)

generate_speech()