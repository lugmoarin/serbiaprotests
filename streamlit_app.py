import streamlit as st
import plotly.express as px
from utils.data_processing_serbia import load_monthly

st.set_page_config(
    layout="wide",
    page_title="Serbia Protests",
    page_icon="🇷🇸"
)

# ── GLOBAL CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

  html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
  [data-testid="block-container"], .stApp {
    background-color: #0a0a0a !important;
    color: #e8e0d5 !important;
  }

  #MainMenu, header, footer { visibility: hidden; }

  [data-testid="block-container"] {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1100px !important;
    margin: 0 auto !important;
  }

  * {
    font-family: 'Libre Baskerville', 'Times New Roman', serif !important;
  }

  .headline {
    font-size: 3.2rem;
    font-weight: normal;
    line-height: 1.15;
    color: #e8e0d5;
    margin-bottom: 1rem;
    letter-spacing: -0.5px;
  }

  .teaser {
    font-size: 1.2rem;
    line-height: 1.7;
    color: #a89f94;
    max-width: 680px;
    margin-bottom: 2.5rem;
    font-style: italic;
  }

  .divider {
    border: none;
    border-top: 1px solid #2a2a2a;
    margin: 2.5rem 0;
  }

  .section-label {
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 0.5rem;
  }

  .body-text {
    font-size: 1.05rem;
    line-height: 1.85;
    color: #c8c0b5;
    margin-bottom: 1.2rem;
  }

  .stat-number {
    font-size: 3.5rem;
    color: #e8e0d5;
    line-height: 1;
    margin-bottom: 0.2rem;
  }

  .stat-label {
    font-size: 0.85rem;
    color: #666;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  [data-testid="stPlotlyChart"] > div {
    background: transparent !important;
  }
</style>
""", unsafe_allow_html=True)


# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Data Investigation · Serbia · 2018–2026</p>', unsafe_allow_html=True)

st.markdown("""
<h1 class="headline">[Headline:<br>Title of the piece]</h1>
""", unsafe_allow_html=True)

st.markdown('<p class="teaser">[Teaser: 2–3 sentence introduction to the story]</p>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── INTRO WITH IMAGE ─────────────────────────────────────────────────────────
col_img, col_intro = st.columns([1, 1.5], gap="large")

with col_img:
    st.image("test.png", use_container_width=True)

with col_intro:
    st.markdown("""
    <p class="body-text">[Placeholder: full-width introductory paragraph. This text sets 
    the scene before the chart appears — what happened, why it matters, what the reader 
    is about to see.]</p>
    <p class="body-text">[Placeholder: second paragraph with more context.]</p>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── SECTION 1: LINE CHART ────────────────────────────────────────────────────
from utils.data_processing_serbia import load_weekly
import plotly.graph_objects as go

weekly = load_weekly()

# Toggle CSS
st.markdown("""
<style>
div[data-testid="stCheckbox"] input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
  pointer-events: none;
}
div[data-testid="stCheckbox"] label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-family: 'Libre Baskerville', serif;
  font-size: 0.85rem;
  color: #888;
  user-select: none;
  position: relative;
  padding-left: 56px;
}
div[data-testid="stCheckbox"] label::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 24px;
  background: #cc3333;
  border-radius: 24px;
  transition: background 0.2s;
}
div[data-testid="stCheckbox"] label::after {
  content: '';
  position: absolute;
  left: 3px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
}
div[data-testid="stCheckbox"]:has(input:checked) label::after {
  transform: translateY(-50%) translateX(24px);
}
div[data-testid="stCheckbox"]:has(input:checked) label {
  color: #e8e0d5;
}
</style>
""", unsafe_allow_html=True)

# Toggle row
tcol1, tcol2, tcol3 = st.columns([1.2, 0.4, 3])
with tcol1:
    st.markdown('<p style="text-align:right; color:#e8e0d5; font-size:0.85rem; margin-top:6px; font-family: Libre Baskerville, serif;">All protests</p>', unsafe_allow_html=True)
with tcol2:
    show_youth = st.checkbox("", key="youth_toggle")
with tcol3:
    st.markdown('<p style="color:#555; font-size:0.85rem; margin-top:6px; font-family: Libre Baskerville, serif;">Youth protests only</p>', unsafe_allow_html=True)

