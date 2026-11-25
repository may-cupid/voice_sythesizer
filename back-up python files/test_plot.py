"""
Simple pygame + pygame_gui window that can display a matplotlib graph.

Install:
    pip install pygame pygame_gui matplotlib numpy

Run:
    python matplotlib_in_pygame.py
"""

import matplotlib

matplotlib.use("Agg")  # render off-screen, we draw the result with pygame
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

import numpy as np
import pygame
import pygame_gui

WINDOW_SIZE = (900, 650)
PLOT_RECT = pygame.Rect(20, 70, 860, 560)


def figure_to_surface(fig: Figure) -> pygame.Surface:
    """Render a matplotlib figure and convert it to a pygame surface."""
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    width, height = canvas.get_width_height()
    return pygame.image.frombuffer(bytes(canvas.buffer_rgba()), (width, height), "RGBA").convert_alpha()


def make_graph(kind: int, size: tuple[int, int]) -> pygame.Surface:
    """Create one of a few example graphs and return it as a surface."""
    dpi = 100
    fig = Figure(figsize=(size[0] / dpi, size[1] / dpi), dpi=dpi)
    ax = fig.add_subplot(111)

    x = np.linspace(0, 10, 200)
    if kind == 0:
        ax.plot(x, np.sin(x), label="sin(x)")
        ax.plot(x, np.cos(x), label="cos(x)")
        ax.set_title("Line plot")
        ax.legend()
    elif kind == 1:
        rng = np.random.default_rng()
        ax.scatter(rng.normal(size=150), rng.normal(size=150), alpha=0.7)
        ax.set_title("Random scatter plot")
    else:
        ax.bar(["A", "B", "C", "D"], np.random.randint(1, 10, size=4))
        ax.set_title("Random bar chart")

    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return figure_to_surface(fig)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Matplotlib in pygame")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    manager = pygame_gui.UIManager(WINDOW_SIZE)
    background = pygame.Surface(WINDOW_SIZE)
    background.fill(manager.get_theme().get_colour("dark_bg"))

    show_button = pygame_gui.elements.UIButton(
        pygame.Rect(20, 20, 160, 35), "Show / next graph", manager
    )
    hide_button = pygame_gui.elements.UIButton(
        pygame.Rect(190, 20, 120, 35), "Hide graph", manager
    )

    # Image element that holds the matplotlib graph (starts empty).
    graph_image = pygame_gui.elements.UIImage(
        PLOT_RECT, pygame.Surface(PLOT_RECT.size, pygame.SRCALPHA), manager
    )
    empty_surface = pygame.Surface(PLOT_RECT.size, pygame.SRCALPHA)

    graph_index = 0
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == show_button:
                    graph_image.set_image(make_graph(graph_index % 3, PLOT_RECT.size))
                    graph_index += 1
                elif event.ui_element == hide_button:
                    graph_image.set_image(empty_surface)

            manager.process_events(event)

        manager.update(time_delta)
        screen.blit(background, (0, 0))
        manager.draw_ui(screen)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()