"""
params.py

Everything related to *parameters* and *configuration* for the voice
synthesizer lives here:

    - Vowel/formant presets (male/female x A E I O U)
    - FormantController: holds the current formant_list / band_list state
    - Effects + top-level settings defaults
    - Loading/saving settings.json to disk
    - Loading synthesizer/conf.json
    - ParameterManager: a small facade the GUI drives instead of poking
      raw dicts directly

Nothing in this file touches pygame, pygame_gui, or audio playback -- that
all lives in main.py.
"""

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


SETTINGS_FILE = Path(__file__).with_name("conf.json")


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


# --------------------------------------------------------------------------- #
# Presets: male / female x A, E, I, O, U
# --------------------------------------------------------------------------- #

PRESETS = {
    "male": {
        "A": ([730, 1090, 2440], [80, 90, 140]),    # "father" /ɑ/
        "E": ([530, 1840, 2480], [70, 100, 140]),   # "bed"    /ɛ/
        "I": ([270, 2290, 3010], [50, 100, 160]),   # "beet"   /i/
        "O": ([570, 840, 2410], [70, 80, 140]),     # "bought" /ɔ/
        "U": ([300, 870, 2240], [50, 80, 140]),     # "boot"   /u/
    },
    "female": {
        "A": ([850, 1220, 2810], [90, 110, 160]),
        "E": ([610, 2330, 2990], [80, 120, 160]),
        "I": ([310, 2790, 3310], [60, 120, 180]),
        "O": ([590, 920, 2710], [80, 100, 160]),
        "U": ([370, 950, 2670], [60, 100, 160]),
    },
}

VALID_VOWELS = ("A", "E", "I", "O", "U")
VALID_GENDERS = ("male", "female")


# --------------------------------------------------------------------------- #
# Formant controller
# --------------------------------------------------------------------------- #

class FormantController:
    """
    Central controller for the current formant_list and band_list parameter state.

    Usage:
        fc = FormantController()
        fc.load_preset("male", "A")
        print(fc.formant_list, fc.band_list)

        fc.set_custom(formant_list=[700, 1200, 2500], band_list=[80, 100, 150])
        print(fc.formant_list, fc.band_list)

        fc.save_custom_preset("myvoice_A", formant_list=[700, 1200, 2500], band_list=[80, 100, 150])
        fc.load_custom_preset("myvoice_A")
    """

    def __init__(self, gender: str = "male", vowel="A"):
        self.gender = gender
        self.vowel = vowel
        self.formant_list = [0.0, 0.0, 0.0]
        self.band_list = [0.0, 0.0, 0.0]
        if isinstance(vowel, dict):
            self.load_dict(gender, vowel)
        else:
            self.load_preset(gender, vowel)

    # ---- Built-in presets ------------------------------------------------ #

    def load_preset(self, gender: str, vowel: str):
        """Load a built-in male/female vowel preset."""

        if gender not in VALID_GENDERS:
            raise ValueError(f"gender must be one of {VALID_GENDERS}, got '{gender}'")
        if vowel not in VALID_VOWELS:
            raise ValueError(f"vowel must be one of {VALID_VOWELS}, got '{vowel}'")

        self.formant_list = PRESETS[gender][vowel][0]
        self.band_list = PRESETS[gender][vowel][1]

        self.gender = gender
        self.vowel = vowel

        return self.formant_list, self.band_list

    def load_dict(self, gender: str, data: dict):
        """Load a controller saved in the settings JSON."""
        vowel = data.get("name", data.get("vowel", "A"))
        formant_list = data.get("formant_list", data.get("formants"))
        band_list = data.get("band_list", data.get("bandwidths"))

        if formant_list is None or band_list is None:
            return self.load_preset(gender, vowel)
        if vowel not in VALID_VOWELS:
            raise ValueError(f"vowel must be one of {VALID_VOWELS}, got '{vowel}'")
        if len(formant_list) != 3 or len(band_list) != 3:
            raise ValueError("a formant controller needs three formants and bandwidths")

        self.gender = gender
        self.vowel = vowel
        self.formant_list = [float(value) for value in formant_list]
        self.band_list = [float(value) for value in band_list]
        return self.formant_list, self.band_list

    def to_dict(self):
        """Return a JSON-serializable representation of this controller."""
        return {
            "name": self.vowel,
            "formant_list": list(self.formant_list),
            "band_list": list(self.band_list),
        }


# --------------------------------------------------------------------------- #
# Effects / settings defaults + persistence
# --------------------------------------------------------------------------- #

DEFAULT_EFFECTS = {
    "vibrato_enabled": False,
    "vibrato_rate": 5.0,
    "vibrato_depth": 12.0,
    "gain": 1.0,
    "noise_level": 0.0,
    "formant_shift": 0.0,
}

