"""Colours and CSS for PhytoCYP Tracker. Every colour in the app is defined in this file; no other file contains a hex value.

The look is a plain reference-entry page: white page, near-black text, hairlines, one navy accent. Colour only ever means the type of
information (the three reference-check words) or the strength of the model's prediction (one blue scale). It never signals good or bad:
no red, green or amber is used (the logo keeps its own colours inside its own image).
"""

# ---------------------------------------------------------------- light and dark palettes
LIGHT = dict(
    bg="#FFFFFF", line="#E5E7EB", ink="#0F172A", muted="#475569", accent="#1F3A5F", num="#1F3A5F", focus="#0B57D0", hover="#F1F5F9",
    btn="#1F3A5F", btn_hover="#172C49", btn_active="#0F2038", btn_ink="#FFFFFF", btn_off="#F1F5F9", btn_off_ink="#475569",
    ref_supported="#1A56B0", ref_contradicted="#7A2F98", ref_untested="#475569", track="#E5E7EB",
    switch_off="#CBD5E1", switch_on="#1F3A5F", knob="#FFFFFF", switch_icon="#475569",
    chart_text="#0F172A", chart_grid="#E5E7EB", bar_low="#A9C4E4", bar_high="#4F86C6", rule="#1F2A44", halo="#FFFFFF",
    field_focus="#1F2A44", band="#F1F5F9", mk_sub="#4F86C6", mk_nti="#8B6FC0", mk_prior="#C9739B", mk_ref="#2F9C95",
)
DARK = dict(
    bg="#0B1220", line="#243044", ink="#E8EDF5", muted="#A9B6C8", accent="#9BBDEC", num="#BCD3F2", focus="#8AB4F8", hover="#152033",
    btn="#2D5A93", btn_hover="#3A6AA6", btn_active="#24497A", btn_ink="#FFFFFF", btn_off="#152033", btn_off_ink="#A9B6C8",
    ref_supported="#86B4F7", ref_contradicted="#D9A9EF", ref_untested="#AAB4C2", track="#243044",
    switch_off="#3B4A63", switch_on="#9BBDEC", knob="#FFFFFF", switch_icon="#E8EDF5",
    chart_text="#E8EDF5", chart_grid="#243044", bar_low="#3B5A80", bar_high="#4E84C8", rule="#E2E8F0", halo="#0B1220",
    field_focus="#E2E8F0", band="#1B2536", mk_sub="#6FA6E8", mk_nti="#AE8CE6", mk_prior="#E58FB4", mk_ref="#4FC3B9",
)

# the four row-marker colours identify the TYPE of information (never the value). The "no red, green or amber status colour" rule is enforced by the explicit allowlist
# (allowed_colours): a colour that is not on it fails the tests, whatever its hue.
MARKER_KEYS = ("mk_sub", "mk_nti", "mk_prior", "mk_ref")

# model probability: one blue sequential scale in five steps (0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0); darker = higher
PROB_SCALE = ["#DCE9F7", "#A9C8EB", "#6FA0DB", "#3E74BE", "#1F3A5F"]
# the same five steps for the dark page: still darker = higher, but every step stays visible on a dark background
PROB_SCALE_DARK = ["#DCE9F7", "#B4CFEE", "#8DB3E4", "#6A98D8", "#4A80C8"]


def allowed_colours():
    """The colours the rendered HTML may contain (used by the tests)."""
    out = set(PROB_SCALE) | set(PROB_SCALE_DARK)
    for pal in (LIGHT, DARK):
        out |= set(pal.values())
    return {c.upper() for c in out}


def prob_step(p):
    """The scale step (0 to 4) for a probability between 0 and 1."""
    return min(int(float(p) / 0.2), 4)


def prob_color(p):
    """The blue step for a probability between 0 and 1 (light page)."""
    return PROB_SCALE[prob_step(p)]


