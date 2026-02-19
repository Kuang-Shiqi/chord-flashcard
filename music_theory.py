import random

# ---------------------------------------------------------------------------
# Quality definitions
# ---------------------------------------------------------------------------

QUALITIES = [
    {"id": "maj",  "label": "maj",  "symbol": "",    "case": "upper"},
    {"id": "min",  "label": "min",  "symbol": "",    "case": "lower"},
    {"id": "dim",  "label": "dim",  "symbol": "\u00b0",  "case": "lower"},
    {"id": "maj7", "label": "maj7", "symbol": "maj7","case": "upper"},
    {"id": "dom7", "label": "7",    "symbol": "7",   "case": "upper"},
    {"id": "min7", "label": "m7",   "symbol": "7",   "case": "lower"},
    {"id": "hdim", "label": "\u00f87",   "symbol": "\u00f87",  "case": "lower"},
]

QUALITY_IDS = [q["id"] for q in QUALITIES]

# Base Roman numerals (uppercase); lowercased for minor/dim qualities
BASE_ROMANS = ["I", "II", "III", "IV", "V", "VI", "VII"]


def build_roman(degree: int, quality_id: str) -> str:
    """
    Build a Roman numeral string from scale degree (1-7) and quality id.
    e.g. degree=2, quality='min' -> 'ii'
         degree=5, quality='dom7' -> 'V7'
         degree=7, quality='hdim' -> 'vii\u00f87'
    """
    if degree < 1 or degree > 7:
        return ""
    q = next((x for x in QUALITIES if x["id"] == quality_id), None)
    if q is None:
        return ""
    base = BASE_ROMANS[degree - 1]
    if q["case"] == "lower":
        base = base.lower()
    return base + q["symbol"]


def parse_roman(roman: str):
    """
    Parse a Roman numeral string back to (degree, quality_id).
    Returns (None, None) if unrecognised.
    """
    for deg, base in enumerate(BASE_ROMANS, 1):
        for q in QUALITIES:
            if build_roman(deg, q["id"]) == roman:
                return deg, q["id"]
    return None, None


# ---------------------------------------------------------------------------
# Diatonic chord pools
# ---------------------------------------------------------------------------

# Each entry: (degree, quality_id)
DIATONIC_PATTERN = [
    (1, "maj"),
    (2, "min"),
    (3, "min"),
    (4, "maj"),
    (5, "maj"),
    (6, "min"),
    (7, "dim"),
]

DIATONIC_7TH_PATTERN = [
    (1, "maj7"),
    (2, "min7"),
    (3, "min7"),
    (4, "maj7"),
    (5, "dom7"),
    (6, "min7"),
    (7, "hdim"),
]

# Chord names for all 12 keys
# key -> list of 7 chord names (triads), list of 7 chord names (7ths)
TRIAD_NAMES = {
    "C":  ["C","Dm","Em","F","G","Am","Bdim"],
    "G":  ["G","Am","Bm","C","D","Em","F#dim"],
    "D":  ["D","Em","F#m","G","A","Bm","C#dim"],
    "A":  ["A","Bm","C#m","D","E","F#m","G#dim"],
    "E":  ["E","F#m","G#m","A","B","C#m","D#dim"],
    "B":  ["B","C#m","D#m","E","F#","G#m","A#dim"],
    "F#": ["F#","G#m","A#m","B","C#","D#m","E#dim"],
    "F":  ["F","Gm","Am","Bb","C","Dm","Edim"],
    "Bb": ["Bb","Cm","Dm","Eb","F","Gm","Adim"],
    "Eb": ["Eb","Fm","Gm","Ab","Bb","Cm","Ddim"],
    "Ab": ["Ab","Bbm","Cm","Db","Eb","Fm","Gdim"],
    "Db": ["Db","Ebm","Fm","Gb","Ab","Bbm","Cdim"],
}

SEVENTH_NAMES = {
    "C":  ["Cmaj7","Dm7","Em7","Fmaj7","G7","Am7","Bm7b5"],
    "G":  ["Gmaj7","Am7","Bm7","Cmaj7","D7","Em7","F#m7b5"],
    "D":  ["Dmaj7","Em7","F#m7","Gmaj7","A7","Bm7","C#m7b5"],
    "A":  ["Amaj7","Bm7","C#m7","Dmaj7","E7","F#m7","G#m7b5"],
    "E":  ["Emaj7","F#m7","G#m7","Amaj7","B7","C#m7","D#m7b5"],
    "B":  ["Bmaj7","C#m7","D#m7","Emaj7","F#7","G#m7","A#m7b5"],
    "F#": ["F#maj7","G#m7","A#m7","Bmaj7","C#7","D#m7","E#m7b5"],
    "F":  ["Fmaj7","Gm7","Am7","Bbmaj7","C7","Dm7","Em7b5"],
    "Bb": ["Bbmaj7","Cm7","Dm7","Ebmaj7","F7","Gm7","Am7b5"],
    "Eb": ["Ebmaj7","Fm7","Gm7","Abmaj7","Bb7","Cm7","Dm7b5"],
    "Ab": ["Abmaj7","Bbm7","Cm7","Dbmaj7","Eb7","Fm7","Gm7b5"],
    "Db": ["Dbmaj7","Ebm7","Fm7","Gbmaj7","Ab7","Bbm7","Cbm7b5"],
}

ALL_KEYS = list(TRIAD_NAMES.keys())


def build_pool(use_triads: bool, use_sevenths: bool) -> list:
    """
    Returns a flat list of (key, chord_name, roman_str) tuples
    based on selected chord types.
    """
    pool = []
    for key in ALL_KEYS:
        if use_triads:
            for i, (deg, qual) in enumerate(DIATONIC_PATTERN):
                roman = build_roman(deg, qual)
                chord = TRIAD_NAMES[key][i]
                pool.append((key, chord, roman))
        if use_sevenths:
            for i, (deg, qual) in enumerate(DIATONIC_7TH_PATTERN):
                roman = build_roman(deg, qual)
                chord = SEVENTH_NAMES[key][i]
                pool.append((key, chord, roman))
    return pool


def get_progression(pool: list, length: int) -> list:
    """
    Return a progression of `length` chords all from the same random key.
    Each item: (key, chord_name, roman_str).
    """
    # filter pool to a random key
    key = random.choice(ALL_KEYS)
    key_items = [item for item in pool if item[0] == key]
    if not key_items:
        key_items = pool  # fallback
    if length > len(key_items):
        chosen = random.choices(key_items, k=length)
    else:
        chosen = random.sample(key_items, k=length)
    return chosen


def format_key_display(key: str) -> str:
    return key.replace("b", "\u266d")


def format_chord_display(chord: str) -> str:
    """Replace flat 'b' (second char) with \u266d symbol."""
    if len(chord) >= 2 and chord[1] == "b":
        return chord[0] + "\u266d" + chord[2:]
    return chord
