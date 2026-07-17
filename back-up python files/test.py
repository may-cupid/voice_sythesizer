import numpy as np
import sounddevice as sd

def main():
    mysound = sine_tone()
    sd.play(mysound)
    sd.wait()

def sine_tone(  
        frequency: int=440,
        duration: float=1.0,
        amplitude: float=0.5,
        sample_rate: int=44100
) -> np.ndarray:
        n_samples = int(sample_rate * duration)
        time_points = np.linspace(0, duration, n_samples, False)
        sine = np.sin(2* np.pi * frequency * time_points)
        sine *= amplitude
        return sine
print(sine_tone)

main()
