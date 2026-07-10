
"""
formant_controller.py

Controls vocal-tract formant frequency (F) and bandwidth (B) parameters
for the five cardinal vowels: A, E, I, O, U.

Each parameter set is a list of 3 elements:
    F = [F1, F2, F3]   -> formant frequencies (Hz)
    B = [B1, B2, B3]   -> formant bandwidths (Hz)

Presets are provided for both MALE and FEMALE voices (based on classic
Peterson & Barney (1952) average formant measurements, with typical
bandwidth estimates used in formant/Klatt-style synthesis).

A custom profile can also be defined and loaded by the user.
"""

from dataclasses import dataclass, field
from typing import List, Dict


# --------------------------------------------------------------------------- #
# Data structure
# --------------------------------------------------------------------------- #

@dataclass
class VowelParams:
    """Holds the 3-element Formant (F) and Bandwidth (B) lists for a vowel."""
    F: List[float]  # [F1, F2, F3] in Hz
    B: List[float]  # [B1, B2, B3] in Hz

    def __post_init__(self):
        if len(self.F) != 3:
            raise ValueError(f"F must have exactly 3 elements (F1,F2,F3), got {len(self.F)}")
        if len(self.B) != 3:
            raise ValueError(f"B must have exactly 3 elements (B1,B2,B3), got {len(self.B)}")


# --------------------------------------------------------------------------- #
# Presets: male / female x A, E, I, O, U
# --------------------------------------------------------------------------- #

PRESETS: Dict[str, Dict[str, VowelParams]] = {
    "male": {
        "A": VowelParams(F=[730, 1090, 2440], B=[80, 90, 140]),   # "father" /ɑ/
        "E": VowelParams(F=[530, 1840, 2480], B=[70, 100, 140]),  # "bed"    /ɛ/
        "I": VowelParams(F=[270, 2290, 3010], B=[50, 100, 160]),  # "beet"   /i/
        "O": VowelParams(F=[570, 840, 2410],  B=[70, 80, 140]),   # "bought" /ɔ/
        "U": VowelParams(F=[300, 870, 2240],  B=[50, 80, 140]),   # "boot"   /u/
    },
    "female": {
        "A": VowelParams(F=[850, 1220, 2810], B=[90, 110, 160]),
        "E": VowelParams(F=[610, 2330, 2990], B=[80, 120, 160]),
        "I": VowelParams(F=[310, 2790, 3310], B=[60, 120, 180]),
        "O": VowelParams(F=[590, 920, 2710],  B=[80, 100, 160]),
        "U": VowelParams(F=[370, 950, 2670],  B=[60, 100, 160]),
    },
}

VALID_VOWELS = ("A", "E", "I", "O", "U")
VALID_GENDERS = ("male", "female")


# --------------------------------------------------------------------------- #
# Controller
# --------------------------------------------------------------------------- #

class FormantController:
    """
    Central controller for the current F and B parameter state.

    Usage:
        fc = FormantController()
        fc.load_preset("male", "A")
        print(fc.F, fc.B)

        fc.set_custom(F=[700, 1200, 2500], B=[80, 100, 150])
        print(fc.F, fc.B)

        fc.save_custom_preset("myvoice_A", F=[700, 1200, 2500], B=[80, 100, 150])
        fc.load_custom_preset("myvoice_A")
    """

    def __init__(self, gender: str = "male", vowel: str = "A"):
        self.custom_profiles: Dict[str, VowelParams] = {}
        self.gender = gender
        self.vowel = vowel
        self.F: List[float] = [0.0, 0.0, 0.0]
        self.B: List[float] = [0.0, 0.0, 0.0]
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
        self.F = list(params.F)
        self.B = list(params.B)

    # ---- Custom user-defined profiles ------------------------------------ #

    def set_custom(self, F: List[float], B: List[float]) -> None:
        """
        Directly set the current F and B parameters to custom values.
        F and B must each contain exactly 3 numeric elements.
        """
        params = VowelParams(F=list(F), B=list(B))  # validates lengths
        self.F = params.F
        self.B = params.B
        self.gender = "custom"
        self.vowel = "custom"

    def save_custom_preset(self, name: str, F: List[float], B: List[float]) -> None:
        """Save a named custom profile for later reuse."""
        self.custom_profiles[name] = VowelParams(F=list(F), B=list(B))

    def load_custom_preset(self, name: str) -> None:
        """Load a previously saved custom profile by name."""
        if name not in self.custom_profiles:
            raise KeyError(f"No custom profile named '{name}' found.")
        params = self.custom_profiles[name]
        self.F = list(params.F)
        self.B = list(params.B)
        self.gender = "custom"
        self.vowel = name

    # ---- Utility ----------------------------------------------------------#

    def as_dict(self) -> dict:
        """Return the current state as a plain dictionary."""
        return {
            "gender": self.gender,
            "vowel": self.vowel,
            "F1": self.F[0], "F2": self.F[1], "F3": self.F[2],
            "B1": self.B[0], "B2": self.B[1], "B3": self.B[2],
        }

    def __repr__(self) -> str:
        return (f"FormantController(gender={self.gender!r}, vowel={self.vowel!r}, "
                f"F={self.F}, B={self.B})")


# --------------------------------------------------------------------------- #
# Interactive input helper (optional, for custom profile entry via terminal)
# --------------------------------------------------------------------------- #

def prompt_custom_profile() -> VowelParams:
    """
    Prompt the user via the terminal to input a custom F/B profile.
    Returns a VowelParams instance.
    """
    print("Enter custom formant values (Hz):")
    F = [float(input(f"  F{i+1}: ")) for i in range(3)]
    print("Enter custom bandwidth values (Hz):")
    B = [float(input(f"  B{i+1}: ")) for i in range(3)]
    return VowelParams(F=F, B=B)


# --------------------------------------------------------------------------- #
# Demo / manual test
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    fc = FormantController()

    print("Built-in presets:")
    for gender in VALID_GENDERS:
        for vowel in VALID_VOWELS:
            fc.load_preset(gender, vowel)
            print(f"  {gender:6s} {vowel}: F={fc.F}  B={fc.B}")

    print("\nApplying a custom profile:")
    fc.set_custom(F=[650, 1500, 2600], B=[75, 110, 150])
    print(" ", fc)

    print("\nSaving and reloading a named custom preset:")
    fc.save_custom_preset("robot_A", F=[400, 1600, 2900], B=[40, 60, 100])
    fc.load_custom_preset("robot_A")
    print(" ", fc)