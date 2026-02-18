import time
import streamlit as st
from music_theory import (
    get_random_question,
    check_answer,
    format_key_display,
    format_chord_display,
    ROMAN_NUMERALS,
)

GAME_DURATION = 60  # seconds

st.set_page_config(page_title="Chord Flashcards", page_icon="🎵", layout="centered")

# ── Session state init ──────────────────────────────────────────────────────

def init_state():
    defaults = {
        "score": 0,
        "correct": 0,
        "incorrect": 0,
        "key": None,
        "chord": None,
        "answer_roman": None,
        "game_active": False,
        "game_over": False,
        "start_time": None,
        "feedback": None,        # "correct" | "incorrect" | None
        "feedback_answer": None, # correct roman numeral shown on wrong answer
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


def start_game():
    st.session_state.score = 0
    st.session_state.correct = 0
    st.session_state.incorrect = 0
    st.session_state.game_active = True
    st.session_state.game_over = False
    st.session_state.start_time = time.time()
    st.session_state.feedback = None
    st.session_state.feedback_answer = None
    next_question()


def next_question():
    key, chord, roman = get_random_question()
    st.session_state.key = key
    st.session_state.chord = chord
    st.session_state.answer_roman = roman


def handle_answer(chosen_roman: str):
    if not st.session_state.game_active:
        return
    correct = check_answer(
        st.session_state.key,
        st.session_state.chord,
        chosen_roman,
    )
    if correct:
        st.session_state.score += 1
        st.session_state.correct += 1
        st.session_state.feedback = "correct"
        st.session_state.feedback_answer = None
    else:
        st.session_state.score -= 1
        st.session_state.incorrect += 1
        st.session_state.feedback = "incorrect"
        st.session_state.feedback_answer = st.session_state.answer_roman
    next_question()


def end_game():
    st.session_state.game_active = False
    st.session_state.game_over = True


# ── Styles ──────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-title   { text-align: center; font-size: 2rem; font-weight: 700; margin-bottom: 0; }
    .key-label    { text-align: center; font-size: 1.1rem; color: #888; margin-top: 0.2rem; }
    .chord-display{ text-align: center; font-size: 5rem; font-weight: 800;
                    line-height: 1.1; margin: 0.4rem 0 0.8rem; }
    .score-row    { display: flex; justify-content: center; gap: 2rem;
                    font-size: 1.1rem; margin-bottom: 0.5rem; }
    .score-val    { font-weight: 700; font-size: 1.4rem; }
    .timer-bar    { height: 8px; border-radius: 4px; background: #e0e0e0;
                    margin: 0.4rem 0 1rem; }
    .timer-fill   { height: 8px; border-radius: 4px; transition: width 0.4s; }
    .feedback-ok  { text-align:center; color: #22c55e; font-size:1.1rem;
                    font-weight:600; min-height:1.5rem; }
    .feedback-bad { text-align:center; color: #ef4444; font-size:1.1rem;
                    font-weight:600; min-height:1.5rem; }
    .feedback-blank { min-height:1.5rem; }
    div[data-testid="stButton"] > button {
        width: 100%; font-size: 1.3rem; font-weight: 700;
        padding: 0.55rem 0; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────

st.markdown('<p class="main-title">🎵 Chord Flashcards</p>', unsafe_allow_html=True)

# ── START SCREEN ─────────────────────────────────────────────────────────────

if not st.session_state.game_active and not st.session_state.game_over:
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;font-size:1.1rem;color:#aaa'>"
        "A chord name will appear. Pick the correct Roman numeral for that key.<br>"
        "<b>+1</b> for correct &nbsp;|&nbsp; <b>−1</b> for incorrect &nbsp;|&nbsp; <b>60 seconds</b>"
        "</p>",
        unsafe_allow_html=True,
    )
    col = st.columns([1, 2, 1])[1]
    with col:
        if st.button("▶ Start Game", use_container_width=True):
            start_game()
            st.rerun()

# ── GAME OVER SCREEN ──────────────────────────────────────────────────────────

elif st.session_state.game_over:
    st.markdown("---")
    score = st.session_state.score
    emoji = "🎉" if score > 0 else ("😐" if score == 0 else "😬")
    st.markdown(
        f"<p style='text-align:center;font-size:1.4rem;font-weight:700'>"
        f"Time's up! {emoji}</p>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Final Score", score)
    c2.metric("Correct ✓", st.session_state.correct)
    c3.metric("Incorrect ✗", st.session_state.incorrect)
    st.markdown("---")
    col = st.columns([1, 2, 1])[1]
    with col:
        if st.button("🔄 Play Again", use_container_width=True):
            start_game()
            st.rerun()

# ── ACTIVE GAME ───────────────────────────────────────────────────────────────

else:
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0.0, GAME_DURATION - elapsed)

    if remaining <= 0:
        end_game()
        st.rerun()

    # Timer bar
    pct = remaining / GAME_DURATION * 100
    color = "#22c55e" if pct > 40 else ("#f59e0b" if pct > 20 else "#ef4444")
    st.markdown(
        f'<div class="timer-bar"><div class="timer-fill" '
        f'style="width:{pct:.1f}%;background:{color}"></div></div>',
        unsafe_allow_html=True,
    )

    # Score row
    st.markdown(
        f'<div class="score-row">'
        f'<span>Score <span class="score-val">{st.session_state.score:+d}</span></span>'
        f'<span>⏱ <span class="score-val">{int(remaining)}s</span></span>'
        f'<span>✓ <span class="score-val">{st.session_state.correct}</span> '
        f'✗ <span class="score-val">{st.session_state.incorrect}</span></span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Key + Chord display
    key_disp = format_key_display(st.session_state.key)
    chord_disp = format_chord_display(st.session_state.chord)
    st.markdown(f'<p class="key-label">Key of {key_disp} Major</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="chord-display">{chord_disp}</p>', unsafe_allow_html=True)

    # Feedback line
    fb = st.session_state.feedback
    if fb == "correct":
        st.markdown('<p class="feedback-ok">✓ Correct!</p>', unsafe_allow_html=True)
    elif fb == "incorrect":
        correct_rn = st.session_state.feedback_answer
        st.markdown(
            f'<p class="feedback-bad">✗ Wrong — answer was <b>{correct_rn}</b></p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<p class="feedback-blank"></p>', unsafe_allow_html=True)

    # Roman numeral buttons (2 rows: 4 + 3)
    row1 = ROMAN_NUMERALS[:4]
    row2 = ROMAN_NUMERALS[4:]

    cols1 = st.columns(len(row1))
    for col, rn in zip(cols1, row1):
        with col:
            if st.button(rn, key=f"btn_{rn}", use_container_width=True):
                handle_answer(rn)
                st.rerun()

    cols2 = st.columns(len(row2))
    for col, rn in zip(cols2, row2):
        with col:
            if st.button(rn, key=f"btn_{rn}", use_container_width=True):
                handle_answer(rn)
                st.rerun()

    # Auto-refresh every second to count down timer
    time.sleep(1)
    st.rerun()
