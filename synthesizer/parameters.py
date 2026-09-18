import sys
sys.dont_write_bytecode = True

#frequency

#f0 = 200


# --------------------------------------------------------------------------- #
# Presets: male / female x A, E, I, O, U
# --------------------------------------------------------------------------- #

PRESETS = {
    "male" : {
        "A": (  [730, 1090, 2440], [80, 90, 140]),   # "father" /ɑ/
        "E": (  [530, 1840, 2480],  [70, 100, 140]),  # "bed"    /ɛ/
        "I": (  [270, 2290, 3010],  [50, 100, 160]),  # "beet"   /i/
        "O": (  [570, 840, 2410],   [70, 80, 140]),   # "bought" /ɔ/
        "U": (  [300, 870, 2240],   [50, 80, 140]),   # "boot"   /u/
    },
    "female" : {
        "A": (  [850, 1220, 2810],  [90, 110, 160]),
        "E": (  [610, 2330, 2990],  [80, 120, 160]),
        "I": (  [310, 2790, 3310],  [60, 120, 180]),
        "O": (  [590, 920, 2710],   [80, 100, 160]),
        "U": (  [370, 950, 2670],   [60, 100, 160]),
    }}

VALID_VOWELS = ("A", "E", "I", "O", "U")
VALID_GENDERS = ("male", "female")


# --------------------------------------------------------------------------- #
# Controller
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
    