# Colors
COLOR_ALL   = "#4a90d9"
COLOR_YOUTH = "#e07b39"

if show_youth:
    active_y, active_name, active_color = weekly["n_student_events"], "Youth protests only", COLOR_YOUTH
    ghost_y,  ghost_name               = weekly["n_events"], "All protests"
else:
    active_y, active_name, active_color = weekly["n_events"], "All protests", COLOR_ALL
    ghost_y,  ghost_name               = weekly["n_student_events"], "Youth protests only"

col_chart, col_text = st.columns([3, 1], gap="large")

with col_text:
    st.markdown("""
    <div style="
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 1.2rem;
        margin-top: 2.5rem;
        background: #111;
    ">
        <p style="font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:#555; margin:0 0 0.6rem 0;">Context</p>
        <p style="font-size:0.9rem; line-height:1.75; color:#a89f94; margin:0; font-family: Libre Baskerville, serif;">
            [Placeholder: short context box — 3–4 sentences summarising the key finding. 
            What should the reader take away?]
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_chart:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=weekly["week"], y=ghost_y,
        name=ghost_name, mode="lines",
        line=dict(color="rgba(255,255,255,0.08)", width=1.2),
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=weekly["week"], y=active_y,
        name=active_name, mode="lines",
        line=dict(color=active_color, width=2),
        hovertemplate="<b>%{x|%b %Y}</b><br>%{y} events<extra></extra>"
    ))

    fig.add_vline(x="2024-11-01", line_dash="dash", line_color="#cc3333", line_width=1.5)

    y_dot_series = weekly.loc[weekly["week"] == "2024-11-01", "n_student_events" if show_youth else "n_events"]
    y_dot = int(y_dot_series.values[0]) if len(y_dot_series) > 0 else 20

    fig.add_trace(go.Scatter(
        x=["2024-11-01"], y=[y_dot],
        mode="markers+text",
        marker=dict(color="#cc3333", size=9),
        text=["Nov 2024 | Collapse of the Novi Sad train station canopy"],
        textposition="top right",
        textfont=dict(color="#cc3333", size=11, family="Libre Baskerville, serif"),
        hovertemplate="<b>Nov 2024 — Novi Sad collapse</b><br>[Placeholder: brief context about the event]<extra></extra>",
        showlegend=False
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0f0f0f",
        font=dict(family="Libre Baskerville, Times New Roman, serif", color="#888"),
        title=dict(
            text="Demonstrations in Serbia<br><sup>1 January 2018 – 31 March 2026 · Source: ACLED (acleddata.com)</sup>",
            font=dict(size=17, color="#e8e0d5"),
            x=0, xanchor="left"
        ),
        xaxis=dict(
            tickformat="%b %Y", dtick="M12", tickangle=0,
            gridcolor="rgba(255,255,255,0.05)",
            linecolor="rgba(255,255,255,0.1)",
            color="#666"
        ),
        yaxis=dict(
            title="Number of protests per week",
            gridcolor="rgba(255,255,255,0.05)",
            linecolor="rgba(255,255,255,0.1)",
            color="#666", title_font=dict(size=11), zeroline=False
        ),
        legend=dict(
            orientation="h", y=-0.12, x=0,
            font=dict(color="#555", size=11),
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(t=90, b=60, l=65, r=20),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1a1a1a", bordercolor="#333",
            font=dict(color="#e8e0d5", family="Libre Baskerville, serif")
        ),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── SECTION 2: MAP ───────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Geography of Dissent</p>', unsafe_allow_html=True)

col3, col4 = st.columns([1.6, 1], gap="large")

with col3:
    st.info("🗺️ Map will appear here")

with col4:
    st.markdown("""
    <p class="body-text">[Text: Geographic spread of protests across Serbia]</p>
    <p class="body-text">[Text: Analysis of which cities and regions were most affected]</p>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<p style="font-size:0.75rem; color:#444; text-align:center; margin-top:3rem;">
Data Source: Armed Conflict Location & Event Data (ACLED), 2026. 
Serbia, January 2018 – March 2026. acleddata.com
</p>
""", unsafe_allow_html=True)