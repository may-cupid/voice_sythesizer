"""
Graph panel for the player window.

Layout inside player_window:
    left column : Play / Stop / Close, then Time domain / Spectrogram / Spectral envelope, status label
    right side  : matplotlib graph (shown through a pygame_gui UIImage)

Assumes you have the played sound as a numpy array `samples` (mono or stereo)
and its `sample_rate` in Hz.
"""

import matplotlib

matplotlib.use("Agg")  # render off-screen; pygame displays the result
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

import numpy as np
import pygame
import pygame_gui
from pygame import Rect

WINDOW_SECONDS = 0.20  # time range shown for time domain + spectrogram
DPI = 100


# --------------------------------------------------------------------------- #
# Plot helpers
# --------------------------------------------------------------------------- #
def _to_mono_float(samples):
    samples = np.asarray(samples, dtype=np.float64)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    return samples


def _new_figure(size):
    fig = Figure(figsize=(size[0] / DPI, size[1] / DPI), dpi=DPI)
    return fig, fig.add_subplot(111)


def _fig_to_surface(fig):
    fig.tight_layout()
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    w, h = canvas.get_width_height()
    surf = pygame.image.frombuffer(bytes(canvas.buffer_rgba()), (w, h), "RGBA")
    return surf.convert_alpha()


def plot_time_domain(samples, sample_rate, size):
    n = int(WINDOW_SECONDS * sample_rate)
    segment = samples[:n]
    t = np.arange(len(segment)) / sample_rate

    fig, ax = _new_figure(size)
    ax.plot(t, segment, linewidth=0.8)
    ax.set_xlim(0, WINDOW_SECONDS)
    # y axis spans the full amplitude range of the whole sound
    peak = float(np.max(np.abs(samples))) or 1.0
    ax.set_ylim(-peak * 1.05, peak * 1.05)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    ax.set_title("Time domain (0 - 0.20 s)")
    ax.grid(True, alpha=0.3)
    return _fig_to_surface(fig)


def plot_spectrogram(samples, sample_rate, size):
    n = int(WINDOW_SECONDS * sample_rate)
    nfft = 256
    segment = samples[:n]
    if len(segment) < nfft:  # specgram needs at least NFFT samples
        segment = np.pad(segment, (0, nfft - len(segment)))

    fig, ax = _new_figure(size)
    ax.specgram(
        segment, NFFT=nfft, Fs=sample_rate, noverlap=nfft * 3 // 4, cmap="magma"
    )
    ax.set_xlim(0, WINDOW_SECONDS)
    ax.set_ylim(0, sample_rate / 2)  # full frequency range up to Nyquist
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Frequency [Hz]")
    ax.set_title("Spectrogram (0 - 0.20 s)")
    return _fig_to_surface(fig)


def plot_spectral_envelope(samples, sample_rate, size, lifter=60):
    """Magnitude spectrum of the whole sound plus a cepstrally smoothed envelope."""
    n = len(samples)
    spectrum = np.abs(np.fft.rfft(samples * np.hanning(n))) + 1e-12
    log_spec = 20 * np.log10(spectrum)
    freqs = np.fft.rfftfreq(n, 1 / sample_rate)

    # cepstral smoothing: keep only the low quefrencies -> smooth envelope
    cepstrum = np.fft.irfft(log_spec)
    cepstrum[lifter:-lifter] = 0
    envelope = np.fft.rfft(cepstrum).real

    fig, ax = _new_figure(size)
    ax.plot(freqs, log_spec, color="0.7", linewidth=0.6, label="Spectrum")
    ax.plot(freqs, envelope, color="C3", linewidth=1.8, label="Spectral envelope")
    ax.set_xlim(0, sample_rate / 2)
    top = float(np.max(log_spec))
    ax.set_ylim(top - 100, top + 5)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Magnitude [dB]")
    ax.set_title("Spectral envelope")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")
    return _fig_to_surface(fig)


PLOTS = {
    "time": plot_time_domain,
    "spectrogram": plot_spectrogram,
    "envelope": plot_spectral_envelope,
}


# --------------------------------------------------------------------------- #
# Window contents
# --------------------------------------------------------------------------- #
class GraphPanel:
    """A UIImage inside the player window that can show any of the plots."""

    def __init__(self, manager, container, rect, samples, sample_rate):
        self.rect = rect
        self.samples = _to_mono_float(samples)
        self.sample_rate = sample_rate
        self.image = pygame_gui.elements.UIImage(
            relative_rect=rect,
            image_surface=pygame.Surface(rect.size, pygame.SRCALPHA),
            manager=manager,
            container=container,
        )

    def set_samples(self, samples, sample_rate):
        """Call this if a different sound gets loaded."""
        self.samples = _to_mono_float(samples)
        self.sample_rate = sample_rate

    def show(self, kind):
        surface = PLOTS[kind](self.samples, self.sample_rate, self.rect.size)
        self.image.set_image(surface)


def build_player_window_contents(
    manager, player_window, samples, sample_rate, play_audio, stop_audio, close_player
):
    """
    Fill `player_window` with: buttons stacked on the left, graph on the right.
    Returns (status_label, graph_panel).

    Suggested window size: Rect((50, 50), (1000, 600))
    """
    cw, ch = player_window.get_container().get_size()
    col_x, col_w, btn_h, gap = 20, 150, 40, 10

    def button(row, text, command):
        return pygame_gui.elements.UIButton(
            relative_rect=Rect((col_x, 20 + row * (btn_h + gap)), (col_w, btn_h)),
            text=text,
            manager=manager,
            container=player_window,
            command=command,
        )

    # --- audio controls (stacked on the left) ---
    button(0, "Play", play_audio)
    button(1, "Stop", stop_audio)
    button(2, "Close", close_player)

    # --- graph panel (right side) ---
    graph_left = col_x + col_w + 20
    graph_rect = Rect((graph_left, 20), (cw - graph_left - 20, ch - 40))
    graph_panel = GraphPanel(manager, player_window, graph_rect, samples, sample_rate)

    # --- graph selection buttons (still on the left, below the audio controls) ---
    button(4, "Time domain", lambda: graph_panel.show("time"))
    button(5, "Spectrogram", lambda: graph_panel.show("spectrogram"))
    button(6, "Spectral envelope", lambda: graph_panel.show("envelope"))

    # --- status label at the bottom of the left column ---
    status_label = pygame_gui.elements.UILabel(
        relative_rect=Rect((col_x, ch - 20 - 30), (col_w, 30)),
        text="Stopped",
        manager=manager,
        container=player_window,
    )

    graph_panel.show("time")  # default graph
    return status_label, graph_panel