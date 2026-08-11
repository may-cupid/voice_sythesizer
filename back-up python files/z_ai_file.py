"""
Voice Synthesis UI — pygame
A minimal but functional interface based on a hand-drawn sketch.

Controls:
  Left click    interact with buttons, sliders, list items
  Mouse wheel   scroll the right panel (effects / advanced / info)
  Space         play / pause in the player view
  Esc           close player view, or quit app
"""
import math
import random
from dataclasses import dataclass
from typing import List, Tuple

import pygame

SEED = 42
random.seed(SEED)

WIDTH, HEIGHT = 960, 640
FPS = 60

# Palette — minimal dark, color-blind safe
BG           = (22, 24, 30)
PANEL        = (32, 35, 44)
PANEL_2      = (40, 44, 56)
BUTTON_BG    = (50, 54, 68)
BUTTON_HOVER = (66, 72, 92)
ACCENT       = (90, 130, 220)
ACCENT_DIM   = (55, 80, 140)
ACCENT_2     = (60, 180, 160)
TEXT         = (225, 228, 236)
TEXT_DIM     = (135, 140, 156)
DIVIDER      = (58, 63, 78)
WAVE_COL     = (110, 200, 240)


def lerp(a, b, t): return a + (b - a) * t
def clamp(v, lo, hi): return max(lo, min(hi, v))
def ease_out_cubic(t): return 1 - (1 - t) ** 3


# ------------------------------------------------------------------ Slider
@dataclass
class Slider:
    x: int = 0
    y: int = 0
    w: int = 200
    min_val: float = 0
    max_val: float = 100
    value: float = 0
    label: str = ""
    unit: str = ""
    dragging: bool = False

    def track_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y + 11, self.w, 4)

    def handle_pos(self) -> Tuple[int, int]:
        t = (self.value - self.min_val) / max(1e-9, self.max_val - self.min_val)
        return (self.x + int(t * self.w), self.y + 13)

    def pick_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - 6, self.y + 2, self.w + 12, 22)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx, hy = self.handle_pos()
            hit_handle = (event.pos[0] - hx) ** 2 + (event.pos[1] - hy) ** 2 < 100
            if hit_handle or self.pick_rect().collidepoint(event.pos):
                self.dragging = True
                self._set_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos[0])
            return True
        return False

    def _set_from_mouse(self, mx: int):
        t = clamp((mx - self.x) / max(1, self.w), 0, 1)
        self.value = self.min_val + t * (self.max_val - self.min_val)

    def draw(self, surf, font_sm, font_xs):
        if self.label:
            lbl = font_xs.render(self.label, True, TEXT_DIM)
            surf.blit(lbl, (self.x, self.y - 16))
        if float(self.value).is_integer():
            vstr = f"{int(self.value)}{self.unit}"
        else:
            vstr = f"{self.value:.1f}{self.unit}"
        vs = font_xs.render(vstr, True, TEXT)
        surf.blit(vs, (self.x + self.w - vs.get_width(), self.y - 16))
        pygame.draw.rect(surf, DIVIDER, self.track_rect(), border_radius=2)
        t = (self.value - self.min_val) / max(1e-9, self.max_val - self.min_val)
        fw = int(t * self.w)
        if fw > 0:
            pygame.draw.rect(surf, ACCENT, (self.x, self.y + 11, fw, 4), border_radius=2)
        hx = self.x + fw
        pygame.draw.circle(surf, TEXT, (hx, self.y + 13), 7)
        pygame.draw.circle(surf, ACCENT, (hx, self.y + 13), 5)


