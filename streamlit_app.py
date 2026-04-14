import os
import json
import base64
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

BASE = os.path.dirname(os.path.abspath(__file__))
def dp(f): return os.path.join(BASE, "data", f)

st.set_page_config(layout="wide", page_title="Serbia Protests", page_icon="🇷🇸")

# ── Keywords (from assign4_journo.R) ─────────────────────────────────────────
KW = "student|students|student-led|university|fakultet|faculty|youth|young|young people"

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_protests():
    df = pd.read_csv(dp("protests_serbia.csv"))
    df["event_date"] = pd.to_datetime(df["event_date"])
    df["is_student"] = (
    df["notes"].str.contains(KW, case=False, na=False) &
    ~df["notes"].str.contains("oppose student-led protests", case=False, na=False)
)
    df["month"] = df["event_date"].dt.to_period("M").astype(str)
    return df

@st.cache_data
def load_weekly():
    df = pd.read_csv(dp("weekly_serbia.csv"))
    df["week"] = pd.to_datetime(df["week"])
    return df

@st.cache_data
def get_weekly_json():
    df = load_weekly()
    return json.dumps([
        {"w": str(r["week"].date()), "a": int(r["n_events"]), "y": int(r["n_student_events"])}
        for _, r in df.iterrows()
    ])

@st.cache_data
def get_map_json():
    df = load_protests()
    post = df[df["event_date"] >= "2024-11-01"].dropna(subset=["latitude","longitude"])
    months = sorted(post["month"].unique())
    monthly = {}
    for m in months:
        mdf = post[post["month"] == m]
        step = max(1, len(mdf) // 150)
        monthly[m] = [
            {"la": round(float(r.latitude),4), "lo": round(float(r.longitude),4),
             "s": bool(r.is_student), "n": r.location}
            for i, r in enumerate(mdf.itertuples()) if i % step == 0
        ]
    return json.dumps(monthly), json.dumps(months)

@st.cache_data
def get_bar_json():
    df = load_protests()
    bar = df[(df["event_date"] >= "2025-03-01") & (df["event_date"] <= "2026-03-31")].copy()
    bar["mp"] = bar["event_date"].dt.to_period("M")
    magg = bar.groupby("mp").agg(youth=("is_student","sum")).reset_index()
    magg["ms"] = magg["mp"].dt.strftime("%b %Y")
    return json.dumps([{"m": r["ms"], "y": int(r["youth"])} for _, r in magg.iterrows()])

def file_to_b64(path, mime):
    try:
        with open(path, "rb") as f:
            return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
    except FileNotFoundError:
        return None

weekly_json  = get_weekly_json()
map_json, months_json = get_map_json()
bar_json     = get_bar_json()
n_months     = len(json.loads(months_json))

audio_luka   = file_to_b64(os.path.join(BASE, "LUKA.mp3"),   "audio/mpeg")
audio_vuk    = file_to_b64(os.path.join(BASE, "VUK.mp3"),    "audio/mpeg")
audio_ognjen = file_to_b64(os.path.join(BASE, "OGNJEN.mp3"), "audio/mpeg")

ELECTION_DATA = {
    "Kula":{"sns":"50.52%","stud":"~48%"},
    "Bor":{"sns":"49.2%","stud":"40.3%"},
    "Sevojno":{"sns":"51.48%","stud":"44.84%"},
    "Aranđelovac":{"sns":"52.96%","stud":"44.9%"},
    "Bajina Bašta":{"sns":"53.49%","stud":"41.35%"},
    "Knjaževac":{"sns":"57.11%","stud":"32.9%"},
    "Smederevska Palanka":{"sns":"58%","stud":"29.22%"},
    "Kladovo":{"sns":"71.98%","stud":"26.69%"},
    "Lučani":{"sns":"63.78%","stud":"11 seats"},
    "Majdanpek":{"sns":"65.64%","stud":"—"},
}
ELECTION_COORDS = {
    "Kula":(45.6072,19.5278),"Bor":(44.0769,22.0961),
    "Sevojno":(43.8333,19.9167),"Aranđelovac":(44.3033,20.5572),
    "Bajina Bašta":(43.9711,19.5672),"Knjaževac":(43.5667,22.2578),
    "Smederevska Palanka":(44.3672,20.9578),"Kladovo":(44.6033,22.6078),
    "Lučani":(43.8606,20.1397),"Majdanpek":(44.4167,21.9333),
}
election_json = json.dumps([
    {"n":k,"la":ELECTION_COORDS[k][0],"lo":ELECTION_COORDS[k][1],
     "sns":v["sns"],"stud":v["stud"]}
    for k,v in ELECTION_DATA.items()
])

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,300;1,400&display=swap');

/* ─ Full-bleed layout (needed for header map) ─ */
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] {
  background:#0d0d0d !important; color:#e8e4de !important;
}
#MainMenu,header,footer { visibility:hidden; }
[data-testid="stMainBlockContainer"],
[data-testid="block-container"],
.main .block-container {
  padding:0 !important;
  max-width:100% !important;
  margin:0 !important;
}
* { font-family:'Source Serif 4',Georgia,serif !important; letter-spacing:0 !important; }

