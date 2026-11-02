"""PhytoCYP Tracker - Streamlit entry point. Layout and widgets only; the content comes from render.py and the look from theme.py.

State lives in st.session_state (memory) only: the notice tick box, the theme switch and the two selections. Nothing is written to a file,
nothing is logged, and nothing the visitor selects leaves the session.
"""

from pathlib import Path

import streamlit as st

import render
import theme

APP = Path(__file__).parent
# "auto": expanded on a computer, collapsed on a phone-width screen
st.set_page_config(page_title="PhytoCYP Tracker", page_icon=str(APP / "assets" / "logo.svg"), layout="wide", initial_sidebar_state="auto")


@st.cache_data(show_spinner=False)
def load():
    return render.load_data(APP / "data")


D = load()
DRUGS = {d["drug"]: d for d in D["drugs"]}

# the theme: ALWAYS light at the start of a session, whatever the computer is set to
st.session_state.setdefault("dark", False)
dark = st.session_state["dark"]
st.markdown(f"<style>{theme.css(dark)}</style>", unsafe_allow_html=True)


def _remember_switch():
    st.session_state["dark"] = st.session_state["dark_switch"]


def theme_switch():
    with st.container(key="themeswitch"):
        st.toggle("Dark mode", value=st.session_state["dark"], key="dark_switch", on_change=_remember_switch)


def _enter():
    # a callback runs before the page is redrawn, so one press is enough: the next run already sees "entered"
    st.session_state["entered"] = True


# the one theme switch, on every screen: placed at the top right of the main area by the stylesheet
theme_switch()
# a switch is operated with Space by default; this 0-pixel helper also lets Enter operate it (it only listens for the Enter key while the switch has focus)
with st.container(key="enterkey"):
    st.iframe("""<!doctype html><html><body><script>
    const d = window.parent.document;
    if (!d.__pcEnterSwitch) { d.__pcEnterSwitch = true;
      d.addEventListener('keydown', function (e) { const a = d.activeElement; if (e.key === 'Enter' && a && a.matches && a.matches('input[role="switch"]')) { e.preventDefault(); a.click(); } }, true); }
    </script></body></html>""", width=1, height=1)

# ---------------------------------------------------------------- the gate
if not st.session_state.get("entered"):
    st.markdown(render.brand_html("Gate"), unsafe_allow_html=True)
    st.markdown(render.gate_html(), unsafe_allow_html=True)
    ack = st.checkbox("I have read and understood this notice.", key="ack")
    st.button("Continue", disabled=not ack, on_click=_enter, key="continue")
    st.stop()

# ---------------------------------------------------------------- the sidebar
with st.sidebar:
    st.markdown(render.brand_html("Side"), unsafe_allow_html=True)
    with st.container(key="side-herb"):
        herb = st.selectbox("Herb", D["herbs"], index=None, placeholder="Select a herb", key="herb")
    with st.container(key="side-drug"):
        drug = st.selectbox("Drug", list(DRUGS), index=None, placeholder="Search for a drug",
                            format_func=lambda name: render.drug_label(DRUGS[name]), key="drug")
        st.markdown('<p class="pc-caption">Each drug is listed with its enzyme</p>', unsafe_allow_html=True)

# ---------------------------------------------------------------- the four tabs
tab_result, tab_overview, tab_model, tab_about = st.tabs(["Result", "Herb overview", "Model and limits", "About"])

with tab_result:
    if not (herb and drug):
        st.markdown('<p class="pc-small">Choose a herb and a drug in the sidebar. The result appears here.</p>', unsafe_allow_html=True)
    else:
        st.markdown(render.cards_html(render.lookup(D, herb, drug)), unsafe_allow_html=True)

with tab_overview:
    if not herb:
        st.markdown('<p class="pc-small">Choose a herb in the sidebar to see its overview.</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="pc-title" role="heading" aria-level="2" style="margin:.4rem 0 .4rem">{render.esc(herb)}</div>', unsafe_allow_html=True)
        if not render.herb_assessable(D, herb):
            st.markdown('<p class="pc-value" style="font-size:18px;font-weight:600;margin:.2rem 0">The model could not assess this herb</p>'
                        '<p class="pc-small">None of its compounds is similar enough to the compounds the model learned from, so no probability exists for any enzyme.</p>',
                        unsafe_allow_html=True)
        st.markdown(render.overview_table_html(D, herb), unsafe_allow_html=True)
        chart = render.overview_chart(D, herb, dark)
        if chart is not None:
            st.altair_chart(chart, use_container_width=True, theme=None)
            st.markdown(f'<p class="pc-small">{render.esc(render.OVERVIEW_BRIGHTER if dark else render.OVERVIEW_DARKER)}</p><p class="pc-small">{render.esc(render.OVERVIEW_NOTE)}</p>', unsafe_allow_html=True)

with tab_model:
    st.markdown(render.model_limits_html(D), unsafe_allow_html=True)

with tab_about:
    st.markdown(render.about_html(D["facts"]), unsafe_allow_html=True)

