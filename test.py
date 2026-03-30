import numpy as np
import sounddevice as sd

def main():
    mysound = white_noise()
    sd.play(mysound)
    sd.wait()

def sine_tone(
        frequency: int=440
        duration: float=1.0,
        amplitude: float=0.5,
        sample_rate: int=44100
) -> np.ndarray:

"""generate sine tone"""

n_samples = int(sample_rate * duration)
timepoints = np.linspace(0, duration, n_samples, False)
sine = np.sin(2* np.pi * frequency * time_points)
sine *= amplitude
return sine


def test_noise(
        duration: float=1.0,
        amplitude: float=0.5,
        sample_rate: int=44100
) -> np.ndarray:
    

