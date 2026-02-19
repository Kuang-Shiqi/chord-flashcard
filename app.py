import time
import json
import streamlit as st
from music_theory import (
    build_pool, get_progression,
    format_key_display, format_chord_display,
    build_roman, QUALITIES, QUALITY_IDS,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chord Flashcards", page_icon="🎵", layout="centered")

# ── Default keybindings ───────────────────────────────────────────────────────
DEFAULT_DEGREE_KEYS = {"1":"1","2":"2","3":"3","4":"4","5":"5","6":"6","7":"7"}
DEFAULT_QUALITY_KEYS = {
    "maj":"h", "min":"j", "dim":"k",
    "maj7":"l", "dom7":";", "min7":"'", "hdim":"n",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main-title  { text-align:center; font-size:2rem; font-weight:700; margin-bottom:.2rem; }
  .key-label   { text-align:center; font-size:1.1rem; color:#888; margin-bottom:.5rem; }
  .cards-row {
    display:flex; gap:.5rem; justify-content:center;
    padding:.3rem 0;
  }
  .chord-card  {
    border:2px solid #e0e0e0; border-radius:12px;
    padding:.5rem .4rem .3rem; min-width:70px;
    text-align:center; transition:border-color .15s, box-shadow .15s;
    cursor:pointer; user-select:none;
  }
  .chord-card.active {
    border-color:#6366f1; box-shadow:0 0 0 3px rgba(99,102,241,.25);
  }
  .chord-card.filled { border-color:#94a3b8; }
  .chord-name  { font-size:2.2rem; font-weight:800; line-height:1.1; margin:0; }
  .chord-ans   { font-size:1.05rem; font-weight:700; color:#6366f1; min-height:1.5rem; margin:.2rem 0 0; }
  .chord-ans.empty { color:#cbd5e1; }
  .score-row   { display:flex;justify-content:center;gap:2.5rem;
                 font-size:1.05rem;margin-bottom:.3rem; }
  .score-val   { font-weight:700;font-size:1.35rem; }
  .timer-bar   { height:8px;border-radius:4px;background:#e0e0e0;margin:.3rem 0 .7rem; }
  .timer-fill  { height:8px;border-radius:4px; }
  .fb-ok  { text-align:center;font-size:1.3rem;font-weight:700;color:#22c55e;padding:.3rem 0; }
  .fb-bad { text-align:center;font-size:1.3rem;font-weight:700;color:#ef4444;padding:.3rem 0; }
  div[data-testid="stButton"] > button {
    width:100%;font-size:1.05rem;font-weight:700;padding:.4rem 0;border-radius:8px;
  }
  .hint { font-size:.8rem;color:#94a3b8;text-align:center;margin-top:.2rem; }
  .fb-chord-ok  { color:#22c55e;font-weight:700;font-size:1rem;text-align:center; }
  .fb-chord-bad { color:#ef4444;font-weight:700;font-size:1rem;text-align:center; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "use_triads": True, "use_sevenths": True, "prog_length": 4,
        "timer_on": True, "timer_seconds": 60, "auto_advance": True,
        "degree_keys": dict(DEFAULT_DEGREE_KEYS),
        "quality_keys": dict(DEFAULT_QUALITY_KEYS),
        "screen": "settings",
        "progression": None,
        "slot_degrees": [], "slot_quals": [],
        "active_slot": 0, "start_time": None,
        "score": 0, "correct": 0, "incorrect": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ── Helpers ───────────────────────────────────────────────────────────────────
def slot_roman(i):
    d = st.session_state.slot_degrees[i]
    q = st.session_state.slot_quals[i]
    if d is None: return None
    return build_roman(d, q if q else "maj")

def start_game():
    st.session_state.score = 0
    st.session_state.correct = 0
    st.session_state.incorrect = 0
    st.session_state.start_time = time.time()
    st.session_state.screen = "playing"
    new_round()

def new_round():
    pool = build_pool(st.session_state.use_triads, st.session_state.use_sevenths)
    prog = get_progression(pool, st.session_state.prog_length)
    st.session_state.progression = prog
    st.session_state.slot_degrees = [None] * len(prog)
    st.session_state.slot_quals = [None] * len(prog)
    st.session_state.active_slot = 0

def check_remaining():
    if not st.session_state.timer_on: return 999999
    return max(0.0, st.session_state.timer_seconds - (time.time() - st.session_state.start_time))

def submit_answers():
    prog = st.session_state.progression
    all_ok = all(slot_roman(i) == prog[i][2] for i in range(len(prog)))
    if all_ok:
        st.session_state.score += 1
        st.session_state.correct += 1
    else:
        st.session_state.score -= 1
        st.session_state.incorrect += 1
    st.session_state.screen = "feedback"

def next_round_fn():
    if st.session_state.timer_on and check_remaining() <= 0:
        st.session_state.screen = "gameover"
    else:
        st.session_state.screen = "playing"
        new_round()

def is_quick_mode():
    return (st.session_state.prog_length == 1 and
            st.session_state.use_triads and
            not st.session_state.use_sevenths)

# diatonic triad quality for each degree (1-indexed)
DIATONIC_TRIAD_QUAL = {1:"maj",2:"min",3:"min",4:"maj",5:"maj",6:"min",7:"dim"}

def set_degree(i, deg):
    st.session_state.slot_degrees[i] = deg
    # In quick mode, auto-set the diatonic quality and submit
    if is_quick_mode():
        st.session_state.slot_quals[i] = DIATONIC_TRIAD_QUAL.get(deg, "maj")
        submit_answers()
        return
    if st.session_state.auto_advance and st.session_state.slot_quals[i] is not None:
        advance_slot()

def set_quality(i, qual):
    st.session_state.slot_quals[i] = qual
    if st.session_state.auto_advance and st.session_state.slot_degrees[i] is not None:
        advance_slot()

def advance_slot():
    n = len(st.session_state.progression)
    nxt = st.session_state.active_slot + 1
    if nxt < n:
        st.session_state.active_slot = nxt

def prev_slot():
    prv = st.session_state.active_slot - 1
    if prv >= 0:
        st.session_state.active_slot = prv

def cycle_quality(direction):
    i = st.session_state.active_slot
    cur = st.session_state.slot_quals[i]
    idx = QUALITY_IDS.index(cur) if cur in QUALITY_IDS else 0
    idx = (idx + direction) % len(QUALITY_IDS)
    st.session_state.slot_quals[i] = QUALITY_IDS[idx]

# ── Timer / score bar ─────────────────────────────────────────────────────────
def draw_timer_bar(remaining):
    if not st.session_state.timer_on: return
    pct = remaining / st.session_state.timer_seconds * 100
    color = "#22c55e" if pct > 40 else ("#f59e0b" if pct > 20 else "#ef4444")
    st.markdown(
        f'<div class="timer-bar"><div class="timer-fill" '
        f'style="width:{pct:.1f}%;background:{color}"></div></div>',
        unsafe_allow_html=True)

def draw_score_row(remaining):
    s = st.session_state
    timer_str = f"⏱ <span class='score-val'>{int(remaining)}s</span>" if s.timer_on else ""
    st.markdown(
        f'<div class="score-row">'
        f'<span>Score <span class="score-val">{s.score:+d}</span></span>'
        f'{timer_str}'
        f'<span>✓ <span class="score-val">{s.correct}</span> '
        f'✗ <span class="score-val">{s.incorrect}</span></span>'
        f'</div>', unsafe_allow_html=True)

# ── Keyboard JS ───────────────────────────────────────────────────────────────
def make_keyboard_js(screen):
    deg_map  = st.session_state.degree_keys
    qual_map = st.session_state.quality_keys
    inv_deg  = json.dumps({v: int(k) for k, v in deg_map.items()})
    inv_qual = json.dumps({v: k for k, v in qual_map.items()})

    deg_labels_js = json.dumps(["I","II","III","IV","V","VI","VII"])
    qual_labels_js = json.dumps([q["label"] for q in QUALITIES])
    qual_ids_js = json.dumps(QUALITY_IDS)

    if screen == "playing_quick":
        # Quick mode: only 1-7 degree keys (buttons labelled "1"–"7")
        action_js = """
        function clickBtnByText(text) {
            const btns = Array.from(window.parent.document.querySelectorAll('button'));
            const b = btns.find(b => b.innerText.trim() === text);
            if (b) b.click();
        }
        window.parent.document.addEventListener('keydown', function(e) {
            if (window.parent.document.activeElement &&
                window.parent.document.activeElement.tagName === 'INPUT') return;
            const key = e.key;
            if (key >= '1' && key <= '7') {
                e.preventDefault();
                clickBtnByText(key);
            }
        });
        """
    elif screen == "playing":
        action_js = f"""
        const DEG_MAP  = {inv_deg};
        const QUAL_MAP = {inv_qual};
        const DEG_LABELS  = {deg_labels_js};
        const QUAL_LABELS = {qual_labels_js};
        const QUAL_IDS    = {qual_ids_js};

        function clickBtnByText(text) {{
            const btns = Array.from(window.parent.document.querySelectorAll('button'));
            const b = btns.find(b => b.innerText.trim() === text);
            if (b) b.click();
        }}

        window.parent.document.addEventListener('keydown', function(e) {{
            if (window.parent.document.activeElement &&
                window.parent.document.activeElement.tagName === 'INPUT') return;
            const key = e.key;
            if (DEG_MAP[key] !== undefined) {{
                e.preventDefault();
                clickBtnByText(DEG_LABELS[DEG_MAP[key] - 1]);
                return;
            }}
            if (QUAL_MAP[key] !== undefined) {{
                e.preventDefault();
                const qid = QUAL_MAP[key];
                const qIdx = QUAL_IDS.indexOf(qid);
                if (qIdx >= 0) clickBtnByText(QUAL_LABELS[qIdx]);
                return;
            }}
            if (key === 'ArrowLeft')  {{ e.preventDefault(); clickBtnByText('\u25c0 Prev'); return; }}
            if (key === 'ArrowRight' || key === ' ') {{ e.preventDefault(); clickBtnByText('Next \u25b6'); return; }}
            if (key === 'ArrowUp')   {{ e.preventDefault(); clickBtnByText('\u2191 Qual'); return; }}
            if (key === 'ArrowDown') {{ e.preventDefault(); clickBtnByText('\u2193 Qual'); return; }}
            if (key === 'Enter')     {{ e.preventDefault(); clickBtnByText('Submit \u21b5'); return; }}
        }});
        """
    elif screen == "feedback":
        action_js = """
        window.parent.document.addEventListener('keydown', function(e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                const btns = Array.from(window.parent.document.querySelectorAll('button'));
                const b = btns.find(b => b.innerText.includes('Next') || b.innerText.includes('Results'));
                if (b) b.click();
            }
        });
        """
    else:
        action_js = ""

    return f"<script>(function(){{ if(window._kbDone) return; window._kbDone=true; {action_js} }})();</script>"

# ════════════════════════════════════════════════════════════════════════════
# SETTINGS SCREEN
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "settings":
    st.markdown('<p class="main-title">🎵 Chord Flashcards</p>', unsafe_allow_html=True)
    st.info("🖥️ Best on desktop — keyboard shortcuts make it way faster! On mobile? Try Quick Mode below.")

    # ── Quick mode button ────────────────────────────────────────────────────
    st.markdown(
        "<p style='text-align:center;color:#888;font-size:.95rem;margin-top:.5rem'>"
        "One chord at a time, triads only, press 1–7 to answer. Great for beginners and mobile!"
        "</p>", unsafe_allow_html=True)
    qcol = st.columns([1,2,1])[1]
    with qcol:
        if st.button("⚡ Quick Mode (triads only)", use_container_width=True, type="primary"):
            st.session_state.use_triads = True
            st.session_state.use_sevenths = False
            st.session_state.prog_length = 1
            st.session_state.timer_on = True
            st.session_state.timer_seconds = 60
            st.session_state.auto_advance = True
            start_game()
            st.rerun()

    st.markdown("---")

    st.subheader("Chord Types")
    c1, c2 = st.columns(2)
    use_triads   = c1.checkbox("Triads  (I ii iii …)",     value=st.session_state.use_triads)
    use_sevenths = c2.checkbox("7th chords  (Imaj7 V7 …)", value=st.session_state.use_sevenths)

    st.subheader("Progression Length")
    prog_length = st.slider("Chords per round", 2, 8, st.session_state.prog_length,
                            label_visibility="collapsed")

    st.subheader("Timer")
    tc1, tc2 = st.columns([1, 3])
    timer_on = tc1.checkbox("Enable timer", value=st.session_state.timer_on)
    timer_seconds = tc2.slider("Duration", 30, 600, st.session_state.timer_seconds, 30,
                               format="%d s", disabled=not timer_on, label_visibility="collapsed")

    st.subheader("Auto-advance")
    auto_advance = st.checkbox(
        "Move to next slot automatically when degree + quality are both set",
        value=st.session_state.auto_advance)

    st.subheader("Keybindings")
    with st.expander("Customise keybindings", expanded=False):
        st.markdown("**Degree keys** (scale degree 1–7):")
        dk = dict(st.session_state.degree_keys)
        dcols = st.columns(7)
        for idx, (deg, _) in enumerate(DEFAULT_DEGREE_KEYS.items()):
            with dcols[idx]:
                dk[deg] = st.text_input(f"Deg {deg}", value=dk[deg], max_chars=1, key=f"dk_{deg}")

        st.markdown("**Quality keys:**")
        qk = dict(st.session_state.quality_keys)
        for q in QUALITIES:
            qk[q["id"]] = st.text_input(
                f"{q['label']} ({build_roman(1, q['id'])})",
                value=qk[q["id"]], max_chars=1, key=f"qk_{q['id']}")

        if st.button("Reset keybindings to default"):
            st.session_state.degree_keys  = dict(DEFAULT_DEGREE_KEYS)
            st.session_state.quality_keys = dict(DEFAULT_QUALITY_KEYS)
            st.rerun()

    with st.expander("How to play / keybind cheatsheet", expanded=False):
        dk_disp = st.session_state.degree_keys
        qk_disp = st.session_state.quality_keys
        st.markdown(f"""
**Goal:** Identify the Roman numeral for each chord in the progression.
**+1** whole progression correct | **−1** any wrong.

**Navigation:** `←` `→` move slots · `Space` next slot · Click card to focus

**Input:** Press **degree key** then **quality key** (auto-advances if on)

| Degree | Key | | Quality | Key | Example (deg 5) |
|--------|-----|-|---------|-----|-----------------|
| I | `{dk_disp['1']}` | | maj | `{qk_disp['maj']}` | V |
| II | `{dk_disp['2']}` | | min | `{qk_disp['min']}` | v |
| III | `{dk_disp['3']}` | | dim | `{qk_disp['dim']}` | v° |
| IV | `{dk_disp['4']}` | | maj7 | `{qk_disp['maj7']}` | Vmaj7 |
| V | `{dk_disp['5']}` | | 7 | `{qk_disp['dom7']}` | V7 |
| VI | `{dk_disp['6']}` | | m7 | `{qk_disp['min7']}` | v7 |
| VII | `{dk_disp['7']}` | | ø7 | `{qk_disp['hdim']}` | vø7 |

**↑ / ↓** cycle quality · **Enter** submit
""")

    st.markdown("---")
    disabled = not (use_triads or use_sevenths)
    col = st.columns([1,2,1])[1]
    with col:
        if st.button("▶ Start Game", use_container_width=True, disabled=disabled):
            st.session_state.use_triads    = use_triads
            st.session_state.use_sevenths  = use_sevenths
            st.session_state.prog_length   = prog_length
            st.session_state.timer_on      = timer_on
            st.session_state.timer_seconds = timer_seconds
            st.session_state.auto_advance  = auto_advance
            st.session_state.degree_keys   = dk
            st.session_state.quality_keys  = qk
            start_game()
            st.rerun()
    if disabled:
        st.warning("Select at least one chord type.")

# ════════════════════════════════════════════════════════════════════════════
# PLAYING SCREEN
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "playing":
    remaining = check_remaining()
    if st.session_state.timer_on and remaining <= 0:
        st.session_state.screen = "gameover"
        st.rerun()

    draw_timer_bar(remaining)
    draw_score_row(remaining)

    prog = st.session_state.progression
    key_disp = format_key_display(prog[0][0])
    st.markdown(f'<p class="key-label">Key of {key_disp} Major</p>', unsafe_allow_html=True)

    # ── Chord cards (HTML flex row) ──────────────────────────────────────────
    active = st.session_state.active_slot
    cards_html = '<div class="cards-row">'
    for i, (_, chord, _) in enumerate(prog):
        rn = slot_roman(i)
        css = "chord-card" + (" active" if i == active else "") + (" filled" if rn else "")
        ans_css = "chord-ans" if rn else "chord-ans empty"
        ans_txt = rn if rn else "?"
        cards_html += (
            f'<div class="{css}">'
            f'<p class="chord-name">{format_chord_display(chord)}</p>'
            f'<p class="{ans_css}">{ans_txt}</p>'
            f'</div>')
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    quick = is_quick_mode()

    # Focus slot buttons (hide in quick mode — only 1 slot)
    if not quick:
        focus_cols = st.columns(len(prog))
        for i, col in enumerate(focus_cols):
            with col:
                lbl = f"● {i+1}" if i == active else f"▸ {i+1}"
                if st.button(lbl, key=f"focus_{i}", use_container_width=True):
                    st.session_state.active_slot = i
                    st.rerun()

    if quick:
        # ── Quick mode: 7 scale-degree buttons labelled 1–7 (4+3 rows) ─────
        st.markdown(
            '<p class="hint">Which scale degree is this chord? Press 1–7</p>',
            unsafe_allow_html=True)
        row1_q = st.columns(4)
        for d in range(1, 5):
            with row1_q[d - 1]:
                if st.button(str(d), key=f"deg_{d}", use_container_width=True):
                    set_degree(active, d)
                    st.rerun()
        row2_q = st.columns([1,1,1,1])
        for idx, d in enumerate(range(5, 8)):
            with row2_q[idx]:
                if st.button(str(d), key=f"deg_{d}", use_container_width=True):
                    set_degree(active, d)
                    st.rerun()
    else:
        # ── Full mode: Degree buttons (row 1: 4, row 2: 3) ──────────────────
        deg_labels = ["I","II","III","IV","V","VI","VII"]
        row1_d = st.columns(4)
        for d in range(1, 5):
            with row1_d[d - 1]:
                cur_deg = st.session_state.slot_degrees[active]
                btn_type = "primary" if cur_deg == d else "secondary"
                if st.button(deg_labels[d-1], key=f"deg_{d}", type=btn_type,
                             use_container_width=True):
                    set_degree(active, d)
                    st.rerun()
        row2_d = st.columns([1,1,1,1])
        for idx, d in enumerate(range(5, 8)):
            with row2_d[idx]:
                cur_deg = st.session_state.slot_degrees[active]
                btn_type = "primary" if cur_deg == d else "secondary"
                if st.button(deg_labels[d-1], key=f"deg_{d}", type=btn_type,
                             use_container_width=True):
                    set_degree(active, d)
                    st.rerun()

        st.markdown("<hr style='margin:.3rem 0;border-color:#e2e8f0'>", unsafe_allow_html=True)

        # ── Quality buttons (row 1: 4, row 2: 3) ────────────────────────────
        row1_q = st.columns(4)
        for idx, q in enumerate(QUALITIES[:4]):
            with row1_q[idx]:
                cur_qual = st.session_state.slot_quals[active]
                btn_type = "primary" if cur_qual == q["id"] else "secondary"
                if st.button(q["label"], key=f"qual_{q['id']}", type=btn_type,
                             use_container_width=True):
                    set_quality(active, q["id"])
                    st.rerun()
        row2_q = st.columns([1,1,1,1])
        for idx, q in enumerate(QUALITIES[4:]):
            with row2_q[idx]:
                cur_qual = st.session_state.slot_quals[active]
                btn_type = "primary" if cur_qual == q["id"] else "secondary"
                if st.button(q["label"], key=f"qual_{q['id']}", type=btn_type,
                             use_container_width=True):
                    set_quality(active, q["id"])
                    st.rerun()

        # ── Nav + Submit ────────────────────────────────────────────────────
        st.markdown("<hr style='margin:.3rem 0;border-color:#e2e8f0'>", unsafe_allow_html=True)
        nav1, nav2, nav3 = st.columns([1,2,1])
        with nav1:
            if st.button("◀ Prev", key="nav_prev", use_container_width=True):
                prev_slot(); st.rerun()
        with nav2:
            if st.button("Submit ↵", key="submit_main",
                         use_container_width=True, type="primary"):
                submit_answers(); st.rerun()
        with nav3:
            if st.button("Next ▶", key="nav_next", use_container_width=True):
                advance_slot(); st.rerun()
        # Quality cycle buttons (for keyboard ↑↓)
        hid1, hid2 = st.columns(2)
        with hid1:
            if st.button("↑ Qual", key="nav_qual_up", use_container_width=True):
                cycle_quality(-1); st.rerun()
        with hid2:
            if st.button("↓ Qual", key="nav_qual_down", use_container_width=True):
                cycle_quality(1); st.rerun()

    if not quick:
        st.markdown(
            '<p class="hint">← → Space = move slots &nbsp;|&nbsp; '
            '↑↓ = cycle quality &nbsp;|&nbsp; Enter = submit</p>',
            unsafe_allow_html=True)

    # Inject keyboard JS (quick mode gets simplified version)
    if quick:
        st.components.v1.html(make_keyboard_js("playing_quick"), height=0)
    else:
        st.components.v1.html(make_keyboard_js("playing"), height=0)

    # auto-refresh for timer
    if st.session_state.timer_on:
        time.sleep(1)
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# FEEDBACK SCREEN
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "feedback":
    remaining = check_remaining()
    draw_timer_bar(remaining)
    draw_score_row(remaining)

    prog = st.session_state.progression
    key_disp = format_key_display(prog[0][0])
    st.markdown(f'<p class="key-label">Key of {key_disp} Major</p>', unsafe_allow_html=True)

    all_ok = all(slot_roman(i) == prog[i][2] for i in range(len(prog)))
    if all_ok:
        st.markdown('<p class="fb-ok">✓ Correct! +1</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="fb-bad">✗ Wrong! −1</p>', unsafe_allow_html=True)

    fb_html = '<div class="cards-row">'
    for i, (_, chord, correct_rn) in enumerate(prog):
        user_rn = slot_roman(i) or "—"
        ok = user_rn == correct_rn
        fb_color = "#22c55e" if ok else "#ef4444"
        icon = "✓" if ok else "✗"
        detail = correct_rn if ok else f"{user_rn}<br><small>({correct_rn})</small>"
        fb_html += (
            f'<div class="chord-card">'
            f'<p class="chord-name">{format_chord_display(chord)}</p>'
            f'<p class="fb-chord-{("ok" if ok else "bad")}">{icon} {detail}</p>'
            f'</div>')
    fb_html += '</div>'
    st.markdown(fb_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col = st.columns([1,2,1])[1]
    with col:
        lbl = "▶ Next [Space/Enter]" if (not st.session_state.timer_on or remaining > 0) else "See Results"
        if st.button(lbl, key="next_btn", use_container_width=True, type="primary"):
            next_round_fn(); st.rerun()

    st.components.v1.html(make_keyboard_js("feedback"), height=0)

# ════════════════════════════════════════════════════════════════════════════
# GAME OVER SCREEN
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "gameover":
    st.markdown('<p class="main-title">🎵 Chord Flashcards</p>', unsafe_allow_html=True)
    st.markdown("---")
    score = st.session_state.score
    emoji = "🎉" if score > 0 else ("😐" if score == 0 else "😬")
    st.markdown(
        f"<p style='text-align:center;font-size:1.5rem;font-weight:700'>Time's up! {emoji}</p>",
        unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Final Score",  f"{score:+d}")
    c2.metric("Correct ✓",   st.session_state.correct)
    c3.metric("Incorrect ✗", st.session_state.incorrect)
    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔄 Play Again", use_container_width=True, type="primary"):
            start_game(); st.rerun()
    with b2:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.screen = "settings"; st.rerun()
