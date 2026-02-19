import random

# ---------------------------------------------------------------------------
# Diatonic chords for all 12 major keys
# ---------------------------------------------------------------------------

# Triads: key -> {roman_numeral: chord_name}
TRIADS = {
    "C":  {"I": "C",   "ii": "Dm",  "iii": "Em",  "IV": "F",   "V": "G",   "vi": "Am",  "vii°": "Bdim"},
    "G":  {"I": "G",   "ii": "Am",  "iii": "Bm",  "IV": "C",   "V": "D",   "vi": "Em",  "vii°": "F#dim"},
    "D":  {"I": "D",   "ii": "Em",  "iii": "F#m", "IV": "G",   "V": "A",   "vi": "Bm",  "vii°": "C#dim"},
    "A":  {"I": "A",   "ii": "Bm",  "iii": "C#m", "IV": "D",   "V": "E",   "vi": "F#m", "vii°": "G#dim"},
    "E":  {"I": "E",   "ii": "F#m", "iii": "G#m", "IV": "A",   "V": "B",   "vi": "C#m", "vii°": "D#dim"},
    "B":  {"I": "B",   "ii": "C#m", "iii": "D#m", "IV": "E",   "V": "F#",  "vi": "G#m", "vii°": "A#dim"},
    "F#": {"I": "F#",  "ii": "G#m", "iii": "A#m", "IV": "B",   "V": "C#",  "vi": "D#m", "vii°": "E#dim"},
    "F":  {"I": "F",   "ii": "Gm",  "iii": "Am",  "IV": "Bb",  "V": "C",   "vi": "Dm",  "vii°": "Edim"},
    "Bb": {"I": "Bb",  "ii": "Cm",  "iii": "Dm",  "IV": "Eb",  "V": "F",   "vi": "Gm",  "vii°": "Adim"},
    "Eb": {"I": "Eb",  "ii": "Fm",  "iii": "Gm",  "IV": "Ab",  "V": "Bb",  "vi": "Cm",  "vii°": "Ddim"},
    "Ab": {"I": "Ab",  "ii": "Bbm", "iii": "Cm",  "IV": "Db",  "V": "Eb",  "vi": "Fm",  "vii°": "Gdim"},
    "Db": {"I": "Db",  "ii": "Ebm", "iii": "Fm",  "IV": "Gb",  "V": "Ab",  "vi": "Bbm", "vii°": "Cdim"},
}

# 7th chords: key -> {roman_numeral: chord_name}
SEVENTHS = {
    "C":  {"Imaj7": "Cmaj7",  "ii7": "Dm7",   "iii7": "Em7",   "IVmaj7": "Fmaj7",  "V7": "G7",   "vi7": "Am7",   "vii\u00f87": "Bm7b5"},
    "G":  {"Imaj7": "Gmaj7",  "ii7": "Am7",   "iii7": "Bm7",   "IVmaj7": "Cmaj7",  "V7": "D7",   "vi7": "Em7",   "vii\u00f87": "F#m7b5"},
    "D":  {"Imaj7": "Dmaj7",  "ii7": "Em7",   "iii7": "F#m7",  "IVmaj7": "Gmaj7",  "V7": "A7",   "vi7": "Bm7",   "vii\u00f87": "C#m7b5"},
    "A":  {"Imaj7": "Amaj7",  "ii7": "Bm7",   "iii7": "C#m7",  "IVmaj7": "Dmaj7",  "V7": "E7",   "vi7": "F#m7",  "vii\u00f87": "G#m7b5"},
    "E":  {"Imaj7": "Emaj7",  "ii7": "F#m7",  "iii7": "G#m7",  "IVmaj7": "Amaj7",  "V7": "B7",   "vi7": "C#m7",  "vii\u00f87": "D#m7b5"},
    "B":  {"Imaj7": "Bmaj7",  "ii7": "C#m7",  "iii7": "D#m7",  "IVmaj7": "Emaj7",  "V7": "F#7",  "vi7": "G#m7",  "vii\u00f87": "A#m7b5"},
    "F#": {"Imaj7": "F#maj7", "ii7": "G#m7",  "iii7": "A#m7",  "IVmaj7": "Bmaj7",  "V7": "C#7",  "vi7": "D#m7",  "vii\u00f87": "E#m7b5"},
    "F":  {"Imaj7": "Fmaj7",  "ii7": "Gm7",   "iii7": "Am7",   "IVmaj7": "Bbmaj7", "V7": "C7",   "vi7": "Dm7",   "vii\u00f87": "Em7b5"},
    "Bb": {"Imaj7": "Bbmaj7", "ii7": "Cm7",   "iii7": "Dm7",   "IVmaj7": "Ebmaj7", "V7": "F7",   "vi7": "Gm7",   "vii\u00f87": "Am7b5"},
    "Eb": {"Imaj7": "Ebmaj7", "ii7": "Fm7",   "iii7": "Gm7",   "IVmaj7": "Abmaj7", "V7": "Bb7",  "vi7": "Cm7",   "vii\u00f87": "Dm7b5"},
    "Ab": {"Imaj7": "Abmaj7", "ii7": "Bbm7",  "iii7": "Cm7",   "IVmaj7": "Dbmaj7", "V7": "Eb7",  "vi7": "Fm7",   "vii\u00f87": "Gm7b5"},
    "Db": {"Imaj7": "Dbmaj7", "ii7": "Ebm7",  "iii7": "Fm7",   "IVmaj7": "Gbmaj7", "V7": "Ab7",  "vi7": "Bbm7",  "vii\u00f87": "Cbm7b5"},
}

TRIAD_ROMANS   = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]
SEVENTH_ROMANS = ["Imaj7", "ii7", "iii7", "IVmaj7", "V7", "vi7", "vii\u00f87"]

ALL_KEYS = list(TRIADS.keys())


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def build_pool(use_triads: bool, use_sevenths: bool) -> dict:
    """
    Return a combined dict: key -> {roman: chord}
    based on which chord types are selected.
    """
    pool = {k: {} for k in ALL_KEYS}
    for key in ALL_KEYS:
        if use_triads:
            pool[key].update(TRIADS[key])
        if use_sevenths:
            pool[key].update(SEVENTHS[key])
    return pool


def get_progression(pool: dict, length: int) -> list[tuple[str, str, str]]:
    """
    Return a progression of `length` chords all from the same random key.
    Each item is (key, chord_name, roman_numeral).
    Chords are drawn without repetition where possible.
    """
    key = random.choice(ALL_KEYS)
    chords = list(pool[key].items())   # [(roman, chord), ...]
    if length > len(chords):
        # allow repeats if progression is longer than available chords
        chosen = random.choices(chords, k=length)
    else:
        chosen = random.sample(chords, k=length)
    # return as (key, chord_name, roman)
    return [(key, chord, roman) for roman, chord in chosen]


def all_correct(progression: list[tuple[str, str, str]],
                answers: list[str]) -> bool:
    """Return True only if every answer matches the corresponding roman."""
    return all(ans == item[2] for ans, item in zip(answers, progression))


def format_key_display(key: str) -> str:
    return key.replace("b", "\u266d")


def format_chord_display(chord: str) -> str:
    """Replace flat 'b' (second char) with ♭ symbol."""
    if len(chord) >= 2 and chord[1] == "b":
        return chord[0] + "\u266d" + chord[2:]
    return chord


def get_roman_options(use_triads: bool, use_sevenths: bool) -> list[str]:
    """Return the list of roman numeral buttons to show."""
    options = []
    if use_triads:
        options += TRIAD_ROMANS
    if use_sevenths:
        options += SEVENTH_ROMANS
    return options