DEFAULT_SETTINGS = {
    "f0": 200,
    "gender": "female",
    "vowel": {"name": "A", "formant_list": [850.0, 1220.0, 2810.0], "band_list": [90.0, 110.0, 160.0]},
    "effects": DEFAULT_EFFECTS.copy(),
}


def load_settings():
    """Read settings from disk, falling back to (and writing) defaults on any problem."""
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as settings_file:
            raw_data = json.load(settings_file)
    except Exception:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    merged = DEFAULT_SETTINGS.copy()
    merged.update(raw_data)

    if not isinstance(raw_data.get("effects", {}), dict):
        merged["effects"] = DEFAULT_EFFECTS.copy()
    else:
        merged["effects"] = DEFAULT_EFFECTS.copy()
        merged["effects"].update(raw_data["effects"])

    vowel_data = merged.get("vowel")
    if not isinstance(vowel_data, dict) or "name" not in vowel_data:
        vowel_data = DEFAULT_SETTINGS["vowel"]
    controller = FormantController(merged["gender"], vowel_data)
    merged["vowel"] = controller.to_dict()

    return merged


def save_settings(settings):
    with SETTINGS_FILE.open("w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, indent=4)


# --------------------------------------------------------------------------- #
# Generic dict/JSON config loader (used for synthesizer/conf.json)
# --------------------------------------------------------------------------- #

class Dict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Config(object):
    @staticmethod
    def __load__(data):
        if type(data) is dict:
            return Config.load_dict(data)
        elif type(data) is list:
            return Config.load_list(data)
        else:
            return data

    @staticmethod
    def load_dict(data: dict):
        result = Dict()
        for key, value in data.items():
            result[key] = Config.__load__(value)
        return result

    @staticmethod
    def load_list(data: list):
        result = [Config.__load__(item) for item in data]
        return result

    @staticmethod
    def load_json(path: str):
        with open(path, "r") as f:
            result = Config.__load__(json.loads(f.read()))
        return result


# --------------------------------------------------------------------------- #
# ParameterManager: the facade the GUI actually talks to
# --------------------------------------------------------------------------- #

class ParameterManager:
    """
    Owns the live settings state (pitch, gender, vowel, effects) plus the
    FormantController backing the current vowel, and knows how to persist
    itself. main.py should go through this instead of poking self.settings
    dicts directly.
    """

    def __init__(self):
        self.settings = load_settings()
        self.controller = FormantController(self.settings["gender"], self.settings["vowel"])
        self.settings["vowel"] = self.controller.to_dict()

    # ---- persistence ------------------------------------------------- #

    def save(self):
        save_settings(self.settings)

    # ---- pitch --------------------------------------------------------- #

    @property
    def f0(self):
        return self.settings["f0"]

    def set_pitch(self, value):
        value = float(value)
        if value <= 0:
            raise ValueError("pitch (f0) must be positive")
        self.settings["f0"] = value

    # ---- gender / trait -------------------------------------------------- #

    @property
    def gender(self):
        return self.settings["gender"]

    def set_gender(self, gender):
        """Switch gender and re-resolve the current vowel to that gender's preset."""
        if gender not in VALID_GENDERS:
            raise ValueError(f"gender must be one of {VALID_GENDERS}, got '{gender}'")
        self.settings["gender"] = gender
        self.controller.load_preset(gender, self.controller.vowel)
        self.settings["vowel"] = self.controller.to_dict()

    # ---- vowel ------------------------------------------------------- #

    @property
    def vowel(self):
        return self.settings["vowel"]

    def set_vowel(self, vowel_letter):
        self.controller.load_preset(self.settings["gender"], vowel_letter)
        self.settings["vowel"] = self.controller.to_dict()

    # ---- effects ------------------------------------------------------- #

    @property
    def effects(self):
        return self.settings["effects"]

    def set_effects(self, effects_dict):
        self.settings["effects"] = dict(effects_dict)

    def toggle_vibrato(self):
        current = self.settings["effects"].get("vibrato_enabled", False)
        self.settings["effects"]["vibrato_enabled"] = not current
        return self.settings["effects"]["vibrato_enabled"]

    # ---- misc ------------------------------------------------------- #

    def status_text(self):
        """returns text from settings for display"""
        return (
            f"Gender: {self.settings['gender']} | Vowel: {self.settings['vowel']['name']} | "
            f"Pitch: {self.settings['f0']} Hz | Volume: {self.settings['effects'].get('gain', 1.0):.2f}"
        )

    def synth_kwargs(self, f0=None):
        """Keyword args ready to hand straight to synthesizer.generate_speech()."""
        return {
            "gender": self.settings["gender"],
            "vowel": self.settings["vowel"],
            "f0": float(self.settings["f0"] if f0 is None else f0),
            "effects": self.settings["effects"],
        }