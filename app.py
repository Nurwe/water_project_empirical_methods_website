from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pycountry
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Water Scarcity and Growth", page_icon="💧", layout="wide")

# Page styling (fonts, header banner, tabs, cards) lives in style.css
st.markdown(f"<style>{(Path(__file__).parent / 'style.css').read_text()}</style>", unsafe_allow_html=True)

REPO_URL = "https://github.com/Nurwe/water_project_empirical_methods_website"
SITE_URL = "https://water-project-empirical-methods.streamlit.app/"
PAPER_URL = "https://www.bis.org/publications/working-paper-1314-economics-water-scarcity"

# Chart style shared by all Plotly figures
FONT = "Inter, system-ui, sans-serif"
NAVY = "#0b2545"

# Demo variables: colour scale, unit (colour-bar title), what low/high values mean,
# and a one-line definition shown under the map. Replace with the real data later.
DEMO_VARIABLES = {
    "Water scarcity (demo)": dict(
        scale="OrRd", unit="% of renewable<br>water withdrawn",
        low="no stress", high="all renewable water used",
        definition="Water withdrawals as a share of the country's renewable freshwater "
                   "resources. 0 = no water used, 100 = withdrawals equal all renewable water."),
    "GDP growth (demo)": dict(
        scale="RdBu", unit="% per year",
        low="shrinking", high="growing",
        definition="Annual growth of real GDP per capita, in percent."),
    "Rainfall anomaly (demo)": dict(
        scale="BrBG", unit="SD from<br>1961–90 normal",
        low="drier than normal", high="wetter than normal",
        definition="Rainfall in the year compared with the country's 1961–90 average, in "
                   "standard deviations. 0 = a normal year, −1 or lower = drought."),
}


@st.cache_data
def demo_panel():
    """Random country-year panel, only to try out the layout."""
    countries = px.data.gapminder()[["country", "iso_alpha"]].drop_duplicates()
    rng = np.random.default_rng(0)
    rows = []
    for _, c in countries.iterrows():
        base_ws = rng.uniform(0, 100)
        for year in range(1990, 2021):
            rows.append({
                "country": c["country"],
                "iso3": c["iso_alpha"],
                "year": year,
                "Water scarcity (demo)": np.clip(base_ws + rng.normal(0, 3), 0, 100),
                "GDP growth (demo)": rng.normal(2, 3),
                "Rainfall anomaly (demo)": rng.normal(0, 1),
            })
    return pd.DataFrame(rows)


@st.cache_data
def world_countries():
    """All countries (ISO3 code -> short name), to show 'No data' on the map."""
    return {c.alpha_3: getattr(c, "common_name", c.name) for c in pycountry.countries}


def no_data_layer(df, variable):
    """Grey map layer for countries without a value: hover shows the name and 'No data'."""
    have = set(df.loc[df[variable].notna(), "iso3"])
    missing = {k: v for k, v in world_countries().items() if k not in have}
    return go.Choropleth(
        locations=list(missing), z=[0] * len(missing), text=list(missing.values()),
        colorscale=[[0, "#e3e8ed"], [1, "#e3e8ed"]], showscale=False,
        marker_line_color="#ffffff", marker_line_width=0.4,
        hovertemplate="<b>%{text}</b><br>No data<extra></extra>",
    )


def section(eyebrow, title, lead=None):
    """Small coloured label, heading and optional intro line."""
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.header(title)
    if lead:
        st.markdown(f'<p class="lead">{lead}</p>', unsafe_allow_html=True)


def placeholder(text):
    st.markdown(f'<p class="placeholder">{text}</p>', unsafe_allow_html=True)


# "Copy link" button, drawn on top of the banner's top-right corner (see .st-key-share in style.css)
with st.container(key="share"):
    components.html(
        f"""
        <button id="b" onclick="copy()">🔗 Copy link</button>
        <script>
          function copy() {{
            const url = "{SITE_URL}", b = document.getElementById("b");
            const done = () => {{ b.textContent = "✓ Link copied"; setTimeout(() => b.textContent = "🔗 Copy link", 2000); }};
            // Fallback for browsers/iframes that block the clipboard API
            const old = () => {{ const t = document.createElement("textarea"); t.value = url;
              document.body.appendChild(t); t.select(); document.execCommand("copy"); t.remove(); done(); }};
            navigator.clipboard ? navigator.clipboard.writeText(url).then(done, old) : old();
          }}
        </script>
        <style>
          body {{ margin: 0; display: flex; justify-content: flex-end; background: transparent; }}
          button {{ font: 500 13px Inter, system-ui, sans-serif; color: #fff; cursor: pointer;
                    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.35);
                    border-radius: 999px; padding: 6px 14px; }}
          button:hover {{ background: rgba(255,255,255,0.22); }}
        </style>
        """,
        height=36,
    )

