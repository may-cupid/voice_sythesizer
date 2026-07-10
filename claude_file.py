"""
formant_multiply.py

Multiplies a "formant graph" (a set of peak frequencies) with a source sound,
strengthening the peak frequencies and weakening everything else.

How it works
------------
1. Load the source audio.
2. Take its Short-Time Fourier Transform (STFT) -> magnitude + phase per frame.
3. Build a formant envelope: a curve over frequency that is high at the
   formant peaks and low elsewhere (each peak is a Gaussian bump; bumps sum
   together to form the full curve).
4. Multiply the magnitude spectrum of the source by the envelope, frame by frame.
5. Recombine the new magnitude with the ORIGINAL phase and inverse-STFT back
   to a waveform.
6. Normalize and save.

Usage (from command line)
--------------------------
    python formant_multiply.py input.wav output.wav

You can edit the FORMANTS list below to change which frequencies get boosted.
"""

import numpy as np
import soundfile as sf
import librosa
import argparse


# ---------------------------------------------------------------------------
# Step A: Define the formant graph
# ---------------------------------------------------------------------------
# Each tuple is (frequency_Hz, gain, bandwidth_Hz).
#   frequency_Hz -> where the peak sits
#   gain         -> relative strength of that peak (1.0 = full strength)
#   bandwidth_Hz -> how wide the peak is (smaller = sharper/narrower peak)
#
# Example below roughly resembles vowel-like formants (F1, F2, F3).
# Replace these with whatever peak frequencies you want to emphasize.
FORMANTS = [
    (730,  1, 50),
    (1090, 1, 60),
    (2440, 1, 30),
]

# How much to suppress non-peak frequencies (0 = total silence away from
# peaks, 1 = no suppression at all / envelope has no effect).
# A small non-zero floor avoids completely killing frequencies between peaks.
FLOOR = 0


def build_formant_envelope(freqs: np.ndarray, formants=FORMANTS, floor=FLOOR) -> np.ndarray:
    """
    Build a 1D envelope curve aligned to the given FFT bin frequencies.

    freqs   : array of frequency values for each STFT bin (Hz), e.g. from
              librosa.fft_frequencies()
    formants: list of (freq_Hz, gain, bandwidth_Hz)
    floor   : minimum envelope value between peaks (keeps things from going
              completely silent away from the formants)

    Returns an array the same length as freqs, normalized so the tallest
    peak = 1.0, then rescaled so the valley floor = `floor`.
    """
    envelope = np.zeros_like(freqs, dtype=np.float64)

    for f0, gain, bw in formants:
        # Gaussian bump centered at f0 with "width" bw
        bump = gain * np.exp(-0.5 * ((freqs - f0) / bw) ** 2)
        envelope = np.maximum(envelope, bump)  # take the max, don't just sum,
                                                # so overlapping peaks don't
                                                # blow out in amplitude

    # Normalize peak to 1.0
    if envelope.max() > 0:
        envelope = envelope / envelope.max()

    # Apply a floor so non-peak frequencies are weakened, not deleted
    envelope = floor + (1 - floor) * envelope

    return envelope


def apply_formants(y: np.ndarray, sr: int, formants=FORMANTS, floor=FLOOR,
                    n_fft=2048, hop_length=512) -> np.ndarray:
    """
    Apply the formant envelope to an audio signal via STFT multiplication.
    """
    # Step B: STFT of the source sound
    stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    magnitude, phase = np.abs(stft), np.angle(stft)

    # Step C: Build the envelope at the STFT's frequency resolution
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    envelope = build_formant_envelope(freqs, formants, floor)

    # Step D: Multiply magnitude spectrum by envelope (broadcast across time frames)
    new_magnitude = magnitude * envelope[:, np.newaxis]

    # Step E: Recombine with original phase, then inverse STFT
    new_stft = new_magnitude * np.exp(1j * phase)
    y_out = librosa.istft(new_stft, hop_length=hop_length, length=len(y))

    return y_out


def normalize(y: np.ndarray, peak=0.99) -> np.ndarray:
    """Scale audio so its max absolute value is `peak`, avoiding clipping."""
    max_val = np.max(np.abs(y))
    if max_val > 0:
        y = y / max_val * peak
    return y


def main():
    parser = argparse.ArgumentParser(description="Multiply a formant graph with a source sound.")
    parser.add_argument("input", help="Path to input audio file (wav, etc.)")
    parser.add_argument("output", help="Path to save the output audio file")
    parser.add_argument("--n_fft", type=int, default=2048, help="FFT window size")
    parser.add_argument("--hop_length", type=int, default=512, help="STFT hop length")
    args = parser.parse_args()

    # Step 1: Load source sound (mono, preserve original sample rate)
    y, sr = librosa.load(args.input, sr=None, mono=True)

    # Step 2-5: Apply the formant multiplication
    y_out = apply_formants(y, sr, FORMANTS, FLOOR, args.n_fft, args.hop_length)

    # Step 6: Normalize and save
    y_out = normalize(y_out)
    sf.write(args.output, y_out, sr)
    print(f"Saved formant-filtered audio to: {args.output}")


if __name__ == "__main__":
    main()