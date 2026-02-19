import time
import streamlit as st
from music_theory import (
    build_pool,
    get_progression,
    format_key_display,
    format_chord_display,
    get_roman_options,
    TRIAD_ROMANS,
    SEVENTH_ROMANS,
)

GAME_DURATION = 60  # seconds

st.set_page_config(page_title="Chord Flashcards", page_icon="🎵", layout="centered")

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title    { text-align:center; font-size:2rem; font-weight:700; margin-bottom:0.2rem; }
    .key-label     { text-align:center; font-size:1.15rem; color:#888; margin-bottom:0.6rem; }
    .chord-name    { text-align:center; font-size:2.6rem; font-weight:800; line-height:1.1; }
    .roman-correct { text-align:center; font-size:1.1rem; color:#22c55e; font-weight:700; min-height:1.6rem; }
    .roman-wrong   { text-align:center; font-size:1.1rem; color:#ef4444; font-weight:700; min-height:1.6rem; }
    .roman-pending { text-align:center; font-size:1.1rem; color:#888;    min-height:1.6rem; }
    .score-row     { display:flex; justify-content:center; gap:2.5rem;
                     font-size:1.05rem; margin-bottom:0.4rem; }
    .score-val     { font-weight:700; font-size:1.35rem; }
    .timer-bar     { height:8px; border-radius:4px; background:#e0e0e0; margin:0.3rem 0 0.8rem; }
    .timer-fill    { height:8px; border-radius:4px; }
    .fb-ok         { text-align:center; font-size:1.3rem; font-weight:700;
                     color:#22c55e; padding:0.4rem 0; }
    .fb-bad        { text-align:center; font-size:1.3rem; font-weight:700;
                     color:#ef4444; padding:0.4rem 0; }
    div[data-testid="stButton"] > button {
        width:100%; font-size:1.1rem; font-weight:700;
        padding:0.4rem 0; border-radius:8px;
    }
    /* tighten up text_input labels */
    div[data-testid="stTextInput"] label { display:none; }
    div[data-testid="stTextInput"] input {
        text-align:center; font-size:1.1rem; font-weight:600;
    }
</style>
""", unsafe_allow_html=True)

# ── Spacebar submit via JS ───────────────────────────────────────────────────
SPACEBAR_JS = """
<script>
(function() {
    // avoid duplicate listeners
    if (window._spaceListenerAdded) return;
    window._spaceListenerAdded = true;
    document.addEventListener('keydown', function(e) {
        if (e.code === 'Space') {
            // don't fire when user is typing in an input
            if (document.activeElement && document.activeElement.tagName === 'INPUT') return;
            // find the submit / next button and click it
            const btns = Array.from(document.querySelectorAll('button'));
            const target = btns.find(b =>
                b.innerText.includes('Submit') || b.innerText.includes('Next'));
            if (target) { e.preventDefault(); target.click(); }
        }
    });
})();
</script>
"""

# ── Session state ────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        # settings
        "use_triads":    True,
        "use_sevenths":  True,
        "prog_length":   4,
        # game lifecycle  "settings" | "playing" | "feedback" | "gameover"
        "screen":        "settings",
        # active round
        "progression":   None,   # list of (key, chord, roman)
        "user_answers":  [],     # list of str
        "start_time":    None,
        # totals
        "score":         0,
        "correct":       0,
        "incorrect":     0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Helpers ──────────────────────────────────────────────────────────────────
def start_game():
    st.session_state.score     = 0
    st.session_state.correct   = 0
    st.session_state.incorrect = 0
    st.session_state.start_time = time.time()
    st.session_state.screen    = "playing"
    new_round()

def new_round():
    pool = build_pool(st.session_state.use_triads, st.session_state.use_sevenths)
    st.session_state.progression  = get_progression(pool, st.session_state.prog_length)
    st.session_state.user_answers = [""] * st.session_state.prog_length

def check_time():
    elapsed = time.time() - st.session_state.start_time
    return max(0.0, GAME_DURATION - elapsed)

def submit_answers():
    prog    = st.session_state.progression
    answers = st.session_state.user_answers
    correct_all = all(
        ans.strip() == item[2]
        for ans, item in zip(answers, prog)
    )
    if correct_all:
        st.session_state.score   += 1
        st.session_state.correct += 1
    else:
        st.session_state.score   -= 1
        st.session_state.incorrect += 1
    st.session_state.screen = "feedback"

def next_round():
    remaining = check_time()
    if remaining <= 0:
        st.session_state.screen = "gameover"
    else:
        st.session_state.screen = "playing"
        new_round()

# ── Draw timer bar ───────────────────────────────────────────────────────────
def draw_timer(remaining):
    pct   = remaining / GAME_DURATION * 100
    color = "#22c55e" if pct > 40 else ("#f59e0b" if pct > 20 else "#ef4444")
    st.markdown(
        f'<div class="timer-bar"><div class="timer-fill" '
        f'style="width:{pct:.1f}%;background:{color}"></div></div>',
        unsafe_allow_html=True,
    )

def draw_score(remaining):
    s = st.session_state
    st.markdown(
        f'<div class="score-row">'
        f'<span>Score <span class="score-val">{s.score:+d}</span></span>'
        f'<span>⏱ <span class="score-val">{int(remaining)}s</span></span>'
        f'<span>✓ <span class="score-val">{s.correct}</span> '
        f'✗ <span class="score-val">{s.incorrect}</span></span>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════════════════════
# SETTINGS SCREEN
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "settings":
    st.markdown('<p class="main-title">🎵 Chord Flashcards</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("Game Settings")

    st.markdown("**Chord types to include:**")
    col1, col2 = st.columns(2)
    with col1:
        use_triads = st.checkbox("Triads  (I, ii, iii …)", value=st.session_state.use_triads)
    with col2:
        use_sevenths = st.checkbox("7th chords  (Imaj7, V7 …)", value=st.session_state.use_sevenths)

    st.markdown("**Progression length:**")
    prog_length = st.slider(
        "Number of chords per round",
        min_value=2, max_value=8,
        value=st.session_state.prog_length,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:#aaa;font-size:0.95rem'>"
        "A chord progression will appear — enter the Roman numeral for each chord.<br>"
        "<b>+1</b> whole progression correct &nbsp;|&nbsp; "
        "<b>−1</b> any wrong &nbsp;|&nbsp; "
        "<b>60 seconds</b> &nbsp;|&nbsp; "
        "<b>Space</b> = quick submit"
        "</p>",
        unsafe_allow_html=True,
    )

    center = st.columns([1, 2, 1])[1]
    with center:
        disabled = not (use_triads or use_sevenths)
        if st.button("▶ Start Game", use_container_width=True, disabled=disabled):
            st.session_state.use_triads   = use_triads
            st.session_state.use_sevenths = use_sevenths
            st.session_state.prog_length  = prog_length
            start_game()
            st.rerun()

    if disabled:
        st.warning("Please select at least one chord type.")

# ════════════════════════════════════════════════════════════════════════════
# PLAYING SCREEN
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "playing":
    st.components.v1.html(SPACEBAR_JS, height=0)

    remaining = check_time()
    if remaining <= 0:
        st.session_state.screen = "gameover"
        st.rerun()

    draw_timer(remaining)
    draw_score(remaining)

    prog = st.session_state.progression
    key_disp = format_key_display(prog[0][0])
    st.markdown(f'<p class="key-label">Key of {key_disp} Major</p>', unsafe_allow_html=True)

    # Chord names row
    cols = st.columns(len(prog))
    for col, (_, chord, _) in zip(cols, prog):
        with col:
            st.markdown(
                f'<p class="chord-name">{format_chord_display(chord)}</p>',
                unsafe_allow_html=True,
            )

    # Input boxes row
    answers = list(st.session_state.user_answers)
    input_cols = st.columns(len(prog))
    for i, col in enumerate(input_cols):
        with col:
            answers[i] = st.text_input(
                f"ans_{i}",
                value=answers[i],
                key=f"inp_{i}",
                placeholder="?",
                label_visibility="collapsed",
            )
    st.session_state.user_answers = answers

    st.markdown("<br>", unsafe_allow_html=True)
    center = st.columns([1, 2, 1])[1]
    with center:
        if st.button("Submit ↵", use_container_width=True, key="submit_btn"):
            submit_answers()
            st.rerun()

    # auto-refresh timer
    time.sleep(1)
    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# FEEDBACK SCREEN
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "feedback":
    st.components.v1.html(SPACEBAR_JS, height=0)

    remaining = check_time()
    draw_timer(remaining)
    draw_score(remaining)

    prog    = st.session_state.progression
    answers = st.session_state.user_answers
    key_disp = format_key_display(prog[0][0])
    st.markdown(f'<p class="key-label">Key of {key_disp} Major</p>', unsafe_allow_html=True)

    # Determine overall result
    all_ok = all(ans.strip() == item[2] for ans, item in zip(answers, prog))
    if all_ok:
        st.markdown('<p class="fb-ok">✓ Correct! +1</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="fb-bad">✗ Wrong! −1</p>', unsafe_allow_html=True)

    # Per-chord feedback columns
    cols = st.columns(len(prog))
    for col, (_, chord, correct_roman), user_ans in zip(cols, prog, answers):
        with col:
            chord_disp = format_chord_display(chord)
            st.markdown(
                f'<p class="chord-name">{chord_disp}</p>',
                unsafe_allow_html=True,
            )
            user_clean = user_ans.strip()
            if user_clean == correct_roman:
                st.markdown(
                    f'<p class="roman-correct">✓ {correct_roman}</p>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<p class="roman-wrong">'
                    f'✗ {user_clean or "—"}<br>'
                    f'<span style="font-size:0.85rem">({correct_roman})</span>'
                    f'</p>',
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)
    center = st.columns([1, 2, 1])[1]
    with center:
        lbl = "▶ Next  [Space]" if remaining > 0 else "See Results"
        if st.button(lbl, use_container_width=True, key="next_btn"):
            next_round()
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# GAME OVER SCREEN
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "gameover":
    st.markdown('<p class="main-title">🎵 Chord Flashcards</p>', unsafe_allow_html=True)
    st.markdown("---")

    score = st.session_state.score
    emoji = "🎉" if score > 0 else ("😐" if score == 0 else "😬")
    st.markdown(
        f"<p style='text-align:center;font-size:1.5rem;font-weight:700'>"
        f"Time's up! {emoji}</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Final Score", f"{score:+d}")
    c2.metric("Correct ✓",  st.session_state.correct)
    c3.metric("Incorrect ✗", st.session_state.incorrect)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Play Again (same settings)", use_container_width=True):
            start_game()
            st.rerun()
    with col2:
        if st.button("⚙️ Change Settings", use_container_width=True):
            st.session_state.screen = "settings"
            st.rerun()