def _icon(path_fill, kind):
    """A 14 px sun or moon as an SVG data URL for use as a CSS background (no external file, no emoji)."""
    fill = path_fill.replace("#", "%23")
    if kind == "sun":
        body = (f"<circle cx='12' cy='12' r='4.2' fill='{fill}'/>"
                + "".join(f"<line x1='12' y1='1.8' x2='12' y2='4.6' stroke='{fill}' stroke-width='2' stroke-linecap='round' transform='rotate({a} 12 12)'/>" for a in range(0, 360, 45)))
    else:
        body = f"<path d='M20.5 14.2A8.6 8.6 0 0 1 9.8 3.5a8.6 8.6 0 1 0 10.7 10.7z' fill='{fill}'/>"
    return f"url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'>{body}</svg>\")"


def css(dark=False):
    """The whole stylesheet for one theme."""
    p = DARK if dark else LIGHT
    sun, moon = _icon(p["switch_icon"], "sun"), _icon(p["switch_icon"], "moon")
    # dark mode only: Streamlit Cloud draws its toolbar GitHub icon as an image with the light-mode text colour (#0F172A) baked in, so it vanishes on the dark page.
    # This one narrow rule turns that icon (and no other toolbar item) light grey. It has no effect in light mode.
    github_icon = '[data-testid="stToolbarActionButtonIcon"] { filter:brightness(0) invert(0.92); }' if dark else ""
    return f"""
:root {{ color-scheme: {"dark" if dark else "light"};
  --bg:{p['bg']}; --line:{p['line']}; --ink:{p['ink']}; --muted:{p['muted']}; --accent:{p['accent']}; --num:{p['num']}; --focus:{p['focus']}; --hover:{p['hover']};
  --ref-supported:{p['ref_supported']}; --ref-contradicted:{p['ref_contradicted']}; --ref-untested:{p['ref_untested']}; --track:{p['track']}; --band:{p['band']}; --field-focus:{p['field_focus']}; --mk-sub:{p['mk_sub']}; --mk-nti:{p['mk_nti']}; --mk-prior:{p['mk_prior']}; --mk-ref:{p['mk_ref']}; 
  {' '.join(f'--p{i}:{c};' for i, c in enumerate(PROB_SCALE_DARK if dark else PROB_SCALE))} }}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {{ background:var(--bg) !important; color:var(--ink) !important; }}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{ background:transparent !important; }}
.stApp, .stApp p, .stApp li, .stApp label, .stApp span:not([data-testid="stIconMaterial"]), .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp input, .stApp button
  {{ font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; text-transform:none !important; letter-spacing:normal !important; }}
.stApp [data-testid="stMarkdownContainer"] p:not([class]), .stApp [data-testid="stMarkdownContainer"] li:not([class]) {{ color:var(--ink); font-size:1rem; line-height:1.6; }}
.stApp [data-testid="stMarkdownContainer"] a {{ color:var(--accent); }}
.stApp [data-testid="stWidgetLabel"] p, .stApp label p {{ color:var(--ink) !important; font-size:15px; }}

/* the page: one plain column; the sidebar is separated by a hairline only */
[data-testid="stMainBlockContainer"], .block-container {{ max-width:912px; box-sizing:border-box; margin:0 auto; padding:68px 16px 48px; position:relative; }}      /* the tab row starts at y = 84 px: 24 px under Streamlit's 60 px header band (68 px + the 16 px Streamlit leaves above the first block) */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {{ background:var(--bg) !important; border-right:1px solid var(--line); }}
[data-testid="stSidebarContent"] {{ padding:0 !important; }}
[data-testid="stSidebarHeader"] {{ position:absolute; top:16px; right:12px; height:auto; padding:0; margin:0; z-index:3; background:transparent !important; }}
[data-testid="stSidebarUserContent"] {{ padding:84px 20px 28px 20px !important; }}      /* the logo block starts on the same line as the tab row (84 px); the collapse arrow sits in the header band above it */
[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {{ gap:0 !important; }}
      /* 40 px logo + 12 px gap: the switch lines up with the text, not the logo */
[class*="st-key-side-herb"] {{ margin-top:44px; }}      /* 28 px gap after the brand, plus the 16 px Streamlit pulls back under a markdown block */
[class*="st-key-side-drug"] {{ margin-top:20px; }}
[data-testid="stExpandSidebarButton"] *, [data-testid="stSidebarCollapseButton"] *, [data-testid^="stTabsScroll"] * {{ color:var(--muted) !important; }}
:focus-visible {{ outline:2px solid var(--focus) !important; outline-offset:2px; }}

/* brand */
.pc-brand {{ display:flex; align-items:flex-start; gap:12px; width:fit-content; max-width:100%; color:var(--ink); }}
.pc-brand .pc-name {{ width:fit-content; white-space:nowrap; font-size:1rem; font-weight:600; line-height:1.2; color:var(--ink); display:block; }}
.pc-brand .pc-sub {{ font-size:13px; line-height:1.3; color:var(--muted); display:block; margin-top:2px; }}
.stApp .pc-caption {{ font-size:13px; font-style:italic; color:var(--muted); margin:.3rem 0 0; line-height:1.4; }}
.stApp .pc-small {{ font-size:14px; color:var(--muted); margin:.35rem 0 0; }}
.pc-gate {{ max-width:40rem; margin:1.5rem 0 0; }}
.pc-gate h2 {{ margin:0 0 .6rem; font-size:1.3rem; font-weight:600; }}
.pc-gate hr {{ border:0; border-top:1px solid var(--line); margin:1.2rem 0; }}

/* the result: title, probability, one sentence, four finding rows, one link */
.pc-head > div:first-child {{ flex:1 1 420px; min-width:0; }}
.pc-head {{ display:flex; justify-content:space-between; align-items:flex-end; gap:1.5rem; flex-wrap:wrap; margin:.2rem 0 1rem; }}
.pc-title {{ font-size:26px; font-weight:500; line-height:1.25; margin:0; color:var(--ink); }}
.pc-meta {{ font-size:14px; color:var(--muted); margin:.3rem 0 0; }}
.pc-prob {{ text-align:right; min-width:10rem; margin-left:auto; }}
.pc-prob .pc-plabel {{ display:block; font-size:14px; color:var(--muted); }}
.pc-prob .pc-num {{ display:block; font-size:46px; font-weight:500; line-height:1.1; color:var(--num); }}
.pc-probbar {{ height:4px; border-radius:999px; background:var(--track); margin:.4rem 0 0; overflow:hidden; }}
.pc-probbar span {{ display:block; height:100%; }}
.pc-sentence {{ font-size:17px; line-height:1.6; margin:0 0 1rem; padding:12px 16px; border:0; border-radius:0; background:var(--band); color:var(--ink); }}
.pc-sentence b, .pc-ref {{ font-weight:700; }}
.pc-ref-Supported {{ color:var(--ref-supported); }} .pc-ref-Contradicted {{ color:var(--ref-contradicted); }} .pc-ref-Untested {{ color:var(--ref-untested); }}
.pc-rows {{ border-top:1px solid var(--line); }}
.pc-row {{ position:relative; display:grid; grid-template-columns:170px 1fr; column-gap:24px; padding:.9rem 0 .9rem 18px; border-bottom:1px solid var(--line); }}
.pc-row + .pc-row {{ margin-top:8px; }}      /* each coloured marker is its own block, with a gap above the next one */
.pc-row::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:5px; background:var(--mk-sub); }}
.pc-row[data-row="nti"]::before {{ background:var(--mk-nti); }} .pc-row[data-row="prior"]::before {{ background:var(--mk-prior); }} .pc-row[data-row="reference"]::before {{ background:var(--mk-ref); }}
.pc-fn {{ font-size:15px; color:var(--muted); line-height:1.5; }}
.pc-fv {{ font-size:18px; font-weight:500; line-height:1.4; color:var(--ink); overflow-wrap:anywhere; }}
.pc-fx {{ font-size:14px; color:var(--muted); line-height:1.5; margin:.15rem 0 0; }}
.pc-row details {{ margin:.25rem 0 0; }}
.pc-link, .pc-row summary, .pc-aboutmodel summary {{ cursor:pointer; color:var(--accent); font-size:14px; text-decoration:underline; list-style:none; display:inline-block; }}
.pc-row summary::-webkit-details-marker, .pc-aboutmodel summary::-webkit-details-marker {{ display:none; }}
.pc-source {{ margin:.5rem 0 .2rem 1rem; padding-left:.9rem; border-left:2px solid var(--line); font-size:14px; line-height:1.6; color:var(--ink); }}
.pc-source p {{ margin:.2rem 0; font-size:14px; }}
.pc-aboutmodel {{ margin:1rem 0 0; }}
.pc-aboutmodel .pc-source {{ margin-left:0; }}
.pc-absent {{ border-top:1px solid var(--line); padding-top:.8rem; }}
.pc-absent p {{ margin:.55rem 0 0; color:var(--ink); }} .pc-absent .pc-value {{ font-weight:600; font-size:18px; }}
.pc-gap {{ height:2rem; }}

/* tables: same left edge and width as the text around them; hairlines only */
.pc-tablewrap {{ overflow-x:auto; max-width:100%; margin:.8rem 0; }}
.pc-table {{ border-collapse:collapse; width:100%; font-size:15px; font-variant-numeric:tabular-nums; }}
.pc-table, .pc-table thead, .pc-table tbody, .pc-table tr {{ border:0 !important; background:transparent; }}      /* Streamlit adds its own faint row borders; only the palette hairlines below are kept */
.pc-table th, .pc-table td {{ text-align:left; padding:10px 12px; border:0; border-bottom:1px solid var(--line); color:var(--ink); vertical-align:top; background:transparent; }}
.pc-table th {{ font-size:14px; color:var(--muted); font-weight:600; border-bottom:1px solid var(--muted); }}
.pc-table th:first-child, .pc-table td:first-child {{ width:40%; padding-left:0; }}
.pc-table.pc-fit {{ display:grid; grid-template-columns:repeat(4, auto); column-gap:0; width:100%; }}      /* the herb overview table: as wide as the chart; the four auto columns share the free width equally, so the gaps are even */
.pc-table.pc-fit thead, .pc-table.pc-fit tbody, .pc-table.pc-fit tr {{ display:contents; }}
.pc-table.pc-fit th, .pc-table.pc-fit td {{ padding:10px 12px 10px 0; width:auto; }}      /* the gap is padding, so each row hairline runs unbroken */
@media (min-width: 641px) {{ .pc-table th {{ white-space:nowrap; }} }}      /* on a computer no header wraps onto a second row */
.pc-prose {{ max-width:760px; }}
.pc-prose p, .pc-prose li {{ color:var(--ink); line-height:1.6; }}
.pc-prose h3 {{ margin:1.8rem 0 .4rem; font-size:1.15rem; font-weight:600; color:var(--ink); }}
.pc-prose h4 {{ margin:1.2rem 0 .3rem; font-size:1rem; font-weight:600; color:var(--ink); }}
.pc-prose details {{ margin:.5rem 0; }}
.pc-prose summary {{ cursor:pointer; color:var(--accent); font-size:15px; text-decoration:underline; list-style:none; display:inline-block; }}
.pc-prose summary::-webkit-details-marker {{ display:none; }}
.pc-prose .pc-source {{ margin:.4rem 0 .6rem 0; }}
.pc-prose dt {{ font-weight:600; margin-top:.8rem; }} .pc-prose dd {{ margin:.1rem 0 0 0; }}

/* Streamlit Community Cloud adds a "Fork" and a GitHub button to the toolbar. No configuration setting hides only the Fork button, so this narrow rule hides the toolbar button that carries a text label (Fork). The GitHub button is an icon without a label and stays. */
[data-testid="stToolbarActionButton"]:has([data-testid="stToolbarActionButtonLabel"]) {{ display:none !important; }}

{github_icon}

/* tabs: plain text with an underline for the active one. Streamlit 1.66 builds tabs and selectboxes with react-aria, not BaseWeb */
[role="tablist"] {{ gap:1.6rem; border-bottom:1px solid var(--line) !important; background:transparent !important; }}
[data-testid="stTab"] {{ background:transparent !important; padding:.6rem .1rem; border-bottom:2px solid transparent !important; box-shadow:none !important; }}
[data-testid="stTab"], [data-testid="stTab"] p, [data-testid="stTab"] div {{ color:var(--muted) !important; font-weight:500; font-size:15px; }}
[data-testid="stTab"][aria-selected="true"] {{ border-bottom:2px solid var(--accent) !important; margin-bottom:-1px; }}
[data-testid="stTab"][aria-selected="true"], [data-testid="stTab"][aria-selected="true"] p, [data-testid="stTab"][aria-selected="true"] div {{ color:var(--ink) !important; font-weight:600; }}
[role="tablist"] > :not([data-testid="stTab"]) {{ background:transparent !important; }}
[data-testid="stTabsScrollRight"] {{ background-image:linear-gradient(to right, transparent, var(--bg) 40%) !important; }}
[data-testid="stTabsScrollLeft"] {{ background-image:linear-gradient(to left, transparent, var(--bg) 40%) !important; }}

/* selectboxes. The input group carries the border and the focus ring; the typing field inside it has NO outline of its own
   (an outline on the inner field drew a thick vertical bar beside the arrow). The dropdown list is a portal outside the app tree, so it is styled by role. */
[data-testid="stSelectbox"] [role="group"] {{ background:var(--bg) !important; border:1px solid var(--line) !important; border-radius:4px !important; color:var(--ink) !important; }}
[data-testid="stSelectbox"] [role="group"], [data-testid="stSelectbox"] [role="group"][data-focus-within], [data-testid="stSelectbox"] [role="group"][data-focused] {{ box-shadow:none !important; }}
[data-testid="stSelectbox"] [role="group"]:focus-within, [data-testid="stSelectbox"] [role="group"][data-focus-within="true"], [data-testid="stSelectbox"] [role="group"][data-focused="true"]
  {{ outline:none !important; box-shadow:none !important; border:1px solid var(--field-focus) !important; }}      /* a thin slate border on the outer box only: no blue, no glow, nothing on the inner typing field */
[data-testid="stSelectbox"] input {{ color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; background:transparent !important; caret-color:var(--ink); outline:none !important; box-shadow:none !important; border:0 !important; }}
[data-testid="stSelectbox"] svg {{ fill:var(--muted) !important; color:var(--muted) !important; }}
[data-trigger], [data-trigger] > div, [role="listbox"] {{ background:var(--bg) !important; color:var(--ink) !important; border-radius:4px; }}
[data-trigger] {{ border:1px solid var(--line) !important; box-shadow:none !important; }}
[role="option"], [role="option"] div, [role="option"] span {{ background:transparent !important; color:var(--ink) !important; font-family:inherit; border-radius:0; }}
[role="option"][aria-selected="true"], [role="option"][data-hovered], [role="option"][data-focused], [role="option"]:hover {{ background:var(--hover) !important; }}
input::placeholder {{ color:var(--muted) !important; opacity:1; }}

/* buttons: white text on the navy button in every state, both themes (the earlier rule lost to the general paragraph colour rule, hence the long selector) */
.stApp button[data-testid="stBaseButton-secondary"] {{ border-radius:4px; font-weight:600; background:{p['btn']} !important; border:1px solid {p['btn']} !important; }}
.stApp button[data-testid="stBaseButton-secondary"]:hover {{ background:{p['btn_hover']} !important; border-color:{p['btn_hover']} !important; }}
.stApp button[data-testid="stBaseButton-secondary"]:focus, .stApp button[data-testid="stBaseButton-secondary"]:focus-visible {{ background:{p['btn_hover']} !important; border-color:{p['btn_hover']} !important; }}
.stApp button[data-testid="stBaseButton-secondary"]:active {{ background:{p['btn_active']} !important; border-color:{p['btn_active']} !important; }}
.stApp button[data-testid="stBaseButton-secondary"] *, .stApp button[data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] p {{ color:{p['btn_ink']} !important; font-size:15px; }}
.stApp button[data-testid="stBaseButton-secondary"]:disabled {{ background:{p['btn_off']} !important; border:1px solid var(--line) !important; }}
.stApp button[data-testid="stBaseButton-secondary"]:disabled *, .stApp button[data-testid="stBaseButton-secondary"]:disabled [data-testid="stMarkdownContainer"] p {{ color:{p['btn_off_ink']} !important; }}
[data-testid="stCheckbox"] label span {{ color:var(--ink) !important; }}
[data-testid="stCheckbox"] [data-baseweb="checkbox"] > span:first-child {{ border-color:var(--muted) !important; border-radius:4px !important; }}

/* the theme switch sits at the top right of the main area, on the tab row (on the gate: beside the name), right-aligned with the content column and left of Streamlit's three-dot menu */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-themeswitch"]) {{ position:absolute; top:93px; right:16px; width:auto; z-index:1000001; }}
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-enterkey"]) {{ position:absolute; width:1px; height:1px; overflow:hidden; opacity:0; pointer-events:none; }}
/* the theme switch: ONE 44 x 24 px switch, sun on the left and moon on the right; off = light, on = dark.
   Streamlit 1.66 renders st.toggle as label > [hidden input role=switch] + track div > knob div + label-text div; the keyed container scopes the rules. */
[class*="st-key-themeswitch"] label {{ display:flex; align-items:center; min-height:24px; cursor:pointer; position:relative; }}
[class*="st-key-themeswitch"] label > div:first-of-type {{ width:44px !important; min-width:44px; height:24px !important; border-radius:999px !important; margin:0 !important; position:relative;
  background-color:{p['switch_off']} !important; background-image:{sun}, {moon}; background-repeat:no-repeat, no-repeat; background-size:14px 14px, 14px 14px; background-position:6px 5px, 24px 5px; }}
[class*="st-key-themeswitch"] label > div:first-of-type > div {{ background:{p['knob']} !important; width:20px !important; height:20px !important; border-radius:50% !important; position:absolute !important;
  top:2px !important; left:2px !important; box-shadow:0 1px 2px rgba(15,23,42,.35) !important; transition:transform .15s; }}
[class*="st-key-themeswitch"] label:has(input:checked) > div:first-of-type {{ background-color:{p['switch_on']} !important; }}
[class*="st-key-themeswitch"] label:has(input:checked) > div:first-of-type > div {{ transform:translateX(20px) !important; }}
[class*="st-key-themeswitch"] label:has(input:focus-visible) > div:first-of-type {{ outline:2px solid var(--focus); outline-offset:2px; }}
[class*="st-key-themeswitch"] [data-testid="stWidgetLabel"] {{ position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap; }}   /* label text hidden visually; the input keeps the accessible name */

@media (max-width: 640px) {{
  [data-testid="stMainBlockContainer"], .block-container {{ padding-left:1rem; padding-right:1rem; }}
  .pc-row {{ grid-template-columns:1fr; row-gap:.2rem; }}
  .pc-prob {{ text-align:left; width:100%; }}
  .pc-title {{ font-size:23px; }}
  [data-testid="stLayoutWrapper"]:has(> [class*="st-key-themeswitch"]) {{ top:18px; right:96px; }}      /* on a phone: the top row, left of the Cloud GitHub icon (36 px wide, 48 px from the right edge, measured on the live page) and the three-dot menu */
}}
"""
