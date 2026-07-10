from dataclasses import dataclass, field
from typing import List, Dict

import sys
sys.dont_write_bytecode = True


#frequency

f0 = 200

@dataclass
class VowelParams:
    """Holds the 3-element Formant (formant_list) and Bandwidth (band_list) lists for a vowel."""
    formant_list: List[float]  # [F1, F2, F3] in Hz
    band_list: List[float]  # [B1, B2, B3] in Hz

    def __post_init__(self):
        if len(self.formant_list) != 3:
            raise ValueError(f"formant_list must have exactly 3 elements (F1,F2,F3), got {len(self.formant_list)}")
        if len(self.band_list) != 3:
            raise ValueError(f"band_list must have exactly 3 elements (B1,B2,B3), got {len(self.band_list)}")


# --------------------------------------------------------------------------- #
# Presets: male / female x A, E, I, O, U
# --------------------------------------------------------------------------- #

PRESETS: Dict[str, Dict[str, VowelParams]] = {
    "male": {
        "A": VowelParams(formant_list=[730, 1090, 2440], band_list=[80, 90, 140]),   # "father" /ɑ/
        "E": VowelParams(formant_list=[530, 1840, 2480], band_list=[70, 100, 140]),  # "bed"    /ɛ/
        "I": VowelParams(formant_list=[270, 2290, 3010], band_list=[50, 100, 160]),  # "beet"   /i/
        "O": VowelParams(formant_list=[570, 840, 2410],  band_list=[70, 80, 140]),   # "bought" /ɔ/
        "U": VowelParams(formant_list=[300, 870, 2240],  band_list=[50, 80, 140]),   # "boot"   /u/
    },
    "female": {
        "A": VowelParams(formant_list=[850, 1220, 2810], band_list=[90, 110, 160]),
        "E": VowelParams(formant_list=[610, 2330, 2990], band_list=[80, 120, 160]),
        "I": VowelParams(formant_list=[310, 2790, 3310], band_list=[60, 120, 180]),
        "O": VowelParams(formant_list=[590, 920, 2710],  band_list=[80, 100, 160]),
        "U": VowelParams(formant_list=[370, 950, 2670],  band_list=[60, 100, 160]),
    },
}

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

    def __init__(self, gender: str = "male", vowel: str = "A"):
        self.custom_profiles: Dict[str, VowelParams] = {}
        self.gender = gender
        self.vowel = vowel
        self.formant_list: List[float] = [0.0, 0.0, 0.0]
        self.band_list: List[float] = [0.0, 0.0, 0.0]
        self.load_preset(gender, vowel)

    # ---- Built-in presets ------------------------------------------------ #

    def load_preset(self, gender: str, vowel: str) -> None:
        """Load a built-in male/female vowel preset."""
        gender = gender.lower()
        vowel = vowel.upper()

        if gender not in VALID_GENDERS:
            raise ValueError(f"gender must be one of {VALID_GENDERS}, got '{gender}'")
        if vowel not in VALID_VOWELS:
            raise ValueError(f"vowel must be one of {VALID_VOWELS}, got '{vowel}'")

        params = PRESETS[gender][vowel]
        self.gender = gender
        self.vowel = vowel
        self.formant_list = list(params.formant_list)
        self.band_list = list(params.band_list)

    # ---- Custom user-defined profiles ------------------------------------ #

    def set_custom(self, formant_list: List[float], band_list: List[float]) -> None:
        """
        Directly set the current formant_list and band_list parameters to custom values.
        formant_list and band_list must each contain exactly 3 numeric elements.
        """
        params = VowelParams(formant_list=list(formant_list), band_list=list(band_list))  # validates lengths
        self.formant_list = params.formant_list
        self.band_list = params.band_list
        self.gender = "custom"
        self.vowel = "custom"

    def save_custom_preset(self, name: str, formant_list: List[float], band_list: List[float]) -> None:
        """Save a named custom profile for later reuse."""
        self.custom_profiles[name] = VowelParams(formant_list=list(formant_list), band_list=list(band_list))

    def load_custom_preset(self, name: str) -> None:
        """Load a previously saved custom profile by name."""
        if name not in self.custom_profiles:
            raise KeyError(f"No custom profile named '{name}' found.")
        params = self.custom_profiles[name]
        self.formant_list = list(params.formant_list)
        self.band_list = list(params.band_list)
        self.gender = "custom"
        self.vowel = name

    # ---- Utility ----------------------------------------------------------#

    def as_dict(self) -> dict:
        """Return the current state as a plain dictionary."""
        return {
            "gender": self.gender,
            "vowel": self.vowel,
            "F1": self.formant_list[0], "F2": self.formant_list[1], "F3": self.formant_list[2],
            "B1": self.band_list[0], "B2": self.band_list[1], "B3": self.band_list[2],
        }
    
    def export(self) -> List[List[float]]:
        """
        Export the current parameters as a plain list for use by other
        (sub)programs, e.g. a synthesis engine:
 
            F, B = fc.export()
 
        Returns:
            [F, B]  where F = [F1, F2, F3] and B = [B1, B2, B3]
        """









#variables

    #formants
"""
class Formants:
class to manage formant parameters
def __init__(self):
"""















"""
F1 = 700
F2 = 1220
F3 = 2600

F = []

F1, F2, F3, F


    #bandwidth 
B1 = 130
B2 = 60
B3 = 160
"""
#Formant presets

#F_M_a = 
#F_M_e = 



