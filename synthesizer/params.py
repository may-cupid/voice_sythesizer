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
import os
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

    def __init__(self, gender, vowel):
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

        return [self.formant_list, self.band_list]

    def load_dict(self, gender: str, data: dict):
        """Load a controller saved in the settings JSON."""

        vowel = data.get("name")
        formant_list = data.get("formant_list")
        band_list = data.get("band_list")

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
    "effects":dict(DEFAULT_EFFECTS),
}



def load_settings():
    """Read settings from disk, falling back to (and writing) defaults on any problem."""
    
    settings = DEFAULT_SETTINGS
    
    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError):
        """when an error occurs: settings are saved"""
        _write(settings)
        return settings
    
    if not isinstance(raw, dict):
        raw = {}
 
    # gender
    if raw.get("gender") in VALID_GENDERS:
        settings["gender"] = raw["gender"]
 
    # f0
    try:
        f0 = float(raw.get("f0", settings["f0"]))
        if f0 > 0:
            settings["f0"] = f0
    except (TypeError, ValueError):
        pass
 
    # effects
    if isinstance(raw.get("effects"), dict):
        settings["effects"].update(raw["effects"])
 
    # vowel
    try:
        controller = FormantController(settings["gender"], raw.get("vowel", settings["vowel"]))
    except (ValueError, TypeError, AttributeError):
        controller = FormantController(settings["gender"], "A")
    settings["vowel"] = controller.to_dict()
 
    return settings


def merge_recursive(base, patch):
    """Deep-merge `patch` into `base` (in place) and return base."""
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            merge_recursive(base[k], v)
        else:
            base[k] = v
    return base


def replace_field(data, key, new_value):
    """Set data[key] = new_value, deep-merging if both sides are dicts."""
    return merge_recursive(data, {key: new_value})


"""def load_settings():
    "loads settings from json file, returns dict"
    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_SETTINGS"""


def _write(data):
    # (very sus)Write to a temp file, then swap it in, so a crash can't leave a half-written file .
    tmp = SETTINGS_FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:

        json.dump(data, f, indent=2)
    os.replace(tmp, SETTINGS_FILE)


def save_settings(key, settings):
    """Read the file, change one top-level key, write it back. Returns the full dict."""
    data = load_settings()
    replace_field(data, key, settings)
    _write(data)
    return data


def save_patch(patch):
    """Same as save_settings but for several keys in one write."""
    data = merge_recursive(load_settings(), patch)
    _write(data)
    return data

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

    def save(self):
        """Write the current settings to disk."""
        _write(self.settings)

    
    def upload(self, path, value):
        """upload(["f0"], 220.0) or upload(["effects", "vibrato_enabled"], True)"""

        print(self.settings)

        if isinstance(path, str):
            path = [path]
        if not path or path[0] not in DEFAULT_SETTINGS:
            raise KeyError(f"unknown setting {path!r}")
        for k in reversed(path[1:]):
            value = {k: value}          # wrap into a nested dict for deep paths
        merge_recursive(self.settings, {path[0]: value})

        self.save()

        print(self.settings)


    # ---- pitch --------------------------------------------------------- #

    @property
    def f0(self):
        """Frequency in Hz, property of ParameterManager"""
        return self.settings["f0"]

    def set_pitch(self, value):
        """uploads f0 to json"""
        value = float(value)
        if value <= 0:
            raise ValueError("pitch (f0) must be positive")
        self.upload(["f0"], value)

    # ---- gender ---- #
    @property
    def gender(self):
        return self.settings["gender"]

    def set_gender(self, gender):
        """uploads selected gender and reloads preset (formant/bandwidth)"""
        if gender not in VALID_GENDERS:
            raise ValueError(f"gender must be one of {VALID_GENDERS}, got '{gender}'")
        self.controller.load_preset(gender, self.settings["vowel"])  # validates
        

        self.upload(["vowel"], self.controller.to_dict())

    # ---- vowel ---- #
    @property
    def vowel(self):
        return self.settings["vowel"]

    def set_vowel(self, vowel):
        """(sus) uploads preset vowel to file, turns to dict"""
        
        #uploads to controller
        self.controller.load_preset(self.settings["gender"], vowel) 

        #uploads to json
        self.upload(["vowel"], self.controller.to_dict())

    # ---- effects ---- #
    @property
    def effects(self):
        return self.settings["effects"]

    def set_effects(self, effects_dict):
        self.upload(["effects"], dict(effects_dict))

    def toggle_vibrato(self):
        new = not self.settings["effects"].get("vibrato_enabled", False)
        self.upload(["effects", "vibrato_enabled"], new)
        return new

    # ---- misc ------------------------------------------------------- #

    def status_text(self):
        """returns text from settings for display"""
        return (
            f"Gender: {self.settings['gender']} | Vowel: {self.settings['vowel']['name']} | "
            f"Pitch: {self.settings['f0']} Hz | Volume: {self.settings['effects'].get('gain', 1.0):.2f}"
        )

    def synth_kwargs(self, f0=None):
        """Keyword args ready to hand straight to synthesizer.generate_speech()."""
        sythesizer_settings = {
            
            "gender": str(self.settings["gender"]),
            "vowel": str(self.settings["vowel"]),
            "f0": float(self.settings["f0"] if f0 is None else f0),
            "effects": dict(self.settings["effects"]),
        }
        return sythesizer_settings

parameter_manager = ParameterManager()
formant_controller = FormantController(parameter_manager.gender, parameter_manager.vowel)




