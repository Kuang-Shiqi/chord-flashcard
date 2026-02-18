import random

# All 12 major keys with their diatonic chords mapped to Roman numerals
# Format: key -> {roman_numeral: chord_name}
MAJOR_KEYS = {
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

ROMAN_NUMERALS = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]


def get_random_question():
    """Pick a random key and a random chord from that key."""
    key = random.choice(list(MAJOR_KEYS.keys()))
    roman = random.choice(ROMAN_NUMERALS)
    chord = MAJOR_KEYS[key][roman]
    return key, chord, roman


def check_answer(key: str, chord: str, user_answer: str) -> bool:
    """Return True if user_answer is the correct Roman numeral for chord in key."""
    correct_roman = get_correct_roman(key, chord)
    return user_answer == correct_roman


def get_correct_roman(key: str, chord: str) -> str:
    """Return the correct Roman numeral for a chord in a given key."""
    for roman, ch in MAJOR_KEYS[key].items():
        if ch == chord:
            return roman
    return ""


def format_key_display(key: str) -> str:
    """Format key name for display, converting 'b' suffix to flat symbol."""
    return key.replace("b", "♭")


def format_chord_display(chord: str) -> str:
    """Format chord name for display, converting 'b' to flat symbol."""
    # Only replace 'b' when it's part of a flat note (e.g., Bb, Eb, Ab, Db, Gb, Cb)
    # These always appear as the second character
    if len(chord) >= 2 and chord[1] == "b":
        return chord[0] + "♭" + chord[2:]
    return chord