# ------------------------------------------------------------------ Button
@dataclass
class TextButton:
    rect: pygame.Rect
    label: str = ""
    sublabel: str = ""
    active: bool = False
    hover_t: float = 0.0

    def update(self, dt, mouse_pos):
        target = 1.0 if self.rect.collidepoint(mouse_pos) else 0.0
        self.hover_t += (target - self.hover_t) * min(1.0, dt * 12)

    def draw(self, surf, font, font_sm):
        if self.active:
            bg = ACCENT; txt_col = (255, 255, 255); sub_col = (220, 230, 250)
        else:
            bg = (int(lerp(BUTTON_BG[0], BUTTON_HOVER[0], self.hover_t)),
                  int(lerp(BUTTON_BG[1], BUTTON_HOVER[1], self.hover_t)),
                  int(lerp(BUTTON_BG[2], BUTTON_HOVER[2], self.hover_t)))
            txt_col = TEXT
            sub_col = ACCENT_2 if self.sublabel else TEXT_DIM
        pygame.draw.rect(surf, bg, self.rect, border_radius=6)
        if self.active:
            pygame.draw.rect(surf, ACCENT_2,
                             (self.rect.x, self.rect.y, 3, self.rect.h), border_radius=2)
        lbl = font.render(self.label, True, txt_col)
        surf.blit(lbl, (self.rect.x + 16,
                        self.rect.y + (self.rect.h - lbl.get_height()) // 2))
        if self.sublabel:
            ss = font_sm.render(self.sublabel, True, sub_col)
            surf.blit(ss, (self.rect.right - ss.get_width() - 16,
                           self.rect.y + (self.rect.h - ss.get_height()) // 2))

    def clicked(self, pos): return self.rect.collidepoint(pos)


# ------------------------------------------------------------------ App
class VoiceSynthApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Voice Synthesis")
        self.clock = pygame.time.Clock()

        try:
            self.font_xs = pygame.font.SysFont("dejavusans,arial", 11)
            self.font_sm = pygame.font.SysFont("dejavusans,arial", 13)
            self.font    = pygame.font.SysFont("dejavusans,arial", 15)
            self.font_md = pygame.font.SysFont("dejavusans,arial", 17)
            self.font_lg = pygame.font.SysFont("dejavusans,arial", 22, bold=True)
        except Exception:
            self.font_xs = pygame.font.Font(None, 14)
            self.font_sm = pygame.font.Font(None, 16)
            self.font    = pygame.font.Font(None, 18)
            self.font_md = pygame.font.Font(None, 20)
            self.font_lg = pygame.font.Font(None, 24)

        # State
        self.current_tab = 'vowel'
        self.selected_vowel = 'A'
        self.selected_trait = 'M'
        self.pitch = 200.0
        self.show_player = False

        # Formant presets (F, BW in Hz) — Peterson-Barney-ish
        self.formant_presets = {
            ('A','M'): [(730,130),(1090,160),(2440,240)],
            ('E','M'): [(530,100),(1840,110),(2480,140)],
            ('I','M'): [(270, 80),(2290,100),(3010,120)],
            ('O','M'): [(570,100),( 840,100),(2410,160)],
            ('U','M'): [(300, 90),( 870,100),(2240,160)],
            ('A','F'): [(850,120),(1220,140),(2810,220)],
            ('E','F'): [(610,100),(2330,120),(2990,160)],
            ('I','F'): [(320,100),(2730,110),(3140,200)],
            ('O','F'): [(590, 90),( 920,100),(2710,180)],
            ('U','F'): [(370, 90),( 950,100),(2670,170)],
        }
        self.formants = list(self.formant_presets[('A','M')])

        # Effects (expandable inline sliders)
        self.effects = [
            {"name":"Vibrato",    "value":80.0,"min":0,"max":100,"expanded":False,"unit":"%"},
            {"name":"Reverb",     "value":30.0,"min":0,"max":100,"expanded":False,"unit":"%"},
            {"name":"Tremolo",    "value": 0.0,"min":0,"max":100,"expanded":False,"unit":"%"},
            {"name":"Echo",       "value": 0.0,"min":0,"max":100,"expanded":False,"unit":"%"},
            {"name":"Distortion", "value": 0.0,"min":0,"max":100,"expanded":False,"unit":"%"},
            {"name":"Chorus",     "value": 0.0,"min":0,"max":100,"expanded":False,"unit":"%"},
            {"name":"Flanger",    "value": 0.0,"min":0,"max":100,"expanded":False,"unit":"%"},
            {"name":"Pitch Shift","value": 0.0,"min":-12,"max":12,"expanded":False,"unit":"st"},
            {"name":"Noise",      "value": 0.0,"min":0,"max":100,"expanded":False,"unit":"%"},
            {"name":"Breathiness","value": 0.0,"min":0,"max":100,"expanded":False,"unit":"%"},
        ]
        self.effect_sliders = {
            e["name"]: Slider(0,0,500,e["min"],e["max"],e["value"],e["name"],e["unit"])
            for e in self.effects
        }
        self.effects_scroll = 0.0
        self.effects_scroll_target = 0.0

        self.pitch_slider = Slider(0,0,580,50,500,self.pitch,"Pitch","Hz")

        self.adv_sliders = []
        for i in range(3):
            fs = Slider(0,0,270,100,4000,self.formants[i][0],f"F{i+1} Frequency","Hz")
            bs = Slider(0,0,270, 20, 500,self.formants[i][1],f"BW{i+1}","Hz")
            self.adv_sliders.append((fs,bs))
        self.advanced_scroll = 0.0
        self.advanced_scroll_target = 0.0

        self.info_scroll = 0.0
        self.info_scroll_target = 0.0
        self.info_text = [
            ("Voice Synthesis — Reference Guide", True),
            ("", False),
            ("This is a formant-based voice synthesizer. Each vowel is", False),
            ("shaped by resonant peaks (formants) in the vocal tract.", False),
            ("", False),
            ("VOWELS", True),
            ("Select from A, E, I, O, U. Each vowel has characteristic", False),
            ("formant frequencies F1, F2, F3.", False),
            ("", False),
            ("TRAITS", True),
            ("Male — lower formants, deeper voice (~120 Hz F0).", False),
            ("Female — higher formants, brighter voice (~220 Hz F0).", False),
            ("", False),
            ("PITCH", True),
            ("Fundamental frequency (F0) in Hertz.", False),
            ("Typical range: 50–500 Hz.", False),
            ("", False),
            ("EFFECTS", True),
            ("Vibrato: periodic pitch modulation (5–7 Hz).", False),
            ("Reverb: room ambience simulation.", False),
            ("Tremolo: amplitude modulation.", False),
            ("Echo: delayed repetition.", False),
            ("Distortion: harmonic saturation.", False),
            ("Chorus: layered detuned copies.", False),
            ("Flanger: comb-filter modulation.", False),
            ("Pitch Shift: transpose in semitones.", False),
            ("Noise: additive broadband noise.", False),
            ("Breathiness: aspiration noise.", False),
            ("", False),
            ("ADVANCED", True),
            ("Manually edit formant frequencies (F1–F3)", False),
            ("and their bandwidths (BW1–BW3).", False),
            ("", False),
            ("PLAYER", True),
            ("Click PLAY to synthesize. The player view shows", False),
            ("the waveform. Use Loop / Play / Stop to control", False),
            ("playback. Click DONE to return.", False),
            ("", False),
            ("Scroll this panel with the mouse wheel.", False),
            ("Press ESC to quit.", False),
        ]

        # Layout
        self.top_rect    = pygame.Rect(0, 0, WIDTH, 50)
        self.bottom_rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)
        self.left_rect   = pygame.Rect(0, 50, 280, HEIGHT - 100)

        self.left_buttons: List[TextButton] = []
        self._rebuild_left_buttons()

        # Player state
        self.player_playing = False
        self.player_looping = True
        self.player_time = 0.0
        self.player_duration = 3.0
        self.player_transition = 0.0
        self._player_surf = pygame.Surface((WIDTH, HEIGHT))

        self.wave_samples = self._generate_waveform()
        self.mouse_pos = (0, 0)

        # Rects filled in by draw
        self._info_rect = pygame.Rect(0,0,0,0)
        self._export_rect = pygame.Rect(0,0,0,0)
        self._play_rect = pygame.Rect(0,0,0,0)
        self._player_loop_rect = pygame.Rect(0,0,0,0)
        self._player_stop_rect = pygame.Rect(0,0,0,0)
        self._player_play_rect = pygame.Rect(0,0,0,0)
        self._player_done_rect = pygame.Rect(0,0,0,0)

    # ----- helpers -----
    def _rebuild_left_buttons(self):
        labels = [
            ("SELECT VOWEL", self.selected_vowel,        'vowel'),
            ("TRAITS",       self.selected_trait,        'traits'),
            ("SET PITCH",    f"{int(self.pitch)}Hz",     'pitch'),
            ("EFFECTS",      "",                         'effects'),
            ("ADVANCED",     "",                         'advanced'),
        ]
        if not self.left_buttons:
            y = 80
            for label, sub, key in labels:
                self.left_buttons.append(TextButton(pygame.Rect(20, y, 240, 56), label, sub))
                y += 64
        for btn, (label, sub, key) in zip(self.left_buttons, labels):
            btn.label = label
            btn.sublabel = sub
            btn.active = (self.current_tab == key)

    def _generate_waveform(self) -> List[float]:
        """Glottal pulse train × formant cosines — visually voice-like."""
        N = 800
        f0 = self.pitch
        formants = self.formants
        vib  = self.effects[0]["value"] / 100.0
        rev  = self.effects[1]["value"] / 100.0
        trem = self.effects[2]["value"] / 100.0
        duration = 0.06   # 60 ms visible
        sr = N / duration
        samples = []
        for i in range(N):
            tt = i / sr
            vib_f = f0 * (1 + 0.05 * vib * math.sin(2*math.pi*5.5*tt/duration))
            # Pulse train — sum of nearby Gaussian pulses
            s = 0.0
            n_pulse = int(tt * vib_f)
            for p in range(max(0, n_pulse-1), n_pulse+2):
                pt = p / vib_f
                s += math.exp(-((tt - pt) ** 2) / 5e-8)
            # Formant resonance sum
            fs = 0.0
            for j, (f, bw) in enumerate(formants):
                amp = 1.0 / (j + 1)
                fs += amp * math.cos(2*math.pi*f*tt)
            s *= fs
            if trem > 0:
                s *= 1 - trem*0.5 + trem*0.5*math.sin(2*math.pi*8*tt/duration)
            samples.append(s)
        if rev > 0:
            delay = max(1, int(sr * 0.01))
            for i in range(delay, N):
                samples[i] += rev * 0.35 * samples[i - delay]
        mx = max((abs(s) for s in samples), default=1) or 1
        return [s / mx for s in samples]

    # ----- update -----
    def update(self, dt):
        self.mouse_pos = pygame.mouse.get_pos()
        for btn in self.left_buttons:
            btn.update(dt, self.mouse_pos)

        self.effects_scroll  += (self.effects_scroll_target  - self.effects_scroll)  * min(1.0, dt*12)
        self.advanced_scroll += (self.advanced_scroll_target - self.advanced_scroll) * min(1.0, dt*12)
        self.info_scroll     += (self.info_scroll_target     - self.info_scroll)     * min(1.0, dt*12)

        target_p = 1.0 if self.show_player else 0.0
        self.player_transition += (target_p - self.player_transition) * min(1.0, dt*10)

        if self.show_player and self.player_playing:
            self.player_time += dt
            if self.player_time >= self.player_duration:
                if self.player_looping:
                    self.player_time = 0.0
                else:
                    self.player_time = self.player_duration
                    self.player_playing = False

        self._layout_sliders()
        self.pitch_slider.value = self.pitch
        for e in self.effects:
            self.effect_sliders[e["name"]].value = e["value"]
        for i, (fs, bs) in enumerate(self.adv_sliders):
            fs.value = self.formants[i][0]
            bs.value = self.formants[i][1]

    def _layout_sliders(self):
        self.pitch_slider.x = 320; self.pitch_slider.y = 200; self.pitch_slider.w = 580
        y = 150; item_h = 36; slider_h = 50
        for e in self.effects:
            if e["expanded"]:
                s = self.effect_sliders[e["name"]]
                s.x = 360
                s.y = y - int(self.effects_scroll) + item_h + 18
                s.w = 500
                y += slider_h
            y += item_h + 4
        y = 150
        for i, (fs, bs) in enumerate(self.adv_sliders):
            fs.x = 320; fs.y = y - int(self.advanced_scroll) + 22 + 18; fs.w = 270
            bs.x = 620; bs.y = y - int(self.advanced_scroll) + 22 + 18; bs.w = 270
            y += 22 + 60 + 16

    # ----- draw -----
    def draw(self):
        self.screen.fill(BG)
        t = ease_out_cubic(self.player_transition)
        if t < 0.99:
            self._draw_main()
        if t > 0.01:
            self._draw_player_on(self._player_surf)
            self._player_surf.set_alpha(int(255 * t))
            self.screen.blit(self._player_surf, (0, 0))
        pygame.display.flip()

    def _draw_main(self):
        # Top bar
        pygame.draw.rect(self.screen, PANEL, self.top_rect)
        pygame.draw.line(self.screen, DIVIDER, (0, 50), (WIDTH, 50))
        title = self.font_md.render("voice synthesis", True, TEXT)
        self.screen.blit(title, (20, (50 - title.get_height()) // 2))

        # Info button
        info_rect = pygame.Rect(WIDTH - 110, 10, 90, 30)
        info_hover = info_rect.collidepoint(self.mouse_pos)
        info_active = self.current_tab == 'info'
        if info_active:        bg = ACCENT; tc = (255,255,255)
        elif info_hover:       bg = BUTTON_HOVER; tc = TEXT
        else:                  bg = BUTTON_BG; tc = TEXT
        pygame.draw.rect(self.screen, bg, info_rect, border_radius=4)
        txt = self.font_sm.render("ⓘ  INFO", True, tc)
        self.screen.blit(txt, (info_rect.centerx - txt.get_width()//2,
                               info_rect.centery - txt.get_height()//2))
        self._info_rect = info_rect

        # Left panel
        pygame.draw.rect(self.screen, PANEL, self.left_rect)
        pygame.draw.line(self.screen, DIVIDER, (280, 50), (280, HEIGHT - 50))
        sec = self.font_xs.render("PARAMETERS", True, TEXT_DIM)
        self.screen.blit(sec, (20, 60))
        for btn in self.left_buttons:
            btn.draw(self.screen, self.font, self.font_sm)

        # Right panel content
        if   self.current_tab == 'vowel':    self._draw_vowel_panel()
        elif self.current_tab == 'traits':   self._draw_traits_panel()
        elif self.current_tab == 'pitch':    self._draw_pitch_panel()
        elif self.current_tab == 'effects':  self._draw_effects_panel()
        elif self.current_tab == 'advanced': self._draw_advanced_panel()
        elif self.current_tab == 'info':     self._draw_info_panel()

        # Bottom bar
        pygame.draw.rect(self.screen, PANEL, self.bottom_rect)
        pygame.draw.line(self.screen, DIVIDER, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50))
        export_rect = pygame.Rect(20, HEIGHT - 40, 120, 30)
        play_rect   = pygame.Rect(WIDTH - 140, HEIGHT - 40, 120, 30)
        eh = export_rect.collidepoint(self.mouse_pos)
        ph = play_rect.collidepoint(self.mouse_pos)
        pygame.draw.rect(self.screen, BUTTON_HOVER if eh else BUTTON_BG, export_rect, border_radius=4)
        ex = self.font_sm.render("EXPORT", True, TEXT)
        self.screen.blit(ex, (export_rect.centerx - ex.get_width()//2,
                              export_rect.centery - ex.get_height()//2))
        pygame.draw.rect(self.screen, ACCENT if ph else ACCENT_DIM, play_rect, border_radius=4)
        pl = self.font_sm.render("▶  PLAY", True, (255,255,255))
        self.screen.blit(pl, (play_rect.centerx - pl.get_width()//2,
                              play_rect.centery - pl.get_height()//2))
        self._export_rect = export_rect
        self._play_rect = play_rect

    def _draw_panel_header(self, title, subtitle=""):
        t = self.font_lg.render(title, True, TEXT)
        self.screen.blit(t, (320, 75))
        if subtitle:
            s = self.font_sm.render(subtitle, True, TEXT_DIM)
            self.screen.blit(s, (320, 105))
        pygame.draw.line(self.screen, DIVIDER, (320, 132), (WIDTH - 40, 132), 1)

    def _draw_vowel_panel(self):
        self._draw_panel_header("Select Vowel", "Choose a vowel to synthesize.")
        vowels = ['A','E','I','O','U']
        x = 320; y = 160; size = 100; gap = 18
        for v in vowels:
            r = pygame.Rect(x, y, size, size)
            hover = r.collidepoint(self.mouse_pos)
            sel = self.selected_vowel == v
            if sel:
                pygame.draw.rect(self.screen, ACCENT, r, border_radius=10)
                pygame.draw.rect(self.screen, ACCENT_2, r.inflate(-6,-6), 2, border_radius=8)
                tc = (255,255,255)
            else:
                pygame.draw.rect(self.screen, BUTTON_HOVER if hover else BUTTON_BG, r, border_radius=10)
                pygame.draw.rect(self.screen, DIVIDER, r, 1, border_radius=10)
                tc = TEXT
            vt = self.font_lg.render(v, True, tc)
            self.screen.blit(vt, (r.centerx - vt.get_width()//2,
                                  r.centery - vt.get_height()//2))
            x += size + gap
        descriptions = {
            'A':"Open front unrounded — 'father'",
            'E':"Mid front unrounded — 'bed'",
            'I':"Close front unrounded — 'machine'",
            'O':"Mid back rounded — 'more'",
            'U':"Close back rounded — 'rule'",
        }
        d = self.font_sm.render(descriptions[self.selected_vowel], True, TEXT_DIM)
        self.screen.blit(d, (320, 290))
        preset = self.formant_presets[(self.selected_vowel, self.selected_trait)]
        f_txt = self.font_xs.render(
            f"Current formants (trait {self.selected_trait}):  F1={preset[0][0]}  F2={preset[1][0]}  F3={preset[2][0]}",
            True, ACCENT_2)
        self.screen.blit(f_txt, (320, 315))

    def _draw_traits_panel(self):
        self._draw_panel_header("Traits", "Pick a formant preset for the selected vowel.")
        opts = [('M','Male',"Lower formants, deeper voice"),
                ('F','Female',"Higher formants, brighter voice")]
        x = 320; y = 160; w = 280; h = 140
        for key, label, desc in opts:
            r = pygame.Rect(x, y, w, h)
            hover = r.collidepoint(self.mouse_pos)
            sel = self.selected_trait == key
            if sel:
                pygame.draw.rect(self.screen, ACCENT, r, border_radius=10)
                pygame.draw.rect(self.screen, ACCENT_2, r.inflate(-6,-6), 2, border_radius=8)
                tc = (255,255,255); sc = (220,230,250)
            else:
                pygame.draw.rect(self.screen, BUTTON_HOVER if hover else BUTTON_BG, r, border_radius=10)
                pygame.draw.rect(self.screen, DIVIDER, r, 1, border_radius=10)
                tc = TEXT; sc = TEXT_DIM
            lt = self.font_md.render(label, True, tc)
            self.screen.blit(lt, (r.x + 18, r.y + 18))
            dt = self.font_sm.render(desc, True, sc)
            self.screen.blit(dt, (r.x + 18, r.y + 50))
            preset = self.formant_presets[(self.selected_vowel, key)]
            f_txt = self.font_xs.render(
                f"F1={preset[0][0]}  F2={preset[1][0]}  F3={preset[2][0]}", True, sc)
            self.screen.blit(f_txt, (r.x + 18, r.y + 80))
            # mini waveform hint
            icon_y = r.y + 110
            for ix in range(0, w - 36, 5):
                hh = int(7 * math.sin(ix * 0.18 + (0 if key == 'M' else 1.5)))
                pygame.draw.line(self.screen, sc,
                                 (r.x + 18 + ix, icon_y + hh),
                                 (r.x + 18 + ix, icon_y - hh), 1)
            x += w + 20

    def _draw_pitch_panel(self):
        self._draw_panel_header("Set Pitch", "Fundamental frequency (F0).")
        self.pitch_slider.draw(self.screen, self.font_sm, self.font_xs)
        presets = [("Bass",80),("Male",120),("Female",220),("Child",300)]
        x = 320; y = 260
        for label, val in presets:
            r = pygame.Rect(x, y, 130, 50)
            hover = r.collidepoint(self.mouse_pos)
            sel = abs(self.pitch - val) < 1
            if sel:
                pygame.draw.rect(self.screen, ACCENT, r, border_radius=6)
                tc = (255,255,255); sc = (220,230,250)
            else:
                pygame.draw.rect(self.screen, BUTTON_HOVER if hover else BUTTON_BG, r, border_radius=6)
                pygame.draw.rect(self.screen, DIVIDER, r, 1, border_radius=6)
                tc = TEXT; sc = TEXT_DIM
            lt = self.font_sm.render(label, True, tc)
            self.screen.blit(lt, (r.centerx - lt.get_width()//2, r.y + 8))
            vt = self.font_xs.render(f"{val} Hz", True, sc)
            self.screen.blit(vt, (r.centerx - vt.get_width()//2, r.y + 28))
            x += 140
        note = self.font_sm.render(f"Current pitch: {int(self.pitch)} Hz", True, ACCENT_2)
        self.screen.blit(note, (320, 340))

    def _draw_effects_panel(self):
        self._draw_panel_header("Effects",
                                "Click a parameter to expand its slider. Scroll for more.")
        clip_top = 145; clip_bottom = HEIGHT - 60
        clip_rect = pygame.Rect(280, clip_top, WIDTH - 280, clip_bottom - clip_top)
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)

        y = 150 - int(self.effects_scroll); item_h = 36; slider_h = 50
        for e in self.effects:
            r = pygame.Rect(320, y, 580, item_h)
            if y + item_h > clip_top and y < clip_bottom:
                hover = r.collidepoint(self.mouse_pos) and clip_rect.collidepoint(self.mouse_pos)
                pygame.draw.rect(self.screen, BUTTON_HOVER if hover else BUTTON_BG, r, border_radius=6)
                chev = "▼" if e["expanded"] else "▶"
                ct = self.font_sm.render(chev, True, TEXT_DIM)
                self.screen.blit(ct, (r.x + 12, r.y + (r.h - ct.get_height())//2))
                nt = self.font.render(e["name"], True, TEXT)
                self.screen.blit(nt, (r.x + 36, r.y + (r.h - nt.get_height())//2))
                vstr = f"{e['value']:.1f}{e['unit']}"
                vt = self.font_sm.render(vstr, True, ACCENT_2)
                self.screen.blit(vt, (r.right - vt.get_width() - 16,
                                      r.y + (r.h - vt.get_height())//2))
            y += item_h
            if e["expanded"]:
                if y + slider_h > clip_top and y < clip_bottom:
                    self.effect_sliders[e["name"]].draw(self.screen, self.font_sm, self.font_xs)
                y += slider_h
            y += 4
        self.screen.set_clip(prev_clip)

        total_h = sum(item_h + 4 + (slider_h if e["expanded"] else 0) for e in self.effects)
        visible_h = clip_bottom - clip_top - 10
        if total_h > visible_h:
            self._draw_scrollbar(WIDTH - 14, clip_top + 5, visible_h,
                                 visible_h / total_h,
                                 self.effects_scroll / (total_h - visible_h))

    def _draw_advanced_panel(self):
        self._draw_panel_header("Advanced", "Manually adjust formant frequencies and bandwidths.")
        preset_txt = self.font_sm.render(
            f"Preset: Vowel '{self.selected_vowel}' / Trait '{self.selected_trait}'",
            True, ACCENT_2)
        self.screen.blit(preset_txt, (320, 110))
        clip_top = 145; clip_bottom = HEIGHT - 60
        clip_rect = pygame.Rect(280, clip_top, WIDTH - 280, clip_bottom - clip_top)
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)
        y = 150 - int(self.advanced_scroll)
        for i, (fs, bs) in enumerate(self.adv_sliders):
            if y + 90 > clip_top and y < clip_bottom:
                head = self.font_sm.render(f"Formant {i+1}", True, TEXT_DIM)
                self.screen.blit(head, (320, y))
                fs.draw(self.screen, self.font_sm, self.font_xs)
                bs.draw(self.screen, self.font_sm, self.font_xs)
                pygame.draw.line(self.screen, DIVIDER, (320, y + 80), (900, y + 80), 1)
            y += 22 + 60 + 16
        self.screen.set_clip(prev_clip)

    def _draw_info_panel(self):
        self._draw_panel_header("Information", "Scroll to read.")
        clip_top = 145; clip_bottom = HEIGHT - 60
        clip_rect = pygame.Rect(280, clip_top, WIDTH - 280, clip_bottom - clip_top)
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)
        y = 150 - int(self.info_scroll)
        total_h = 0
        for text, is_header in self.info_text:
            f = self.font_md if is_header else self.font_sm
            t_surf = f.render(text, True, ACCENT_2 if is_header else TEXT)
            if y + t_surf.get_height() > clip_top and y < clip_bottom:
                self.screen.blit(t_surf, (320, y))
            y += t_surf.get_height() + 4
            total_h += t_surf.get_height() + 4
        self.screen.set_clip(prev_clip)
        visible_h = clip_bottom - clip_top - 10
        if total_h > visible_h:
            self._draw_scrollbar(WIDTH - 14, clip_top + 5, visible_h,
                                 visible_h / total_h,
                                 self.info_scroll / (total_h - visible_h))

    def _draw_scrollbar(self, x, y, track_h, thumb_ratio, thumb_t):
        pygame.draw.rect(self.screen, DIVIDER, (x, y, 4, track_h), border_radius=2)
        thumb_h = max(30, int(track_h * thumb_ratio))
        thumb_y = y + int(thumb_t * (track_h - thumb_h))
        pygame.draw.rect(self.screen, ACCENT, (x, thumb_y, 4, thumb_h), border_radius=2)

    # ----- player -----
    def _draw_player_on(self, surf):
        surf.fill(BG)
        # Title bar
        pygame.draw.rect(surf, PANEL, (0, 0, WIDTH, 60))
        pygame.draw.line(surf, DIVIDER, (0, 60), (WIDTH, 60))
        title = self.font_md.render("voice synthesis player", True, TEXT)
        surf.blit(title, (24, (60 - title.get_height()) // 2))

        # Waveform area
        wf_rect = pygame.Rect(40, 100, WIDTH - 80, HEIGHT - 220)
        pygame.draw.rect(surf, PANEL_2, wf_rect, border_radius=8)
        pygame.draw.rect(surf, DIVIDER, wf_rect, 1, border_radius=8)
        for gx in range(wf_rect.left + 40, wf_rect.right, 40):
            pygame.draw.line(surf, (40, 44, 56), (gx, wf_rect.top + 2), (gx, wf_rect.bottom - 2), 1)
        for gy in range(wf_rect.top + 40, wf_rect.bottom, 40):
            pygame.draw.line(surf, (40, 44, 56), (wf_rect.left + 2, gy), (wf_rect.right - 2, gy), 1)
        pygame.draw.line(surf, DIVIDER,
                         (wf_rect.left, wf_rect.centery), (wf_rect.right, wf_rect.centery), 1)

        samples = self.wave_samples
        n = len(samples)
        if n > 1:
            pts = []
            for i, s in enumerate(samples):
                x = wf_rect.left + int(i * wf_rect.width / n)
                y = wf_rect.centery - int(s * wf_rect.height * 0.4)
                pts.append((x, y))
            if len(pts) > 1:
                pygame.draw.aalines(surf, WAVE_COL, False, pts)

        prog = self.player_time / self.player_duration if self.player_duration > 0 else 0
        ph_x = wf_rect.left + int(prog * wf_rect.width)
        pygame.draw.line(surf, ACCENT_2, (ph_x, wf_rect.top), (ph_x, wf_rect.bottom), 2)

        time_txt = self.font_xs.render(
            f"{self.player_time:.2f}s / {self.player_duration:.2f}s", True, TEXT_DIM)
        surf.blit(time_txt, (wf_rect.left, wf_rect.bottom + 8))
        info_txt = self.font_xs.render(
            f"Vowel: {self.selected_vowel}   Trait: {self.selected_trait}   F0: {int(self.pitch)} Hz",
            True, TEXT_DIM)
        surf.blit(info_txt, (wf_rect.right - info_txt.get_width(), wf_rect.bottom + 8))

        # Controls
        ctrl_y = HEIGHT - 90
        loop_rect = pygame.Rect(WIDTH//2 - 220, ctrl_y, 100, 40)
        stop_rect = pygame.Rect(WIDTH//2 - 110, ctrl_y, 100, 40)
        play_rect = pygame.Rect(WIDTH//2,       ctrl_y, 100, 40)
        done_rect = pygame.Rect(WIDTH - 140,    ctrl_y, 100, 40)

        mp = self.mouse_pos
        lh = loop_rect.collidepoint(mp)
        bg = ACCENT if self.player_looping else (BUTTON_HOVER if lh else BUTTON_BG)
        pygame.draw.rect(surf, bg, loop_rect, border_radius=6)
        lt = self.font_sm.render("↻ LOOP", True,
                                 (255,255,255) if self.player_looping else TEXT)
        surf.blit(lt, (loop_rect.centerx - lt.get_width()//2,
                       loop_rect.centery - lt.get_height()//2))

        sh = stop_rect.collidepoint(mp)
        pygame.draw.rect(surf, BUTTON_HOVER if sh else BUTTON_BG, stop_rect, border_radius=6)
        st = self.font_sm.render("■ STOP", True, TEXT)
        surf.blit(st, (stop_rect.centerx - st.get_width()//2,
                       stop_rect.centery - st.get_height()//2))

        ph = play_rect.collidepoint(mp)
        pygame.draw.rect(surf, ACCENT if ph else ACCENT_DIM, play_rect, border_radius=6)
        pt_label = "❚❚ PAUSE" if self.player_playing else "▶ PLAY"
        pt = self.font_sm.render(pt_label, True, (255,255,255))
        surf.blit(pt, (play_rect.centerx - pt.get_width()//2,
                       play_rect.centery - pt.get_height()//2))

        dh = done_rect.collidepoint(mp)
        pygame.draw.rect(surf, BUTTON_HOVER if dh else BUTTON_BG, done_rect, border_radius=6)
        pygame.draw.rect(surf, ACCENT_2, done_rect, 2, border_radius=6)
        dt = self.font_sm.render("DONE", True, TEXT)
        surf.blit(dt, (done_rect.centerx - dt.get_width()//2,
                       done_rect.centery - dt.get_height()//2))

        self._player_loop_rect = loop_rect
        self._player_stop_rect = stop_rect
        self._player_play_rect = play_rect
        self._player_done_rect = done_rect

    # ----- events -----
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.show_player:
                    self.show_player = False
                    return True
                return False
            if event.key == pygame.K_SPACE and self.show_player:
                self.player_playing = not self.player_playing
                if self.player_playing and self.player_time >= self.player_duration:
                    self.player_time = 0
                return True

        # Block main UI while player is open or transitioning
        if self.show_player or self.player_transition > 0.1:
            if self.show_player and self.player_transition > 0.5:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._player_done_rect.collidepoint(event.pos):
                        self.show_player = False
                        return True
                    if self._player_play_rect.collidepoint(event.pos):
                        if self.player_time >= self.player_duration:
                            self.player_time = 0
                        self.player_playing = not self.player_playing
                        return True
                    if self._player_stop_rect.collidepoint(event.pos):
                        self.player_playing = False
                        self.player_time = 0
                        return True
                    if self._player_loop_rect.collidepoint(event.pos):
                        self.player_looping = not self.player_looping
                        return True
            return True

        # Slider event routing (only when not in player)
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
            if self.current_tab == 'pitch':
                want = self.pitch_slider.dragging or event.type == pygame.MOUSEBUTTONDOWN
                if want and self.pitch_slider.handle_event(event):
                    self.pitch = self.pitch_slider.value
                    if event.type != pygame.MOUSEMOTION:
                        return True
            if self.current_tab == 'effects':
                for e in self.effects:
                    s = self.effect_sliders[e["name"]]
                    if e["expanded"] and (s.dragging or event.type == pygame.MOUSEBUTTONDOWN):
                        if s.handle_event(event):
                            e["value"] = s.value
                            if event.type != pygame.MOUSEMOTION:
                                return True
            if self.current_tab == 'advanced':
                for i, (fs, bs) in enumerate(self.adv_sliders):
                    if fs.dragging or bs.dragging or event.type == pygame.MOUSEBUTTONDOWN:
                        a = fs.handle_event(event)
                        b = bs.handle_event(event)
                        if a:
                            self.formants[i] = (fs.value, self.formants[i][1])
                        if b:
                            self.formants[i] = (self.formants[i][0], bs.value)
                        if (a or b) and event.type != pygame.MOUSEMOTION:
                            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._info_rect.collidepoint(event.pos):
                self.current_tab = 'info' if self.current_tab != 'info' else 'vowel'
                return True
            keys = ['vowel','traits','pitch','effects','advanced']
            for btn, key in zip(self.left_buttons, keys):
                if btn.clicked(event.pos):
                    self.current_tab = key
                    self._rebuild_left_buttons()
                    return True
            if self._play_rect.collidepoint(event.pos):
                self.wave_samples = self._generate_waveform()
                self.show_player = True
                self.player_time = 0
                self.player_playing = True
                return True
            if self._export_rect.collidepoint(event.pos):
                return True

            if self.current_tab == 'vowel':
                x = 320; y = 160; size = 100; gap = 18
                for v in ['A','E','I','O','U']:
                    r = pygame.Rect(x, y, size, size)
                    if r.collidepoint(event.pos):
                        self.selected_vowel = v
                        self.formants = list(self.formant_presets[(self.selected_vowel, self.selected_trait)])
                        self._rebuild_left_buttons()
                        return True
                    x += size + gap
            elif self.current_tab == 'traits':
                for key, x in [('M', 320), ('F', 620)]:
                    r = pygame.Rect(x, 160, 280, 140)
                    if r.collidepoint(event.pos):
                        self.selected_trait = key
                        self.formants = list(self.formant_presets[(self.selected_vowel, self.selected_trait)])
                        self._rebuild_left_buttons()
                        return True
            elif self.current_tab == 'pitch':
                x = 320; y = 260
                for val in [80, 120, 220, 300]:
                    r = pygame.Rect(x, y, 130, 50)
                    if r.collidepoint(event.pos):
                        self.pitch = float(val)
                        self._rebuild_left_buttons()
                        return True
                    x += 140
            elif self.current_tab == 'effects':
                clip_top = 145; clip_bottom = HEIGHT - 60
                if clip_top <= event.pos[1] <= clip_bottom and event.pos[0] >= 280:
                    y = 150 - int(self.effects_scroll); item_h = 36; slider_h = 50
                    for e in self.effects:
                        r = pygame.Rect(320, y, 580, item_h)
                        if r.collidepoint(event.pos):
                            e["expanded"] = not e["expanded"]
                            if not e["expanded"]:
                                self.effect_sliders[e["name"]].dragging = False
                            return True
                        y += item_h
                        if e["expanded"]:
                            y += slider_h
                        y += 4

        if event.type == pygame.MOUSEWHEEL:
            mp = self.mouse_pos
            if mp[0] >= 280:
                if self.current_tab == 'effects':
                    total_h = sum(36 + 4 + (50 if e["expanded"] else 0) for e in self.effects)
                    visible_h = HEIGHT - 60 - 145 - 10
                    max_s = max(0, total_h - visible_h)
                    self.effects_scroll_target = clamp(self.effects_scroll_target - event.y * 30, 0, max_s)
                elif self.current_tab == 'advanced':
                    total_h = 3 * (22 + 60 + 16)
                    visible_h = HEIGHT - 60 - 145 - 10
                    max_s = max(0, total_h - visible_h)
                    self.advanced_scroll_target = clamp(self.advanced_scroll_target - event.y * 30, 0, max_s)
                elif self.current_tab == 'info':
                    total_h = 0
                    for text, is_header in self.info_text:
                        f = self.font_md if is_header else self.font_sm
                        total_h += f.get_height() + 4
                    visible_h = HEIGHT - 60 - 145 - 10
                    max_s = max(0, total_h - visible_h)
                    self.info_scroll_target = clamp(self.info_scroll_target - event.y * 30, 0, max_s)

        return True

    def run(self):
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1/30)
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
                    break
            self._rebuild_left_buttons()
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    VoiceSynthApp().run()