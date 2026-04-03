import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import base64
import streamlit.components.v1 as components

# ── Path helper — works locally AND on Streamlit Cloud ───────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
def dp(filename):
    return os.path.join(BASE, "data", filename)

st.set_page_config(
    layout="wide",
    page_title="Serbia Protests",
    page_icon="🇷🇸"
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
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

  [data-testid="stPlotlyChart"] > div {
    background: transparent !important;
  }

  /* Toggle CSS */
  div[data-testid="stCheckbox"] input[type="checkbox"] {
    position: absolute; opacity: 0; width: 0; height: 0; pointer-events: none;
  }
  div[data-testid="stCheckbox"] label {
    display: flex; align-items: center; gap: 10px; cursor: pointer;
    font-family: 'Libre Baskerville', serif; font-size: 0.85rem; color: #888;
    user-select: none; position: relative; padding-left: 56px;
  }
  div[data-testid="stCheckbox"] label::before {
    content: ''; position: absolute; left: 0; top: 50%;
    transform: translateY(-50%); width: 48px; height: 24px;
    background: #cc3333; border-radius: 24px; transition: background 0.2s;
  }
  div[data-testid="stCheckbox"] label::after {
    content: ''; position: absolute; left: 3px; top: 50%;
    transform: translateY(-50%); width: 18px; height: 18px;
    background: white; border-radius: 50%; transition: transform 0.2s;
  }
  div[data-testid="stCheckbox"]:has(input:checked) label::after {
    transform: translateY(-50%) translateX(24px);
  }
  div[data-testid="stCheckbox"]:has(input:checked) label {
    color: #e8e0d5;
  }
</style>
""", unsafe_allow_html=True)


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Data Investigation · Serbia · 2018–2026</p>', unsafe_allow_html=True)

st.markdown("""
<h1 class="headline">[Headline:<br>Title of the piece]</h1>
""", unsafe_allow_html=True)

st.markdown('<p class="teaser">[Teaser: 2–3 sentence introduction to the story]</p>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── INTRO WITH IMAGE ──────────────────────────────────────────────────────────
col_img, col_intro = st.columns([1, 1.5], gap="large")

with col_img:
    st.image("test.png", use_container_width=True)

with col_intro:
    st.markdown("""
    <p class="body-text">[Placeholder: introductory paragraph — what happened, why it matters.]</p>
    <p class="body-text">[Placeholder: second paragraph with more context.]</p>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── SECTION 1: LINE CHART ─────────────────────────────────────────────────────
weekly = pd.read_csv(dp("weekly_serbia.csv"))
weekly["week"] = pd.to_datetime(weekly["week"])

# Toggle row
tcol1, tcol2, tcol3 = st.columns([1.2, 0.4, 3])
with tcol1:
    st.markdown('<p style="text-align:right; color:#e8e0d5; font-size:0.85rem; margin-top:6px; font-family:Libre Baskerville,serif;">All protests</p>', unsafe_allow_html=True)
with tcol2:
    show_youth = st.checkbox("", key="youth_toggle")
with tcol3:
    st.markdown('<p style="color:#555; font-size:0.85rem; margin-top:6px; font-family:Libre Baskerville,serif;">Youth protests only</p>', unsafe_allow_html=True)

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
    <div style="border:1px solid #2a2a2a; border-radius:4px; padding:1.2rem;
         margin-top:2.5rem; background:#111;">
      <p style="font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase;
         color:#555; margin:0 0 0.6rem 0;">Context</p>
      <p style="font-size:0.9rem; line-height:1.75; color:#a89f94; margin:0;
         font-family:Libre Baskerville,serif;">
        [Placeholder: short context box — key finding, what the reader should take away.]
      </p>
    </div>
    """, unsafe_allow_html=True)

with col_chart:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weekly["week"], y=ghost_y, name=ghost_name, mode="lines",
        line=dict(color="rgba(255,255,255,0.08)", width=1.2), hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=weekly["week"], y=active_y, name=active_name, mode="lines",
        line=dict(color=active_color, width=2),
        hovertemplate="<b>%{x|%b %Y}</b><br>%{y} events<extra></extra>"
    ))
    fig.add_vline(x="2024-11-01", line_dash="dash", line_color="#cc3333", line_width=1.5)
    y_dot_series = weekly.loc[weekly["week"] == "2024-11-01",
                              "n_student_events" if show_youth else "n_events"]
    y_dot = int(y_dot_series.values[0]) if len(y_dot_series) > 0 else 20
    fig.add_trace(go.Scatter(
        x=["2024-11-01"], y=[y_dot], mode="markers+text",
        marker=dict(color="#cc3333", size=9),
        text=["Nov 2024 | Collapse of the Novi Sad train station canopy"],
        textposition="top right",
        textfont=dict(color="#cc3333", size=11, family="Libre Baskerville,serif"),
        hovertemplate="<b>Nov 2024 — Novi Sad collapse</b><br>[Placeholder: context]<extra></extra>",
        showlegend=False
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0f0f0f",
        font=dict(family="Libre Baskerville,Times New Roman,serif", color="#888"),
        title=dict(
            text="Demonstrations in Serbia<br><sup>1 January 2018 – 31 March 2026 · Source: ACLED (acleddata.com)</sup>",
            font=dict(size=17, color="#e8e0d5"), x=0, xanchor="left"
        ),
        xaxis=dict(tickformat="%b %Y", dtick="M12", tickangle=0,
                   gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)", color="#666"),
        yaxis=dict(title="Number of protests per week",
                   gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)",
                   color="#666", title_font=dict(size=11), zeroline=False),
        legend=dict(orientation="h", y=-0.12, x=0,
                    font=dict(color="#555", size=11), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=90, b=60, l=65, r=20),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1a1a1a", bordercolor="#333",
                        font=dict(color="#e8e0d5", family="Libre Baskerville,serif")),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── SECTION 2: SCROLLYTELLING MAP ────────────────────────────────────────────
# Map data: protests_serbia.csv — all protest events with coordinates.
# Student flag: keyword match on notes field (same as R script).
# Opacity per dot = frequency of protests at that location in same month.
# Media files encoded as base64 so iframe can load them without security errors.

# ── Encode media as base64 ────────────────────────────────────────────────────
def file_to_b64(path, mime):
    full = os.path.join(BASE, path)
    with open(full, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

audio_b64 = file_to_b64("test.mp3", "audio/mpeg")
photo_b64 = file_to_b64("test.png",  "image/png")

# ── Load protests ─────────────────────────────────────────────────────────────
protests_df = pd.read_csv(dp("protests_serbia.csv"))
protests_df["event_date"] = pd.to_datetime(protests_df["event_date"])
keywords = "student|university|fakultet|faculty|omladina|youth|young people"
protests_df["is_student"] = protests_df["notes"].str.contains(keywords, case=False, na=False)

def make_points(df, special_popups=None):
    df = df.dropna(subset=["latitude","longitude"]).copy()
    df["month_loc"] = df["location"].str.lower() + "_" + df["event_date"].dt.to_period("M").astype(str)
    counts = df["month_loc"].value_counts().to_dict()
    max_count = max(counts.values()) if counts else 1
    points = []
    for r in df.itertuples():
        date_str  = str(r.event_date.date())
        loc_lower = r.location.lower()
        opacity   = round(0.25 + 0.65 * (counts.get(r.month_loc, 1) / max_count), 2)
        popup     = special_popups.get((loc_lower, date_str)) if special_popups else None
        points.append({
            "lat": float(r.latitude), "lon": float(r.longitude),
            "student": bool(r.is_student), "location": r.location,
            "date": date_str, "opacity": opacity, "popup": popup,
        })
    return points

# ── Phase data ────────────────────────────────────────────────────────────────
map_data = {}

# ACT 1 — November 2024, zooms to Novi Sad
map_data["act1"] = make_points(protests_df[
    (protests_df["event_date"] >= "2024-11-01") &
    (protests_df["event_date"] <  "2024-12-01")
])

# ACT 2 — Nov 2024 – Feb 2025, voice note + photo popup
map_data["act2"] = make_points(
    protests_df[
        (protests_df["event_date"] >= "2024-11-01") &
        (protests_df["event_date"] <  "2025-03-01")
    ],
    special_popups={
        ("novi sad", "2025-02-28"): {
            "type": "audio", "file": audio_b64,
            "caption": "Voice note — Novi Sad, 28 February 2025",
        },
        ("belgrade - savski venac", "2025-02-24"): {
            "type": "photo", "file": photo_b64,
            "caption": "Protest — Belgrade, 24 February 2025",
        },
    }
)

# ACT 3 — Mar 2025 – Feb 2026
map_data["act3"] = make_points(protests_df[
    (protests_df["event_date"] >= "2025-03-01") &
    (protests_df["event_date"] <  "2026-03-01")
])

# ACT 4 — March 2026
map_data["act4"] = make_points(protests_df[
    protests_df["event_date"] >= "2026-03-01"
])

map_data_json = json.dumps(map_data)

# ═══════════════════════════════════════════════════════════════════════════════
# TEXT CONTENT — edit strings marked with  # ◀ TEXT HERE
# ═══════════════════════════════════════════════════════════════════════════════
acts_1_2 = [
    {
        "period":  "November 2024",                          # ◀ TEXT HERE
        "heading": "[Heading: November 2024]",               # ◀ TEXT HERE
        "body":    "[Text: first paragraph]",                # ◀ TEXT HERE
        "body2":   "[Text: second paragraph]",               # ◀ TEXT HERE
        "map_key": "act1", "zoom_novi": True,
    },
    {
        "period":  "November 2024 – February 2025",          # ◀ TEXT HERE
        "heading": "[Heading: Nov 2024 – Feb 2025]",         # ◀ TEXT HERE
        "body":    "[Text: first paragraph]",                # ◀ TEXT HERE
        "body2":   "[Text: second paragraph]",               # ◀ TEXT HERE
        "map_key": "act2", "zoom_novi": False,
    },
]

acts_3_4 = [
    {
        "period":  "March 2025 – February 2026",             # ◀ TEXT HERE
        "heading": "[Heading: Mar 2025 – Feb 2026]",         # ◀ TEXT HERE
        "body":    "[Text: first paragraph]",                # ◀ TEXT HERE
        "body2":   "[Text: second paragraph]",               # ◀ TEXT HERE
        "map_key": "act3", "zoom_novi": False,
    },
    {
        "period":  "March 2026",                             # ◀ TEXT HERE
        "heading": "[Heading: March 2026]",                  # ◀ TEXT HERE
        "body":    "[Text: first paragraph]",                # ◀ TEXT HERE
        "body2":   "[Text: second paragraph]",               # ◀ TEXT HERE
        "map_key": "act4", "zoom_novi": False,
    },
]

# ── Scrollytelling HTML builder ───────────────────────────────────────────────
def make_scrolly(acts_data, map_data_json, height=660):
    acts_json = json.dumps(acts_data)
    return f"""
<html><head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0a0a0a; font-family:'Times New Roman',serif; color:#e8e0d5; height:{height}px; overflow:hidden; }}
#scrolly {{ display:flex; height:{height}px; width:100%; }}
#steps {{ flex:0 0 40%; height:{height}px; overflow-y:scroll; padding:0 1.5rem 0 0.5rem; scrollbar-width:none; }}
#steps::-webkit-scrollbar {{ display:none; }}
#map-col {{ flex:0 0 60%; height:{height}px; position:relative; }}
#map {{ width:100%; height:100%; border-radius:3px; }}
.step {{ min-height:{height-60}px; display:flex; flex-direction:column; justify-content:center; padding:2rem 0; border-bottom:1px solid #1e1e1e; opacity:0.3; transition:opacity 0.5s; }}
.step.active {{ opacity:1; }}
.step:last-child {{ min-height:400px; border-bottom:none; }}
.s-period {{ font-size:0.62rem; letter-spacing:0.18em; text-transform:uppercase; color:#cc3333; margin-bottom:0.3rem; }}
.s-heading {{ font-size:1.25rem; font-weight:normal; color:#e8e0d5; line-height:1.3; margin-bottom:0.9rem; margin-top:0.4rem; }}
.s-body {{ font-size:0.88rem; line-height:1.85; color:#a89f94; margin-bottom:0.7rem; }}
#period-lbl {{ position:absolute; top:14px; left:14px; background:rgba(10,10,10,0.9); border:1px solid #2a2a2a; border-radius:3px; padding:6px 12px; z-index:1000; font-size:0.62rem; letter-spacing:0.15em; text-transform:uppercase; color:#cc3333; pointer-events:none; }}
#legend {{ position:absolute; bottom:14px; left:14px; background:rgba(10,10,10,0.9); border:1px solid #2a2a2a; border-radius:3px; padding:10px 14px; z-index:1000; font-size:11px; color:#a89f94; pointer-events:none; }}
.li {{ display:flex; align-items:center; gap:7px; margin-bottom:5px; }}
.li:last-child {{ margin-bottom:0; }}
.dot {{ width:8px; height:8px; border-radius:50%; flex-shrink:0; }}
.op-row {{ display:flex; align-items:center; gap:4px; margin-top:7px; padding-top:7px; border-top:1px solid #2a2a2a; font-size:10px; color:#555; }}
.op-dot {{ width:9px; height:9px; border-radius:50%; background:#e07b39; flex-shrink:0; }}
.leaflet-popup-content-wrapper {{ background:#111 !important; border:1px solid #333 !important; border-radius:3px !important; box-shadow:none !important; color:#e8e0d5 !important; font-family:'Times New Roman',serif !important; }}
.leaflet-popup-tip {{ background:#111 !important; }}
.leaflet-popup-content {{ margin:10px 14px !important; min-width:180px; }}
.p-caption {{ font-size:10px; color:#666; margin:5px 0 4px 0; }}
.p-audio {{ width:100%; margin-top:4px; }}
.p-img {{ width:180px; border-radius:2px; display:block; margin-top:4px; }}
.leaflet-popup-close-button {{ color:#888 !important; }}
.leaflet-tile-pane {{ filter:grayscale(0.15) brightness(0.93); }}
.leaflet-control-attribution {{ display:none; }}
.leaflet-control-zoom a {{ background:#fff !important; color:#333 !important; border-color:#ccc !important; }}
.leaflet-tooltip {{ background:#111; border:1px solid #333; color:#ccc; font-size:11px; padding:3px 7px; border-radius:2px; box-shadow:none; font-family:'Times New Roman',serif; }}
</style>
</head><body>
<div id="scrolly">
  <div id="steps"></div>
  <div id="map-col">
    <div id="map"></div>
    <div id="period-lbl"></div>
    <div id="legend">
      <div class="li"><div class="dot" style="background:#e07b39;"></div><span>Protest event (1 dot = 1 event)</span></div>
      <div class="li"><div class="dot" style="background:#7ab8f5;"></div><span>Student protest</span></div>
      <div class="li" id="l-novi" style="display:none;"><div class="dot" style="background:#cc3333;width:10px;height:10px;"></div><span>Novi Sad — collapse site</span></div>
      <div class="li" id="l-audio" style="display:none;"><span style="font-size:14px;line-height:1;">🎙</span><span>Click marker for voice note</span></div>
      <div class="li" id="l-photo" style="display:none;"><span style="font-size:14px;line-height:1;">📷</span><span>Click marker for photo</span></div>
      <div class="op-row">
        <div class="op-dot" style="opacity:0.25;"></div>
        <div class="op-dot" style="opacity:0.55;"></div>
        <div class="op-dot" style="opacity:0.9;"></div>
        <span style="margin-left:2px;">Opacity = protest frequency at location</span>
      </div>
    </div>
  </div>
</div>
<script>
const DATA = {map_data_json};
const ACTS = {acts_json};

const stepsEl = document.getElementById('steps');
ACTS.forEach((a,i) => {{
  const d = document.createElement('div');
  d.className = 'step'+(i===0?' active':'');
  d.dataset.idx = i;
  d.innerHTML = `<div class="s-period">${{a.period}}</div><h2 class="s-heading">${{a.heading}}</h2><p class="s-body">${{a.body}}</p><p class="s-body">${{a.body2}}</p>`;
  stepsEl.appendChild(d);
}});

const map = L.map('map',{{center:[44.2,21.0],zoom:7,zoomControl:true,scrollWheelZoom:false}});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{subdomains:'abcd',maxZoom:12}}).addTo(map);

const pLayer = L.layerGroup().addTo(map);
const nLayer = L.layerGroup();
L.circleMarker([45.2671,19.8335],{{radius:18,color:'#cc3333',weight:1.5,fillColor:'#cc3333',fillOpacity:0.15}}).addTo(nLayer);
L.circleMarker([45.2671,19.8335],{{radius:5,color:'#cc3333',weight:0,fillColor:'#cc3333',fillOpacity:1}}).bindPopup('<b>Novi Sad</b><br>Train station canopy collapse<br>1 November 2024').addTo(nLayer);

function render(act) {{
  pLayer.clearLayers();
  const pts = DATA[act.map_key]||[];
  const MAX = 900;
  const step = pts.length>MAX ? Math.ceil(pts.length/MAX) : 1;
  pts.forEach((p,i) => {{
    if (i%step!==0 && !p.popup) return;
    let marker;
    if (p.popup) {{
      const emoji = p.popup.type==='audio' ? '🎙' : '📷';
      const icon = L.divIcon({{html:`<div style="font-size:20px;line-height:1;filter:drop-shadow(0 1px 3px rgba(0,0,0,0.8));cursor:pointer;">${{emoji}}</div>`,className:'',iconAnchor:[10,10]}});
      marker = L.marker([p.lat,p.lon],{{icon}});
      let html = `<b>${{p.location}}</b> &middot; ${{p.date}}`;
      if (p.popup.type==='audio') {{
        html += `<p class="p-caption">${{p.popup.caption}}</p><audio class="p-audio" controls><source src="${{p.popup.file}}" type="audio/mpeg">Your browser does not support audio.</audio>`;
      }} else {{
        html += `<p class="p-caption">${{p.popup.caption}}</p><img class="p-img" src="${{p.popup.file}}" alt="${{p.popup.caption}}">`;
      }}
      marker.bindPopup(html,{{maxWidth:220,minWidth:180}});
    }} else {{
      const color = p.student?'#7ab8f5':'#e07b39';
      marker = L.circleMarker([p.lat,p.lon],{{radius:p.student?4:3,color,weight:0,fillColor:color,fillOpacity:p.opacity||0.6}});
      marker.bindTooltip(`${{p.location}} &middot; ${{p.date}}`,{{permanent:false,direction:'top'}});
    }}
    marker.addTo(pLayer);
  }});
  if (act.zoom_novi) {{
    map.addLayer(nLayer);
    map.setView([45.2671,19.8335],10,{{animate:true,duration:1.2}});
    document.getElementById('l-novi').style.display='flex';
  }} else {{
    map.removeLayer(nLayer);
    map.setView([44.2,21.0],7,{{animate:true,duration:1.2}});
    document.getElementById('l-novi').style.display='none';
  }}
  document.getElementById('period-lbl').textContent=act.period;
  const hasAudio=(DATA[act.map_key]||[]).some(p=>p.popup&&p.popup.type==='audio');
  const hasPhoto=(DATA[act.map_key]||[]).some(p=>p.popup&&p.popup.type==='photo');
  document.getElementById('l-audio').style.display=hasAudio?'flex':'none';
  document.getElementById('l-photo').style.display=hasPhoto?'flex':'none';
}}

let cur=0;
render(ACTS[0]);
const sd=document.getElementById('steps');
sd.addEventListener('scroll',()=>{{
  const mid=sd.scrollTop+sd.clientHeight*0.5;
  let a=0;
  document.querySelectorAll('.step').forEach((el,i)=>{{if(el.offsetTop<=mid)a=i;}});
  if(a!==cur){{
    cur=a;
    document.querySelectorAll('.step').forEach(s=>s.classList.remove('active'));
    document.querySelectorAll('.step')[a].classList.add('active');
    render(ACTS[a]);
  }}
}});
</script>
</body></html>
"""

# ── Render ACT 1 + 2 ──────────────────────────────────────────────────────────
components.html(make_scrolly(acts_1_2, map_data_json), height=660, scrolling=False)


# ── INTERLUDE: LINE CHART ─────────────────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid #1e1e1e; border-bottom:1px solid #1e1e1e;
     padding:1.8rem 0; margin:0; display:flex; align-items:center; gap:1.5rem;">
  <div style="flex:1; height:1px; background:#1e1e1e;"></div>
  <p style="font-size:0.65rem; letter-spacing:0.2em; text-transform:uppercase;
     color:#cc3333; white-space:nowrap; margin:0;">The Data</p>
  <div style="flex:1; height:1px; background:#1e1e1e;"></div>
</div>
""", unsafe_allow_html=True)

col_chart, col_text = st.columns([1.8, 1], gap="large")

with col_text:
    st.markdown("""
    <div style="display:flex; flex-direction:column; justify-content:center; height:100%; padding-top:1rem;">
      <p style="font-size:0.62rem; letter-spacing:0.18em; text-transform:uppercase; color:#cc3333; margin-bottom:0.3rem;">The Data</p>
      <p style="font-size:0.65rem; letter-spacing:0.1em; color:#444; margin-bottom:0.9rem; text-transform:uppercase;">January 2018 – March 2026</p>
      <h2 style="font-size:1.25rem; font-weight:normal; color:#e8e0d5; line-height:1.3; margin-bottom:0.9rem; font-family:'Libre Baskerville',serif;">
        [Heading: what the data shows]
      </h2>
      <p style="font-size:0.88rem; line-height:1.85; color:#a89f94; margin-bottom:0.7rem; font-family:'Libre Baskerville',serif;">
        [Text: explain what the chart shows]
      </p>
      <p style="font-size:0.88rem; line-height:1.85; color:#a89f94; font-family:'Libre Baskerville',serif;">
        [Text: reference ITS finding — +43 protests per week]
      </p>
    </div>
    """, unsafe_allow_html=True)

with col_chart:
    tcol1, tcol2, tcol3 = st.columns([1.2, 0.4, 3])
    with tcol1:
        st.markdown('<p style="text-align:right; color:#e8e0d5; font-size:0.85rem; margin-top:6px; font-family:Libre Baskerville,serif;">All protests</p>', unsafe_allow_html=True)
    with tcol2:
        show_youth_2 = st.checkbox("", key="youth_toggle_2")
    with tcol3:
        st.markdown('<p style="color:#555; font-size:0.85rem; margin-top:6px; font-family:Libre Baskerville,serif;">Youth protests only</p>', unsafe_allow_html=True)

    weekly2 = pd.read_csv(dp("weekly_serbia.csv"))
    weekly2["week"] = pd.to_datetime(weekly2["week"])

    if show_youth_2:
        active_y2, active_name2, active_color2 = weekly2["n_student_events"], "Youth protests only", COLOR_YOUTH
        ghost_y2,  ghost_name2                 = weekly2["n_events"], "All protests"
    else:
        active_y2, active_name2, active_color2 = weekly2["n_events"], "All protests", COLOR_ALL
        ghost_y2,  ghost_name2                 = weekly2["n_student_events"], "Youth protests only"

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=weekly2["week"], y=ghost_y2, name=ghost_name2, mode="lines",
        line=dict(color="rgba(255,255,255,0.08)", width=1.2), hoverinfo="skip"
    ))
    fig2.add_trace(go.Scatter(
        x=weekly2["week"], y=active_y2, name=active_name2, mode="lines",
        line=dict(color=active_color2, width=2),
        hovertemplate="<b>%{x|%b %Y}</b><br>%{y} events<extra></extra>"
    ))
    fig2.add_vline(x="2024-11-01", line_dash="dash", line_color="#cc3333", line_width=1.5)
    fig2.add_annotation(
        x="2024-11-01", y=1, yref="paper", text="Nov 2024", showarrow=False,
        xanchor="left", xshift=5,
        font=dict(color="#cc3333", size=10, family="Libre Baskerville,serif"),
        bgcolor="rgba(0,0,0,0)"
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0f0f0f",
        font=dict(family="Libre Baskerville,Times New Roman,serif", color="#888"),
        title=dict(
            text="Demonstrations in Serbia<br><sup>1 January 2018 – 31 March 2026 · Source: ACLED</sup>",
            font=dict(size=15, color="#e8e0d5"), x=0, xanchor="left"
        ),
        xaxis=dict(tickformat="%b %Y", dtick="M12",
                   gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)", color="#666"),
        yaxis=dict(title="Protests per week",
                   gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)",
                   color="#666", title_font=dict(size=11), zeroline=False),
        legend=dict(orientation="h", y=-0.15, x=0,
                    font=dict(color="#555", size=11), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=80, b=60, l=60, r=20),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1a1a1a", bordercolor="#333", font=dict(color="#e8e0d5")),
        height=460
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div style="border-top:1px solid #1e1e1e; margin:0;"></div>', unsafe_allow_html=True)


# ── Render ACT 3 + 4 ──────────────────────────────────────────────────────────
components.html(make_scrolly(acts_3_4, map_data_json), height=660, scrolling=False)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<p style="font-size:0.75rem; color:#444; text-align:center; margin-top:3rem;">
Data Source: Armed Conflict Location & Event Data (ACLED), 2026.
Serbia, January 2018 – March 2026. acleddata.com
</p>
""", unsafe_allow_html=True)