/* ─ Typography ─ */
.body-text    { font-size:1rem; line-height:1.9; color:#e8e4de; margin-bottom:.9rem; text-align:justify; hyphens:auto; }
.teaser       { font-size:1.4rem !important; line-height:1.8; color:#9a9490; font-style:italic; font-weight:300; margin-bottom:.4rem; }
.author-line  { font-size:.76rem !important; color:#6a6560; margin:0; line-height:1.4; font-style:italic; }
.sec-divider  { border:none; border-top:1px solid #7a7570; margin:.4rem 0 .6rem; }
.section-title{ font-size:1.2rem; font-weight:600; color:#f0ece6; margin:.8rem 0 .5rem; line-height:1.3; }
.chart-title  { font-size:1.5rem !important; font-weight:600; color:#f0ece6; margin-bottom:.3rem; }
.chart-caption{ font-size:.86rem; color:#8a8580; margin-top:.4rem; line-height:1.6; font-style:italic; }
.divider      { border:none; border-top:1px solid #222; margin:1.2rem 0; }
.quote-box    { border-left:3px solid #d97941; padding:.9rem 0 .9rem 1.4rem; margin:1rem 0; }
.quote-text   { font-size:1.5rem; font-weight:600; font-style:italic; color:#f0ece6; line-height:1.4; margin-bottom:.4rem; }
.quote-attr   { font-size:.82rem; color:#6a6560; font-style:normal; }
.ctx-box      { border-left:1px solid #333; padding:0 0 0 1.2rem; }
.ctx-text     { font-size:.88rem; line-height:1.8; color:#c8c4be; text-align:justify; }

/* ─ Expander: all three (Serbia in Context, Sources, Methodology) ─
   Fixes overlapping "arrow_right" text; makes titles bold; rounds corners; darker bg ─ */
[data-testid="stExpander"] {
  border:1.5px solid #d97941 !important;
  border-radius:12px !important;
  background:#111 !important;
  margin-bottom:8px !important;
  overflow:hidden !important;
}
[data-testid="stExpander"] details { background:#111 !important; border-radius:12px !important; }
[data-testid="stExpander"] summary {
  list-style:none !important;
  position:relative !important;
  padding:12px 44px 12px 16px !important;
  background:#111 !important;
  border-radius:12px !important;
  cursor:pointer !important;
}
[data-testid="stExpander"] summary:hover { background:#161616 !important; }
[data-testid="stExpander"] summary::-webkit-details-marker { display:none !important; }
/* The * { font-family: Source Serif 4 !important } breaks Material Symbols font
   so icon text like "arrow_down" renders as literal text in Source Serif 4.
   Fix: set ALL text in summary to background color #111 (invisible),
   then ONLY restore the <p> that holds the actual title. */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
  color:#111 !important;
}
[data-testid="stExpanderToggleIcon"],
[data-testid="stExpander"] summary svg {
  display:none !important;
}
/* Restore only the title <p> */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary p * {
  color:#c0bbb5 !important;
  font-size:15px !important;
  font-weight:600 !important;
  display:inline !important;
  margin:0 !important;
}
/* Custom +/− indicator */
[data-testid="stExpander"] summary::after {
  content:'+'; position:absolute; right:16px; top:50%;
  transform:translateY(-50%); color:#5a5651;
  font-size:18px; font-weight:300; font-family:Georgia,serif !important;
}
[data-testid="stExpander"] details[open] summary::after { content:'−'; }
/* Expanded content area */
[data-testid="stExpanderDetails"] {
  background:#dedad6 !important;
  border-radius:0 0 12px 12px !important;
  padding:14px 16px 16px !important;
  border-top:1px solid #c8c4be !important;
}
[data-testid="stExpanderDetails"] p,
[data-testid="stExpanderDetails"] .body-text {
  color:#1a1a1a !important; font-size:14px !important;
  line-height:1.85 !important; text-align:justify !important;
  margin-bottom:.6rem !important;
}
[data-testid="stExpanderDetails"] a { color:#cc3333 !important; }
</style>
""", unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# Beg1 ── HEADER MAP (full-bleed, edge-to-edge)
# Europe map greyed out; Serbia border in orange; headline overlaid left
# Serbia's real border from world-atlas (Natural Earth, ISO 688) — exact match to map tiles
# ◀ Beg1: replace headline text in the #headline div below
# ═══════════════════════════════════════════════════════════════════════════════
components.html("""
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson-client.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{background:#0d0d0d;width:100%;height:100%;overflow:hidden;}
#mapwrap{position:relative;width:100%;height:400px;}
#map{width:100%;height:400px;}
.leaflet-tile-pane{filter:grayscale(1) brightness(0.28) contrast(1.2);}
.leaflet-control-attribution,.leaflet-control-zoom{display:none;}
#overlay{
  position:absolute;top:0;left:0;width:100%;height:400px;
  z-index:1000;pointer-events:none;
  display:flex;align-items:center;padding:0 4%;
}
#headline{
  font-family:Georgia,serif;
  font-size:clamp(2rem,4vw,3.8rem);
  font-weight:600;color:#f0ece6;line-height:1.2;max-width:50%;
  text-shadow:0 2px 16px rgba(0,0,0,0.95),0 0 60px rgba(0,0,0,0.85);
}
#fade{
  position:absolute;bottom:0;left:0;width:100%;height:90px;
  background:linear-gradient(to bottom,transparent,#0d0d0d);
  z-index:999;pointer-events:none;
}
</style></head><body>
<div id="mapwrap">
  <div id="map"></div>
  <div id="fade"></div>
  <div id="overlay">
    <div id="headline">
      <!-- ◀ Beg1: HEADLINE — replace with actual title -->
      Anatomy of Serbia’s<br>Youth Protests
    </div>
  </div>
</div>
<script>
// Center: Europe on left for title, Serbia fully visible on right
const map=L.map("map",{
  center:[46,15],zoom:5,
  zoomControl:false,scrollWheelZoom:false,
  dragging:false,touchZoom:false,doubleClickZoom:false,keyboard:false
});
L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
  {subdomains:"abcd",maxZoom:7}).addTo(map);

// Serbia real border from Natural Earth via world-atlas npm package.
// ISO 3166-1 numeric 688 = Serbia.
// fillOpacity:0 = outline only, no fill. Exactly matches the map tile borders.
fetch("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json")
  .then(r=>r.json())
  .then(world=>{
    const all=topojson.feature(world,world.objects.countries);
    const serbia=all.features.find(f=>f.id==="688");
    if(serbia) L.geoJSON(serbia,{style:{color:"#d97941",weight:2,opacity:1,fillOpacity:0}}).addTo(map);
  }).catch(()=>{});
</script>
</body></html>
""", height=400, scrolling=False)


# ── Sentinel helper for timeline tracking ─────────────────────────────────────
def sentinel(i):
    st.markdown(
        f'<div id="tl-s{i}" style="height:0;margin:0;padding:0;pointer-events:none;"></div>',
        unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN TWO-COLUMN LAYOUT
# Left column (0.09): timeline OV1
# Right column (0.91): all article content
# Padding added via extra thin outer columns
# ═══════════════════════════════════════════════════════════════════════════════
_, col_tl, col_content, _ = st.columns([0.02, 0.08, 0.80, 0.10], gap="small")

# ── OV1: Timeline column ──────────────────────────────────────────────────────
with col_tl:
    components.html("""
<html><head><style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{background:#0d0d0d;width:100%;height:100%;}
#wrap{width:100%;min-height:4920px;position:relative;
  display:flex;flex-direction:column;align-items:center;padding:16px 0;}
svg{display:block;width:20px;flex:1;overflow:visible;min-height:5120px;}
.lbl{position:absolute;right:2px;transform:translateY(-50%);
  font-size:11.1px;font-family:Georgia,serif;white-space:nowrap;transition:color .4s;}
</style></head><body>
<div id="wrap"><svg id="svg" preserveAspectRatio="none"></svg></div>
<script>
const times=['11:52','11:53','11:54','11:55','11:56','11:57','11:58','11:59',
  '12:00','12:01','12:02','12:03','12:04','12:05','12:06','12:07','12:08'];
const N=times.length;
const wrap=document.getElementById('wrap');
const svg=document.getElementById('svg');
let circles=[],labels=[],current=0;

function draw(){
  const h=wrap.offsetHeight-32;if(h<200)return;
  svg.style.height=h+'px';svg.setAttribute('viewBox','0 0 20 '+h);
  svg.innerHTML='';wrap.querySelectorAll('.lbl').forEach(e=>e.remove());
  circles=[];labels=[];
  const ln=document.createElementNS('http://www.w3.org/2000/svg','line');
  ln.setAttribute('x1',10);ln.setAttribute('y1',0);
  ln.setAttribute('x2',10);ln.setAttribute('y2',h);
  ln.setAttribute('stroke','#3a3835');ln.setAttribute('stroke-width','1.5');
  svg.appendChild(ln);
  times.forEach((t,i)=>{
    const y=(i/(N-1))*h,isE=i===0||i===N-1;
    const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
    c.setAttribute('cx',10);c.setAttribute('cy',y);c.setAttribute('r',isE?4.5:2.5);
    c.setAttribute('fill','#3a3835');c.style.transition='fill .4s';
    svg.appendChild(c);circles.push({el:c,isE});
    const l=document.createElement('div');
    l.className='lbl';l.textContent=t;l.style.top=(16+y)+'px';l.style.color='#3a3835';
    wrap.appendChild(l);labels.push(l);
  });
  setActive(0);
}
function setActive(idx){
  if(idx===current&&circles.length&&idx!==0)return;current=idx;
  circles.forEach(({el,isE},i)=>{
    if(i===idx){el.setAttribute('fill','#d97941');el.setAttribute('r',isE?5.5:4);}
    else if(i<idx){el.setAttribute('fill','#4a4845');el.setAttribute('r',isE?3.5:2);}
    else{el.setAttribute('fill','#3a3835');el.setAttribute('r',isE?4.5:2.5);}
  });
  labels.forEach((l,i)=>{
    l.style.color=i===idx?'#d97941':i<idx?'#4a4845':'#3a3835';
  });
}
function pollSentinels(){
  try{
    const p=window.parent,center=p.window.innerHeight/2;
    let best=0,bestDist=Infinity;
    for(let i=0;i<N;i++){
      const el=p.document.getElementById('tl-s'+i);if(!el)continue;
      const dist=Math.abs(el.getBoundingClientRect().top-center);
      if(dist<bestDist){bestDist=dist;best=i;}
    }
    setActive(best);
  }catch(e){}
}
setTimeout(draw,300);setTimeout(draw,900);
window.addEventListener('resize',draw);setInterval(pollSentinels,120);
</script></body></html>
""", height=5300, scrolling=False)

# ── Content column ────────────────────────────────────────────────────────────
with col_content:

    # ──────────────────────────────────────────────────────────────────────────
    # BEGINNING
    # ──────────────────────────────────────────────────────────────────────────

    # Beg2 ── TEASER (italic, gray, below header map)
    # ◀ Beg2: replace placeholder with your teaser text
    st.markdown('<p class="teaser">16 minutes that tell the story of a nationwide protest movement and a generation who refused to stay silent.</p>',
                unsafe_allow_html=True)

    # Beg3 ── AUTHOR LINE
    # ◀ Beg3: replace names if needed
    st.markdown('<p class="author-line">Story by Sophie Eder · Laura Lugmair · Sara Comendador</p>',
                unsafe_allow_html=True)
    st.markdown('<div style="margin-bottom:1.2rem;"></div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────────
    # PAST
    # ──────────────────────────────────────────────────────────────────────────

    # PA1 ── First text block  [TIMELINE START]
    sentinel(0)
    # ◀ PA1: replace with your first full-width paragraph
    st.markdown("""
<p class="body-text">“Today it’s been 17 months since the tragedy“, Luka says, his eyes wandering from the desktop screen to the window. “At this moment, people are gathering in front of the railway station to honor the victims by holding 16 minutes of silence.“ One minute for each life lost on November 1, 2024, when a newly renovated railway station canopy in Novi Sad collapsed, burying those beneath it.</p>
""", unsafe_allow_html=True)

    # PA2 ── Text (~80-90 words) left  +  X-Post right
    sentinel(1)
    col_pa2t, col_pa2x = st.columns([1.5, 0.9], gap="large")
    with col_pa2t:
        # ◀ PA2: replace with your text (~80-90 words, ends at the same point as the post)
        # PA3 content can be combined here to fill the column beside the post
        st.markdown("""
<p class="body-text">Thinking back to that day, the 21-year-old student struggles to gather his words. The distinct sound of ambulance sirens is still ingrained in his memory.</p>

<div style="border-left:3px solid #d97941;padding:0.6rem 0 0.6rem 1.2rem;margin:1rem 0;">
  <p style="font-size:1.9rem;font-weight:600;font-style:italic;color:#f0ece6;line-height:1.4;margin:0;">"I remember everyone calling each other.<br>Asking if they are near the station?<br>If they are alive?"</p>
</div>

<p class="body-text">In a different part of the city, another young man struggled to do so. Vuk, a 22-year-old social work student, has a friend who commuted through that station. "I was scared to text her at first. What if she wouldn’t respond?" Across Novi Sad, phones buzzed with similar questions that day. "You feel like it is happening far away, but actually it is so close."</p>
""", unsafe_allow_html=True)
        
    with col_pa2x:
        img_path = os.path.join(BASE, "collapse_picture.jpg")
        img_b64 = file_to_b64(img_path, "image/jpeg")
        if img_b64:
            st.markdown(f"""
<div style="margin-top:0.5rem;">
  <img src="{img_b64}" style="width:62%;border-radius:6px;display:block;">
  <p class="chart-caption" style="margin-top:0.5rem;">The concrete roof that collapsed.</p>
</div>
""", unsafe_allow_html=True)

    # ◀ PA2 new: replace 
    st.markdown("""
<p class="body-text">That evening, people gathered on the Main Square. Some lit candles, others cried together. But beneath the grief, something else was taking hold: fury at the corruption that many believed had made the disaster possible. Fury that would soon lead to a nationwide student-led protest movement. One which Luka and Vuk have been part of from the beginning.</p>
""", unsafe_allow_html=True)

    # PA4 ── Line chart (left, wider)  +  text box (right, narrow)
    sentinel(2)
    # ◀ PA4 chart title: replace placeholder
    st.markdown('<p class="chart-title">Protest Activity in Serbia Per Week, January 2018 until March 2026</p>',
                unsafe_allow_html=True)

    col_pa4c, col_pa4t = st.columns([2.8, 1], gap="small")
    with col_pa4t:
        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        # ◀ PA4b: replace with your sidebar text (~60-70 words)
        st.markdown("""
<div class="ctx-box">
  <p class="ctx-text">In the six years before November 1, 2024, on average nine protest events happened in Serbia every week. Since the collapse until now, data analysis shows a significant increase of 42 more protests per week on average. Identifying only youth-related protests provides insight into the movement: having remained near zero for years, after the tragedy on average 29 more such protests happen per week.</p>
</div>
""", unsafe_allow_html=True)

    with col_pa4c:
        # Line chart: All protests (blue) vs Youth-related (orange)
        # Toggle switches between them; red dashed line marks Nov 2024
        components.html(f"""
<html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d0d0d;font-family:Georgia,serif;color:#e8e4de;padding:4px 0 8px;}}
#tog{{display:flex;align-items:center;gap:10px;margin-bottom:10px;}}
.lbl{{font-size:13px;cursor:pointer;transition:color .3s;user-select:none;}}
.lbl.on{{color:#e8e4de;}}.lbl.off{{color:#2a2a2a;}}
.track{{width:44px;height:22px;background:#cc3333;border-radius:22px;cursor:pointer;position:relative;flex-shrink:0;}}
.thumb{{position:absolute;top:3px;left:3px;width:16px;height:16px;background:#fff;border-radius:50%;transition:transform .25s;pointer-events:none;}}
.track.on .thumb{{transform:translateX(22px);}}
.dot{{width:10px;height:3px;border-radius:2px;display:inline-block;margin-right:4px;}}
#wrap{{height:370px;}}
canvas{{width:100%!important;height:370px!important;}}
#cap{{font-size:13px;color:#8a8580;margin-top:6px;line-height:1.5;font-style:italic;}}
</style></head><body>
<div id="tog">
  <span class="lbl on"><span class="dot" style="background:#4a90d9;vertical-align:middle;"></span>All protests</span>
  <div class="track" id="track" onclick="toggle()"><div class="thumb"></div></div>
  <span class="lbl off"><span class="dot" style="background:#d97941;vertical-align:middle;"></span>Youth-related protests</span>
</div>
<div id="wrap"><canvas id="c"></canvas></div>
<div id="cap">
  <!-- ◀ PA4 caption: replace with your source note -->
  Weekly protest event count, Serbia, January 2018 – March 2026. Youth-related protests identified via keyword-based search (see further information in Methodology). Source: ACLED (Armed Conflict Location & Event Data), accessed 12. April 2026. www.acleddata.com.
</div>
<script>
const D={weekly_json};
const C_ALL='#4a90d9',C_YOUTH='#d97941';
let youth=false;
const labels=D.map(d=>d.w);
const noviIdx=labels.findIndex(l=>l>='2024-11-01');
const ctx=document.getElementById('c').getContext('2d');
const chart=new Chart(ctx,{{
  type:'line',
  data:{{labels,datasets:[
    {{data:D.map(d=>d.a),borderColor:C_ALL,borderWidth:2,pointRadius:0,tension:.3,fill:false}},
    {{data:D.map(d=>d.y),borderColor:'rgba(255,255,255,.05)',borderWidth:1,pointRadius:0,tension:.3,fill:false}}
  ]}},
  options:{{
    animation:{{duration:600,easing:'easeInOutQuart'}},
    responsive:true,maintainAspectRatio:false,
    interaction:{{mode:'index',intersect:false}},
    plugins:{{legend:{{display:false}},tooltip:{{
      backgroundColor:'#1a1a1a',borderColor:'#2a2a2a',borderWidth:1,
      titleColor:'#e8e4de',bodyColor:'#7a7570',
      displayColors:false,
      callbacks:{{
        title:()=>'',
        label:c=>c.datasetIndex===0?c.parsed.y+' protests per week':''
      }}
    }}}},
    scales:{{
      x:{{
  ticks:{{
    color:'#5a5651',font:{{size:11}},maxRotation:0,
    autoSkip:true,
    maxTicksLimit:9,
    callback:(v)=>labels[v]?labels[v].slice(0,4):''
  }},
  grid:{{color:'rgba(255,255,255,.03)'}},border:{{color:'rgba(255,255,255,.05)'}}}},
      y:{{ticks:{{color:'#5a5651',font:{{size:11}}}},grid:{{color:'rgba(255,255,255,.03)'}},
         border:{{color:'rgba(255,255,255,.05)'}},
         title:{{display:true,text:'Protests per week',color:'#5a5651',font:{{size:11}}}}}}
    }}
  }},
  plugins:[{{
    id:'noviLine',
    afterDraw(chart){{
      if(noviIdx<0)return;
      const meta=chart.getDatasetMeta(0);
      if(!meta.data[noviIdx])return;
      const x=meta.data[noviIdx].x;
      const{{top,bottom}}=chart.scales.y;
      const c2=chart.ctx;
      c2.save();
      c2.setLineDash([6,4]);c2.strokeStyle='#cc3333';c2.lineWidth=2;
      c2.beginPath();c2.moveTo(x,top);c2.lineTo(x,bottom);c2.stroke();
      c2.setLineDash([]);
      c2.textAlign='right';c2.font='bold 11px Georgia';c2.fillStyle='#cc3333';
      c2.fillText('Nov 2024 |',x-8,top+14);
      c2.font='10px Georgia';
      c2.fillText('Collapse of a concrete',x-8,top+27);
      c2.fillText('Canopy in Novi Sad',x-8,top+40);
      c2.textAlign='left';c2.restore();
    }}
  }}]
}});
function toggle(){{
  youth=!youth;
  document.getElementById('track').classList.toggle('on',youth);
  const lbls=document.getElementById('tog').querySelectorAll('.lbl');
  if(lbls.length>=2){{lbls[0].className='lbl '+(youth?'off':'on');lbls[1].className='lbl '+(youth?'on':'off');}}
  if(youth){{chart.data.datasets[0].borderColor='rgba(255,255,255,.05)';chart.data.datasets[1].borderColor=C_YOUTH;chart.data.datasets[1].borderWidth=2;}}
  else{{chart.data.datasets[0].borderColor=C_ALL;chart.data.datasets[1].borderColor='rgba(255,255,255,.05)';chart.data.datasets[1].borderWidth=1;}}
  chart.update('active');
}}
</script></body></html>
""", height=450)

    # PA5 ── Text block
    sentinel(3)
    # ◀ PA5: replace with your paragraph
    st.markdown("""
<p class="body-text">“Such protests very often attach themselves to tragic events”, says Dr. Tobias Spöri, a political scientist at the University of Vienna. He describes tragedies like this as a “core trigger” for protest movements, rooted in people being dissatisfied with the political situation. “It is very often students who initiate these processes”, he says. This is what happened in Serbia. What began as grief-driven protests, demanding a thorough investigation into the collapse, quickly grew into a broad movement. Protesters turned their anger towards President Aleksandar Vučić and his ruling Serbian Progressive Party (SNS), blaming large-scale corruption for the catastrophe and accusing the government of restricting democratic freedoms since coming into power in 2012.</p>
""", unsafe_allow_html=True)

    # PA6 ── Expandable "Serbia’s Political System at a Glance"
    # Uses native st.expander → content below shifts dynamically when opened/closed
    sentinel(4)
    with st.expander("Serbia at a Glance"):
        # ◀ PA6: replace with your ~70-word context text (shown on light gray background)
        st.markdown("""
<p class="body-text">Serbia ranks 116th out of 182 countries on the 2024 Global Corruption Index, among the worst in Europe.<br>The V-Dem Institute classifies the country as an electoral autocracy: elections take place, but conditions are neither free nor fair.</p>
""", unsafe_allow_html=True)

    # PA7 ── Text block
    sentinel(5)
    # ◀ PA7: replace with your paragraph
    st.markdown("""
<p class="body-text">What fueled the movement further was the government’s response. From the outset, police used tear gas and made arrests. On November 22, 2024, students at the Faculty of Dramatic Arts in Belgrade were attacked during a 16-minute silent vigil. Later, media reported some of the assailants were connected to the SNS. The university requested a comprehensive investigation. When their demands weren’t met, faculty blockades spread across the country.</p>
""", unsafe_allow_html=True)

    # PA8 ── Text block
    # ◀ PA8: replace with your paragraph
    st.markdown("""
<p class="body-text">“These violent crackdowns against the protesters functioned as a catalyst for citizens to show solidarity with the demonstrators and to join the movement”, says Tobias Spöri. Ognjen, a 25-year-old student in Belgrade, was one of them. "I started protesting shortly after some of our colleagues were attacked," he says, remembering his first demonstration vividly: "There was a lot of youthful energy in the air.” This energy soon spread across the country. “In early 2025 the protests happened in many cities and small towns.”</p>
""", unsafe_allow_html=True)

    # PA9 ── Geographic spread map: Nov 2024 – Mar 2026
    sentinel(6)
    # ◀ PA9 chart title: replace placeholder
    st.markdown('<p class="chart-title">Spread of Protests in Serbia, November 2024 until March 2026</p>',
                unsafe_allow_html=True)
    components.html(f"""
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d0d0d;font-family:Georgia,serif;color:#e8e4de;padding-bottom:.5rem;}}
#map{{width:100%;height:420px;border-radius:3px;}}
#leg{{position:absolute;top:10px;right:10px;z-index:1000;background:rgba(13,13,13,.92);
  border:1px solid #2a2a2a;border-radius:3px;padding:9px 13px;font-size:12px;color:#a09b95;line-height:1.9;pointer-events:none;}}
#info{{position:absolute;bottom:10px;left:10px;z-index:1000;background:rgba(13,13,13,.92);border:1px solid #2a2a2a;border-radius:3px;padding:9px 13px;font-size:12px;color:#f0ece6;
  line-height:1.75;pointer-events:none;max-width:240px;font-family:Georgia,serif;font-style:normal;}}
.li{{display:flex;align-items:center;gap:7px;}}.dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;}}
.leg-note{{font-size:12px;color:#8a8580;margin-top:5px;padding-top:5px;border-top:1px solid #1f1f1f;}}
#ctrl{{display:flex;align-items:center;gap:10px;margin-top:8px;flex-wrap:wrap;}}
#mlbl{{font-size:13px;color:#d97941;min-width:76px;font-style:italic;font-weight:600;}}
#slw{{flex:1;min-width:140px;}}
#msl{{width:100%;accent-color:#d97941;cursor:pointer;height:3px;}}
#playbtn{{background:#1a1a1a;border:1px solid #2a2a2a;color:#e8e4de;font-size:18px;
  width:34px;height:34px;border-radius:50%;cursor:pointer;display:flex;align-items:center;
  justify-content:center;transition:background .2s;flex-shrink:0;}}
#playbtn:hover{{background:#252525;}}
#mrow{{display:flex;align-items:center;gap:8px;}}
.ms{{font-size:14px;font-weight:600;cursor:pointer;transition:color .3s;user-select:none;color:#6a6560;}}
.ms.on{{color:#e8e4de;}}
.track-s{{width:38px;height:18px;background:#cc3333;border-radius:18px;cursor:pointer;position:relative;flex-shrink:0;}}
.thumb-s{{position:absolute;top:2px;left:2px;width:14px;height:14px;background:#fff;border-radius:50%;transition:transform .25s;pointer-events:none;}}
.track-s.on .thumb-s{{transform:translateX(20px);}}
.mhint{{font-size:10px;color:#4a4845;font-style:italic;}}
#cap{{font-size:13px;color:#8a8580;margin-top:6px;line-height:1.6;font-style:italic;}}
.leaflet-tile-pane{{filter:grayscale(1) brightness(.85) contrast(1.1);}}
.leaflet-control-attribution{{display:none;}}
.leaflet-control-zoom a{{background:#1a1a1a !important;color:#888 !important;border-color:#2a2a2a !important;}}
.leaflet-tooltip{{background:#111;border:1px solid #2a2a2a;color:#e8e4de;font-size:11px;padding:3px 8px;border-radius:2px;box-shadow:none;}}
#mwrap{{position:relative;}}
</style></head><body>
<div id="mwrap">
  <div id="map"></div>
  <div id="leg">
    <div class="li"><div class="dot" style="background:#d97941;"></div><span>Youth-related protests</span></div>
    <div class="li"><div class="dot" style="background:#4a90d9;"></div><span>All other protests</span></div>
    <div class="leg-note">1 dot = 1 protest event · ACLED 2026</div>
  </div>
  <div id="info">
  Ognjen's statement is backed by data:<br>The increase in protests did not remain local to Novi Sad only, statistical analysis finds.
  <br><br>Use the slider to move through time. Toggle to change between "monthly" and "cumulative" view.
</div>
</div>
<div id="ctrl">
  <button id="playbtn" onclick="togglePlay()">&#9654;</button>
  <div id="mlbl">Nov 2024</div>
  <div id="slw"><input type="range" id="msl" min="0" max="{n_months-1}" value="0" step="1"></div>
  <div id="mrow">
    <span class="ms on" id="lbl-m">Monthly</span>
    <div class="track-s" id="track-m" onclick="toggleMode()"><div class="thumb-s"></div></div>
    <span class="ms" id="lbl-c">Cumulative</span>
    <span class="mhint" id="mhint">— showing this month only</span>
  </div>
</div>
<div id="cap">
  <!-- ◀ PA9 caption: describe what the map shows and add data source -->
  Spread of protest events in Serbia from November 2024 - March 2026. "Monthly" (events that month only) and "cumulative" (all events up to that month). Source: ACLED, accessed 12. April 2026. www.acleddata.com Youth-related protests identified with keywords.
</div>
<script>
const M={map_json};const MONTHS={months_json};
const map=L.map('map',{{center:[44.2,21.0],zoom:7,zoomControl:true,scrollWheelZoom:false}});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{subdomains:'abcd',maxZoom:12}}).addTo(map);
const layer=L.layerGroup().addTo(map);
let mode='monthly',cur=0,playing=false,timer=null;
function fmt(s){{const[y,mo]=s.split('-');return['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][parseInt(mo)-1]+' '+y;}}
function render(idx){{
  layer.clearLayers();let pts=[];
  if(mode==='cumulative')for(let i=0;i<=idx;i++)pts=pts.concat(M[MONTHS[i]]||[]);
  else pts=M[MONTHS[idx]]||[];
  pts.forEach(p=>{{const c=p.s?'#d97941':'#4a90d9';
    L.circleMarker([p.la,p.lo],{{radius:p.s?4:3,color:c,weight:0,fillColor:c,fillOpacity:.7}})
     .bindTooltip(p.n,{{permanent:false,direction:'top'}}).addTo(layer);}});
  document.getElementById('mlbl').textContent=fmt(MONTHS[idx]);
  document.getElementById('msl').value=idx;
}}
function toggleMode(){{
  const isCumul=mode==='cumulative';mode=isCumul?'monthly':'cumulative';
  document.getElementById('track-m').classList.toggle('on',!isCumul);
  document.getElementById('lbl-m').className='ms'+(mode==='monthly'?' on':'');
  document.getElementById('lbl-c').className='ms'+(mode==='cumulative'?' on':'');
  document.getElementById('mhint').textContent=mode==='cumulative'?'— all events up to this month':'— showing this month only';
  render(cur);
}}
function togglePlay(){{
  playing=!playing;const btn=document.getElementById('playbtn');
  if(playing){{btn.innerHTML='&#9646;&#9646;';if(cur>=MONTHS.length-1)cur=0;
    timer=setInterval(()=>{{cur++;render(cur);if(cur>=MONTHS.length-1){{playing=false;clearInterval(timer);btn.innerHTML='&#9654;';}}}},700);
  }}else{{clearInterval(timer);btn.innerHTML='&#9654;';}}
}}
document.getElementById('msl').addEventListener('input',e=>{{cur=parseInt(e.target.value);render(cur);}});
const obs=new IntersectionObserver(e=>{{if(e[0].isIntersecting&&!playing&&cur===0)togglePlay();}},{{threshold:.5}});
obs.observe(document.getElementById('map'));
render(0);
</script></body></html>
""", height=560, scrolling=False)

    # PA10a ── Text block
    sentinel(7)
    # ◀ PA10a: replace with your paragraph
    # st.markdown("""
# <p class="body-text">This broad public support sustained the movement through a winter and spring of massive demonstrations, with several protests spanning widely over 100,000 people. On March 15, 2025, the independent NGO Arhiv javnih skupova estimated over 300,000 people taking the streets of Belgrade, with the government reporting a count of 107,000. That day, the government was accused of deploying a sonic weapon against protesters by rights groups and opposition. They ultimately denied it.</p>
# """, unsafe_allow_html=True)

    # PA10b ── X-Post right  +  text left (~22 words, PA11 combined)
    sentinel(8)
    col_pa10t, col_pa10x = st.columns([1.5, 0.7], gap="large")
    with col_pa10x:
        # X-Post: https://twitter.com/visegrad24/status/1902376760555065655
        components.html("""
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0d0d0d;overflow:hidden;">
<blockquote class="twitter-tweet" data-theme="dark" data-width="280" data-dnt="true">
  <a href="https://twitter.com/visegrad24/status/1902376760555065655"></a>
</blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
</body></html>
""", height=600, scrolling=False)
    with col_pa10t:
        # ◀ PA10b + PA11: replace with your text (right column, ~22 + additional words)
        st.markdown("""
<p class="body-text">This broad public support sustained the movement through months of massive demonstrations, with several protests spanning widely over 100,000 people. On March 15, 2025, the independent NGO Arhiv javnih skupova estimated over 300,000 people taking the streets of Belgrade. That day, the government was accused of deploying a sonic weapon against protesters by rights groups and opposition. They denied it.</p>
<p class="body-text">By this point, the movement had already forced some institutional cracks: Prime Minister Miloš Vučević as well as Milan Đurić, Novi Sad’s mayor, had resigned, and the first indictments for criminal liability in connection to the canopy collapse had been filed. However, for Ognjen, these concessions felt like "cosmetic arrests" and masks.</p>

<div style="border-left:3px solid #d97941;padding:0.6rem 0 0.6rem 1.2rem;margin:1rem 0;">
  <p style="font-size:1.9rem;font-weight:600;font-style:italic;color:#f0ece6;line-height:1.4;margin:0;">"They don’t have<br>any interest in actually<br>doing their job"</p>
</div>

<p class="body-text">he says. The movement’s demands — publication of all documentation related to the station reconstruction, identification of those who attacked students, dismissal of all legal proceedings against protesters and a 20 percent increase in state funding for public universities — remained unmet.</p>
""", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────────
    # PRESENT
    # ──────────────────────────────────────────────────────────────────────────

    # PRE1 ── Section heading
    sentinel(9)
    # ◀ PRE1: replace with your section heading
    st.markdown('<h2 class="section-title">What now?</h2>',
                unsafe_allow_html=True)

    # PRE2 ── Text block
    # ◀ PRE2: replace with your paragraph
    st.markdown("""
<p class="body-text">In the summer of 2025 the movement entered a new stage, the strategy shifted toward political involvement.  A student list of non-partisan candidates, many drawn from academia, wants to challenge the regime directly in the electoral arena. Tobias Spöri sees this as a logical evolution for a movement to maintain its momentum. He notes that while re-democratizing a country like Serbia is a "very large hurdle", the emergence of a new force that distances itself from the "old opposition" brings vital "fresh air" to the system.</p>
""", unsafe_allow_html=True)

    # PRE3 ── Pull quote
    sentinel(10)
    # ◀ PRE3: replace quote text (~20 words) and attribution
    st.markdown("""
<div class="quote-box">
  <div class="quote-text">"Last year was a year of protesting, and this year will be hopefully the year of elections."</div>
  <div class="quote-attr">— Vuk, 22-year-old student from Novi Sad</div>
</div>
""", unsafe_allow_html=True)

    # PRE4 ── Bar chart: youth protests only, Mar 2025 – Mar 2026
    # ◀ PRE4 chart title: replace placeholder
    st.markdown('<p class="chart-title">Development of Youth-related Protest Activity, March 2025 until March 2026</p>',
                unsafe_allow_html=True)
    components.html(f"""
<html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d0d0d;font-family:Georgia,serif;color:#e8e4de;padding:4px 0 6px;}}
#wrap{{height:300px;}}canvas{{width:100%!important;height:300px!important;}}
#cap{{font-size:13px;color:#8a8580;margin-top:5px;line-height:1.5;font-style:italic;}}
</style></head><body>
<div id="wrap"><canvas id="c"></canvas></div>
<div id="cap">
  <!-- ◀ PRE4 caption: replace with your chart description and source note -->
  Monthly count of youth-related protest events in Serbia, March 2025 – March 2026. Youth-related protests identified via keywords in ACLED event notes. Source: ACLED, accessed 12. April 2026. www.acleddata.com.
</div>
<script>
const BD={bar_json};let built=false;
const ctx=document.getElementById('c').getContext('2d');
function buildChart(){{
  if(built)return;built=true;
  new Chart(ctx,{{
    type:'bar',
    data:{{labels:BD.map(d=>d.m),datasets:[{{
      data:BD.map(d=>d.y),backgroundColor:'rgba(217,121,65,.75)',
      hoverBackgroundColor:'rgba(217,121,65,1)',borderRadius:2,borderSkipped:false
    }}]}},
    options:{{
      animation:{{duration:900,easing:'easeOutQuart',delay:ctx=>ctx.dataIndex*60}},
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},tooltip:{{
        backgroundColor:'#1a1a1a',borderColor:'#2a2a2a',borderWidth:1,
        titleColor:'#e8e4de',bodyColor:'#7a7570',
        callbacks:{{label:c=>c.parsed.y+' youth protests'}}
      }}}},
      scales:{{
        x:{{ticks:{{color:'#5a5651',font:{{size:11}}}},grid:{{display:false}},border:{{color:'rgba(255,255,255,.05)'}}}},
        y:{{ticks:{{color:'#5a5651',font:{{size:11}}}},grid:{{color:'rgba(255,255,255,.03)'}},
           border:{{color:'rgba(255,255,255,.05)'}},
           title:{{display:true,text:'Youth protests per month',color:'#5a5651',font:{{size:11}}}}}}
      }}
    }}
  }});
}}
const obs=new IntersectionObserver(e=>{{if(e[0].isIntersecting)buildChart();}},{{threshold:.4}});
obs.observe(document.getElementById('wrap'));
</script></body></html>
""", height=350)

    # PRE5 ── Text block
    sentinel(11)
    # ◀ PRE5: replace with your paragraph
    st.markdown("""
<p class="body-text">Today, students are working more focused than ever, though the movement’s presence on the streets has quieted. The focus has shifted to preparing for elections. While the data shows fewer youth-related gatherings, Ognjen explains that they are working very hard behind the scenes to field a united opposition in the upcoming national elections, which Vučić has loosely scheduled for late 2026.</p>
""", unsafe_allow_html=True)

    # PRE6 ── Text (~80 words, left)  +  Election map (right)
    col_pre6t, col_pre6m = st.columns([0.6, 1.4], gap="large")
    with col_pre6t:
        # ◀ PRE6a: replace with your text (~80 words)
        st.markdown("""
<p class="body-text">The impact of this political shift was tested in March 2026 during local elections in ten towns, where the student list was on the ballot. Vučić recalled his victory over all ten of them, but in some only winning with a slight lead in votes. In a political system that has long been marked by easy and predictable wins for the ruling party, these results are striking. "This regime is not unbeatable anymore," says Luka.</p>
""", unsafe_allow_html=True)
    with col_pre6m:
        # PRE6b: 10 municipalities — hover/click shows election results
        components.html(f"""
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}body{{background:#0d0d0d;font-family:Georgia,serif;}}
#map{{width:100%;height:270px;border-radius:3px;}}
#cap{{font-size:13px;color:#8a8580;margin-top:6px;line-height:1.5;font-style:italic;}}
.leaflet-tile-pane{{filter:grayscale(1) brightness(.85) contrast(1.1);}}
.leaflet-control-attribution{{display:none;}}
.leaflet-control-zoom a{{background:#1a1a1a !important;color:#888 !important;border-color:#2a2a2a !important;}}
.leaflet-popup-content-wrapper{{background:#111;border:1px solid #333;border-radius:3px;box-shadow:none;color:#e8e4de;}}
.leaflet-popup-tip{{background:#111;}}
.leaflet-popup-content{{margin:10px 14px;min-width:170px;font-family:Georgia,serif;}}
.leaflet-popup-close-button{{color:#888 !important;}}
.sns{{color:#cc3333;font-size:12px;}}.stud{{color:#4a90d9;font-size:12px;}}
</style></head><body>
<div id="map"></div>
<div id="cap">
  <!-- ◀ PRE6b caption: describe what the map shows and add source -->
  Ten municipalities in Serbia where local elections were held in March 2026. Click markers to see results. Source: serbianmonitor.com.
</div>
<script>
const LOCS={election_json};
const map=L.map('map',{{center:[44.2,21.0],zoom:7,zoomControl:true,scrollWheelZoom:false}});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png',{{subdomains:'abcd',maxZoom:14}}).addTo(map);
LOCS.forEach(l=>{{
  L.circleMarker([l.la,l.lo],{{radius:14,color:'#cc3333',weight:1.5,fillColor:'#cc3333',fillOpacity:.18}}).addTo(map);
  L.circleMarker([l.la,l.lo],{{radius:5,color:'#cc3333',weight:0,fillColor:'#cc3333',fillOpacity:1}})
   .bindPopup(`<b style="font-size:13px;">${{l.n}}</b><br><span class="sns">SNS: ${{l.sns}}</span><br><span class="stud">Student list: ${{l.stud}}</span>`,{{maxWidth:200}})
   .addTo(map);
}});
</script></body></html>
""", height=320)

    # PRE7, PRE8, PRE9 ── Text blocks
    sentinel(12)
    # ◀ PRE7: replace with your paragraph
    st.markdown("""<p class="body-text">The regime’s reaction to this rising competition has been one of peak repression. Protesters point to a "systemic violence" that has become the rule. Amnesty International reports that “Serbian riot police” has been targeting “peaceful protesters”, with “widespread arrests”. Despite seeing how far the regime is willing to go, the endurance of the students remains. Vuk describes the current atmosphere as the "last part of the marathon".</p>""", unsafe_allow_html=True)
    # ◀ PRE8: replace with your paragraph
    # st.markdown("""<p class="body-text">Despite seeing how far the regime is willing to go, the endurance of the students remains. Vuk describes the current atmosphere as the "last part of the marathon". "We are all just still working hard every single day, every single night", Ognjen insists, emphasizing that much of their most important work is currently "not visible" to the public.</p>""", unsafe_allow_html=True)
    # ◀ PRE9: replace with your paragraph
    # st.markdown("""<p class="body-text">At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.</p>""", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────────
    # FUTURE
    # ──────────────────────────────────────────────────────────────────────────
    sentinel(13)
    # FUT1 ── Section heading
    # ◀ FUT1: replace placeholder heading
    st.markdown('<h2 class="section-title">Serbia\'s future is uncertain.</h2>', unsafe_allow_html=True)
    st.markdown("""<p class="body-text">What are Luka, Vuk and Ognjen working towards?</p>""", unsafe_allow_html=True)
    # FUT2 ── Three voice memos (Luka, Vuk, Ognjen)
    # Files: LUKA.mp3, VUK.mp3, OGNJEN.mp3 in project root
    # Auto-plays Luka → Vuk → Ognjen on scroll into view
    sentinel(14)
    luka_src   = audio_luka   or ""
    vuk_src    = audio_vuk    or ""
    ognjen_src = audio_ognjen or ""
    components.html(f"""
<html><head><meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#0d0d0d;font-family:Georgia,serif;color:#e8e4de;padding:0;}}
#cards{{display:flex;gap:12px;}}
.card{{flex:1;min-width:160px;background:#111;border:1px solid #2a2a2a;border-radius:4px;
  padding:14px 14px 12px;display:flex;flex-direction:column;align-items:center;gap:8px;transition:border-color .3s;}}
.card.playing{{border-color:#d97941;}}
.card-name{{font-size:1rem;font-weight:600;color:#f0ece6;letter-spacing:.02em;text-align:center;}}
.waveform{{display:flex;align-items:center;gap:3px;height:24px;}}
.bar{{width:3px;border-radius:2px;background:#3a3835;transition:background .3s;transform-origin:bottom;}}
.card.playing .bar{{background:#d97941;animation:wave .8s ease-in-out infinite;}}
.bar:nth-child(1){{animation-delay:0s;height:6px;}}.bar:nth-child(2){{animation-delay:.1s;height:12px;}}
.bar:nth-child(3){{animation-delay:.2s;height:18px;}}.bar:nth-child(4){{animation-delay:.3s;height:14px;}}
.bar:nth-child(5){{animation-delay:.4s;height:8px;}}.bar:nth-child(6){{animation-delay:.5s;height:20px;}}
.bar:nth-child(7){{animation-delay:.15s;height:10px;}}.bar:nth-child(8){{animation-delay:.25s;height:6px;}}
@keyframes wave{{0%,100%{{transform:scaleY(.4);}}50%{{transform:scaleY(1);}}}}
.card:not(.playing) .bar{{animation:none !important;height:6px !important;}}
.play-btn{{width:36px;height:36px;border-radius:50%;background:#1a1a1a;border:1px solid #3a3835;
  color:#e8e4de;font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;}}
.card.playing .play-btn{{background:#d97941;border-color:#d97941;color:#fff;}}
.no-file{{font-size:10px;color:#4a4845;font-style:italic;text-align:center;}}
audio{{width:0;height:0;opacity:0;position:absolute;}}
#cap{{font-size:13px;color:#8a8580;margin-top:7px;line-height:1.5;font-style:italic;}}
</style></head><body>
<div id="cards">
  <div class="card" id="c0">
    <div class="card-name">Luka</div>
    <div class="waveform"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div>
    <button class="play-btn" onclick="tog(0)">&#9654;</button>
    <audio id="a0" {'src="'+luka_src+'"' if luka_src else ''}></audio>
    {'<div class="no-file">LUKA.mp3 not found</div>' if not luka_src else ''}
  </div>
  <div class="card" id="c1">
    <div class="card-name">Vuk</div>
    <div class="waveform"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div>
    <button class="play-btn" onclick="tog(1)">&#9654;</button>
    <audio id="a1" {'src="'+vuk_src+'"' if vuk_src else ''}></audio>
    {'<div class="no-file">VUK.mp3 not found</div>' if not vuk_src else ''}
  </div>
  <div class="card" id="c2">
    <div class="card-name">Ognjen</div>
    <div class="waveform"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div>
    <button class="play-btn" onclick="tog(2)">&#9654;</button>
    <audio id="a2" {'src="'+ognjen_src+'"' if ognjen_src else ''}></audio>
    {'<div class="no-file">OGNJEN.mp3 not found</div>' if not ognjen_src else ''}
  </div>
</div>
<div id="cap">
  <!-- ◀ FUT2 caption: source note for the voice memos (AI-generated, date, context) -->
  Quotes original, voice notes AI-generated.
</div>
<script>
const audios=[0,1,2].map(i=>document.getElementById('a'+i));
const cards=[0,1,2].map(i=>document.getElementById('c'+i));
const btns=cards.map(c=>c.querySelector('.play-btn'));
let cur=-1,started=false;
function setP(i,p){{cards[i].classList.toggle('playing',p);btns[i].innerHTML=p?'&#9646;&#9646;':'&#9654;';}}
function stopAll(){{audios.forEach((a,i)=>{{a.pause();a.currentTime=0;setP(i,false);}});cur=-1;}}
function play(i){{if(!audios[i].src)return;stopAll();cur=i;audios[i].play().catch(()=>{{}});setP(i,true);}}
function tog(i){{if(cur===i&&!audios[i].paused){{audios[i].pause();setP(i,false);cur=-1;}}else play(i);}}
audios.forEach((a,i)=>{{a.addEventListener('ended',()=>{{setP(i,false);cur=-1;if(i<2)play(i+1);}});}});
const obs=new IntersectionObserver(e=>{{if(e[0].isIntersecting&&!started){{started=true;setTimeout(()=>play(0),400);}}}},{{threshold:.5}});
obs.observe(cards[0]);
</script></body></html>
""", height=147)

    # FUT3 ── Final text block  [TIMELINE END at first sentence]
    sentinel(15)
    sentinel(16)  # 12:08 fires at start of this paragraph
    # ◀ FUT3: replace with your last paragraph (more graphics can be added before this)
    st.markdown("""
<p class="body-text">Winning elections might not be enough though. Political scientist Tobias Spöri points to Poland, where eight years of democratic backsliding left institutions so entrenched that re-democratisation has proven difficult even after the government changed. In Serbia, that entrenchment runs deeper: the presidency has steadily absorbed competencies from other institutions, and Vučić, Spöri notes, who would "very probably face legal proceedings due to corruption" if voted out, has every reason to fight.</p>
""", unsafe_allow_html=True)
    st.markdown("""
<p class="body-text">The EU has been an ambiguous actor. Spöri notes that Brussels for years prioritised Serbian stability over democratic progress, finding Vučić's balancing act between Russia, China and the West convenient enough. Meanwhile, thousands continue to leave Serbia. Spöri cautions that many are "voting with their feet rather than going to the polls." Every person who leaves is one fewer voice at the ballot box. For those who stay, the stakes feel existential and the generation that learned politics in a blockaded faculty will not quietly return to passive citizenship. “It’s fight or leave, literally, for my generation”, says Luka.</p>
""", unsafe_allow_html=True)
    st.markdown("""
<p class="body-text">Every first of the month at 12:08 p.m., people leave Novi Sad’s railway station after standing for 16 minutes in silence. They move on with their lives without forgetting those who aren’t there anymore. Luka often walks past the station. "That building was shining every day," he says. "You could see it from the other half of the city. And nowadays it's not shining anymore. It's dark." He pauses. "So basically, we need to change."</p>
""", unsafe_allow_html=True)
    # ──────────────────────────────────────────────────────────────────────────
    # ENDING
    # ──────────────────────────────────────────────────────────────────────────

    # END1 ── Decorative divider (same style as before authors)
    st.markdown('<hr class="sec-divider" style="margin-top:1.5rem;">', unsafe_allow_html=True)

    # END2 ── Sources  |  Methodology  (independent expandables, side by side)
    col_src, col_met = st.columns(2, gap="small")
    with col_src:
        with st.expander("Sources"):
            # ◀ END2 Sources: replace with your actual sources
            st.markdown("""
<p class="body-text">Data source:<br> 
ACLED (Armed Conflict Location & Event Data), accessed 12. April 2026. www.acleddata.com
</p>
<p class="body-text">Visual sources:<br>
Mishyac. (2024, November 1). Novi Sad railway station canopy collapse [Photograph]. Wikimedia Commons. https://commons.wikimedia.org/wiki/File:Novi_Sad_railway_station_canopy_collapse.jpg<br>
Visegrád 24. (2025, March 18). Picture showing the scale of Saturday's student protest in Belgrade which gathered more than half a million people demanding the… [Post]. X. https://x.com/visegrad24/status/1902376760555065655
</p>
<p class="body-text">Audio sources:<br>
ElevenLabs. (2026). ElevenLabs voice AI [Software]. https://elevenlabs.io: The three voice notes on the website are AI-generated reproductions created using ElevenLabs based on real interviews; in order to protect our sources, we didn’t include their original voices.
</p>
<p class="body-text">Dialogue sources:<br> 
Luka (2026, April). Personal interview conducted by Sophie Eder.<br>
Ognjen (2026, April). Personal interview conducted by Sophie Eder.<br>
Vuk (2026, April). Personal interview conducted by Sophie Eder.<br>
Dr. Tobias Spöri (2025, April). Personal interview conducted by Sophie Eder and Laura Lugmair.
<p class="body-text">Non-dialogue sources:<br>
Al Jazeera. (2024, November 6). Police fire tear gas at Serbians protesting deadly station roof collapse. Al Jazeera. https://www.aljazeera.com/news/2024/11/6/police-fire-tear-gas-at-serbians-protesting-deadly-station-roof-collapse<br>
BBC News. (2025, March 15). Serbia's largest-ever rally sees 325,000 protest against government. BBC News. https://www.bbc.com/news/articles/cx2g8v32q30o<br>
Amnesty International. (2025, July 4). Serbia: Authorities must end unlawful use of force against protesters and investigate reports of police violence. https://www.amnesty.org/en/latest/news/2025/07/serbia-authorities-must-end-unlawful-use-of-force-against-protesters-and-investigate-reports-of-police-violence/<br>
Danas. (2024, December 11). Funkcioner SNS-a i "slučajni prolaznik": Ko je Milija Koldžić, član opštinskog veća koji "ništa nije kriv"? [SNS official and "accidental bystander": Who is Milija Koldžić, the municipal council member who "did nothing wrong"?]. Danas. https://www.danas.rs/vesti/politika/milija-koldzic-biografija/<br>
Deutsche Welle. (2025, March 15). Serbia: Protesters flood Belgrade with Vucic under pressure. DW. https://www.dw.com/en/serbia-protesters-flood-belgrade-with-vucic-under-pressure/a-71933147<br>
European Western Balkans. (2025, September 5). Vučić's distortion of facts to help save a tarnished international reputation. European Western Balkans. https://europeanwesternbalkans.com/2025/09/05/vucics-distortion-of-facts-to-help-save-a-tarnished-international-reputation/<br>
Icoski, M. (2022, October 19). Reversing the brain drain in the Western Balkans. German Marshall Fund of the United States. https://www.gmfus.org/news/reversing-brain-drain-western-balkans<br>
Luhrmann, A., Maerz, S. F., Grahn, S., Alizada, N., Gastaldi, L., Hellmeier, S., Hindle, G., & Lindberg, S. I. (2025). Democracy report 2025: Autocratization turns viral. University of Gothenburg, V-Dem Institute. https://www.v-dem.net/publications/democracy-reports/<br>
Raleigh, C., Kishi, R., & Linke, A. (2023). Political instability patterns are obscured by conflict dataset scope conditions, sources, and coding choices. Humanities and Social Sciences Communications. https://doi.org/10.1057/s41599-023-01559-4<br>
Rakić, S. (2026, March 30). Vučić declares victory in all municipalities: Election day marked by clashes and allegations of vote-buying. N1, Radio Free Europe. https://www.serbianmonitor.com/en/vucic-declares-victory-in-all-municipalities-election-day-marked-by-clashes-and-allegations-of-vote-buying/<br> 
Stojanović, M. (2025, January 28). Serbia's prime minister resigns as mass protests rock country. Balkan Insight. https://balkaninsight.com/2025/01/28/serbias-prime-minister-resigns-as-mass-protests-rock-country/bi/<br>
Transparency International. (2025). Corruption Perceptions Index 2025. https://www.transparency.org/en/cpi/2025<br> 
Vreme. (2025, January 28). Gradonačelnik Novog Sada Milan Đurić podneo ostavku [Mayor of Novi Sad Milan Đurić resigns]. Vreme. https://vreme.com/en/vesti/gradonacelnik-novog-sada-milan-djuric-podnosi-ostavku/
</p>
""", unsafe_allow_html=True)
    with col_met:
        with st.expander("Methodology"):
            # ◀ END2 Methodology: replace with your methodology description
            st.markdown("""
<p class="body-text">Data Processing:<br>
We scaled the ACLED dataset (see in “Sources”) down to protest events in Serbia from January 2018 to March 2026. Further, we identified youth-related protest events in the dataset with keyword-based search. ACLED advises this data processing approach when aiming for additional details of events that are not captured in other variables. This was the case, as ACLED does not consistently cover demographics of actors. However, the dataset provides these details in the event notes. The applied keywords for including data points as youth-related are “student, students, student-led, university, fakultet, faculty, youth, young, young people”, the key-phrase "oppose student-led protests" was added to exclude unwanted data points.
</p>
<p class="body-text">Applied Statistical Analysis:<br>
We employed a simple Interrupted Time Series design to analyse the protests statistically. This method allows us to compare average level changes before/after an event of a measure collected repeatedly over time. Our dependent variable is weekly protest count (total/youth-related) from January 2018 until March 2026. Our independent (treatment) variable is a binary indicator for the before/after weeks after 1 November 2024. We added weekly protest counts in Novi Sad as a control variable. This helped isolate whether the increase in protests extends beyond Novi Sad.
</p>
""", unsafe_allow_html=True)
    st.markdown('<hr class="sec-divider" style="margin-top:1.5rem;">', unsafe_allow_html=True)