# --- Header banner ---
st.markdown(
    f"""
    <div class="hero">
      <div class="kicker">Empirical Methods · UZH · Fall 2026</div>
      <h1>Water Scarcity and Economic Growth</h1>
      <p class="sub">A replication and extension: does water scarcity slow down growth,
      and what do weather shocks tell us about it?</p>
      <div class="paper">
        <span class="label">Paper</span>
        <a href="{PAPER_URL}" target="_blank" rel="noopener"><i>The economics of water scarcity</i> ↗</a>
        · Jon Frost, Carlos Madeira and
        Serafín Martínez Jaramillo · BIS Working Papers No 1314, December 2025
      </div>
      <div class="summary"><b>In short:</b> placeholder for the summary – research question,
      method and main findings in three or four sentences.</div>
      <svg class="wave" viewBox="0 0 1200 46" preserveAspectRatio="none">
        <path d="M0,24 C200,46 400,2 600,22 C800,42 1000,6 1200,24 L1200,46 L0,46 Z"
              fill="#ffffff"/>
      </svg>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_paper, tab_data, tab_results, tab_questions = st.tabs(
    ["The Paper", "Explore the Data", "Results", "Questions"]
)

# --- Tab 1: the paper's discussion and main arguments ---
with tab_paper:
    col_text, col_facts = st.columns([2, 1], gap="large")
    with col_text:
        section("Background", "What is the paper about?")
        placeholder("Research question, motivation and context.")

        section("Approach", "Method")
        placeholder("Data, specification and identifying assumptions.")

        section("Argument", "Main arguments")
        placeholder("The paper's key arguments.")

    with col_facts:
        with st.container(border=True):
            st.markdown("**At a glance**")
            st.metric("Countries", "—")
            st.metric("Years", "—")
            st.metric("Observations", "—")

# --- Tab 2: interactive data exploration ---
with tab_data:
    section("Interactive", "World map",
            "Pick a variable and press play to see how it changes over time. "
            "Hover over a country to see its values.")
    st.markdown('<span class="pill">Demo data – random numbers, not real results</span>',
                unsafe_allow_html=True)

    demo = demo_panel()
    variable = st.selectbox("Variable", list(DEMO_VARIABLES))

    info = DEMO_VARIABLES[variable]
    # Colour range fixed over all years so changes over time are visible.
    lo, hi = demo[variable].min(), demo[variable].max()
    if info["scale"] in ("RdBu", "BrBG"):  # diverging: centre the colours on 0
        lo, hi = -max(abs(lo), abs(hi)), max(abs(lo), abs(hi))
    # Colour-bar ticks: numbers in between, meaning written at both ends
    ticks = np.linspace(lo, hi, 5)
    tick_text = [f"{t:.0f}" if abs(hi) >= 10 else f"{t:.1f}" for t in ticks]
    tick_text[0] += f" · {info['low']}"
    tick_text[-1] += f" · {info['high']}"

    # Animated map: play button + year slider under the map.
    fig = px.choropleth(
        demo.sort_values("year"),
        locations="iso3",
        color=variable,
        animation_frame="year",
        hover_name="country",
        hover_data={"iso3": False, "year": False, **{v: ":.2f" for v in DEMO_VARIABLES}},
        color_continuous_scale=info["scale"],
        range_color=(lo, hi),
        projection="natural earth",
    )
    # Grey 'No data' layer for each year (countries missing that year get a hover label too)
    years = sorted(demo["year"].unique())
    fig.add_trace(no_data_layer(demo[demo["year"] == years[0]], variable))
    for frame in fig.frames:
        frame.data = (frame.data[0], no_data_layer(demo[demo["year"] == int(frame.name)], variable))
    # Speed: 0.5 s per year, no morphing between years
    play = fig.layout.updatemenus[0].buttons[0].args[1]
    play["frame"]["duration"] = 500
    play["transition"]["duration"] = 0
    fig.layout.sliders[0].currentvalue.update(prefix="Year: ", font=dict(size=14, color=NAVY))
    fig.update_geos(showframe=False, showcoastlines=False, showcountries=True,
                    countrycolor="#ffffff", countrywidth=0.4,
                    showocean=True, oceancolor="#eef4f9", landcolor="#e3e8ed",
                    bgcolor="rgba(0,0,0,0)", lataxis_range=[-58, 85])  # cut off Antarctica
    # Static map: no dragging/rotating/zooming, hover only
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=560, dragmode=False,
        font=dict(family=FONT, color="#1b2a3a"),
        hoverlabel=dict(bgcolor="white", bordercolor="#d5dde5", font=dict(family=FONT, size=13)),
        coloraxis_colorbar=dict(
            # Unit on top; the empty line keeps it clear of the top tick label
            title=dict(text=info["unit"] + "<br>&nbsp;", side="top", font=dict(size=12)),
            tickvals=ticks, ticktext=tick_text, thickness=12, len=0.75, outlinewidth=0,
        ),
    )
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True, key="world_map",
                        config={"scrollZoom": False, "displayModeBar": False})
        st.caption(f"**{variable.replace(' (demo)', '')}:** {info['definition']}")

    # Country details: pick a country from the list
    section("By country", "Country details")
    countries = sorted(demo["country"].unique())
    country = st.selectbox("Country", countries)
    st.dataframe(
        demo[demo["country"] == country].drop(columns=["iso3", "country"]).set_index("year").round(2).T,
        use_container_width=True,
    )

    section("Interactive", "All countries together",
            "One variable, or two against each other, across all countries. "
            "Hover over a point to see which country it is.")
    placeholder("Scatter plot comes here.")

# --- Tab 3: main results ---
with tab_results:
    section("Findings", "Main results")
    placeholder("The paper's main results and the arguments behind them.")

    section("Estimates", "Regression table")
    with st.container(border=True):
        placeholder("Main coefficient table.")

# --- Tab 4: exam-style questions ---
with tab_questions:
    section("Test yourself", "Questions",
            "Three exam-style questions. Think first, then open the answer.")
    for i in range(1, 4):
        with st.container(border=True):
            st.markdown(f"**Question {i}**")
            placeholder("Question text.")
            with st.expander("Show answer"):
                placeholder("Answer.")

# --- Footer ---
st.markdown(
    f"""<div class="footer">Group project for Empirical Methods, University of Zurich ·
    <a href="{REPO_URL}" target="_blank">Code on GitHub</a></div>""",
    unsafe_allow_html=True,
)
