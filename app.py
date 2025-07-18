import streamlit as st
import pandas as pd
import numpy as np
import datetime

import os
import plotly.graph_objects as go
import plotly.express as px
import base64
import schedule
import time
import threading
from io import BytesIO
from PIL import Image


from data.raw.club_mapping import club_mapping
from modules.get_scoreboard_name import get_scoreboard_name
from modules.get_elo_diff_bar_chart import get_elo_diff_bar_chart
from modules.get_elo_fixtures_bar_chart import get_elo_fixtures_bar_chart
from modules.calculate_average_elo import calculate_average_elo
from modules.get_expected_points import get_expected_points

# Page config
st.set_page_config(page_title="Chance Liga 2025/26 Predikce - ELO Ratings", layout="wide")

# Set the PROJECT ROOT
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def run_script():
    """Runs the data processing script at the scheduled time."""
    st.write("Stahování posledních výsledků...")
    exec(open("scripts/data_processing.py").read())  # Executes the script

def schedule_task():
    """Runs the scheduler in the background without blocking Streamlit."""
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every 60 seconds

@st.cache_resource
def start_scheduler():
    """Ensures the scheduler runs only once per session."""
    schedule.every().day.at("07:14").do(run_script)  # Runs at 08:00 AM UTC
    thread = threading.Thread(target=schedule_task, daemon=True)
    thread.start()

# Start the scheduler (runs in the background)
start_scheduler()

fixtures = pd.read_csv(os.path.join(PROJECT_ROOT, "data/processed/fixtures.csv"))
fixtures = fixtures[fixtures["is_planned_tf"]==True]
fixtures["event_date"] = pd.to_datetime(fixtures["event_date"])
today = datetime.datetime.today()
club_elo = pd.read_csv(os.path.join(PROJECT_ROOT, "data/processed/club_elo.csv"))
league_table = pd.read_csv(os.path.join(PROJECT_ROOT, "data/processed/league_table.csv"))
home_league_table = pd.read_csv(os.path.join(PROJECT_ROOT, "data/processed/home_league_table.csv"))
away_league_table = pd.read_csv(os.path.join(PROJECT_ROOT, "data/processed/away_league_table.csv"))

# Streamlit filter for matchday range
min_matchday = int(fixtures["matchday"].min())
max_matchday = int(fixtures["matchday"].max())

import matplotlib.pyplot as plt



selected_matchday_range = st.sidebar.slider(
    "Výběr ligových kol pro výpočet",
    min_value=min_matchday,
    max_value=max_matchday,
    value=(min_matchday, max_matchday),
    key="matchday_slider"
)

# Add histogram to the slider
# Filter matchday_counts based on selected matchday range
filtered_fixtures_hist = fixtures[
    (fixtures["matchday"] >= selected_matchday_range[0]) & 
    (fixtures["matchday"] <= selected_matchday_range[1])
]
matchday_counts = filtered_fixtures_hist["matchday"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(10, 2))
ax.bar(matchday_counts.index, matchday_counts.values, color='#111A67')
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_xticks(matchday_counts.index)

# Hide some x-tick labels to avoid overlap
xtick_labels = []
skip = max(1, len(matchday_counts) // 10)  # Show at most 10 labels
for i, val in enumerate(matchday_counts.index):
    if i % skip == 0 or i == len(matchday_counts.index) - 1:
        xtick_labels.append(str(val))
    else:
        xtick_labels.append("")
ax.set_xticklabels(xtick_labels)

ax.set_yticks([])

# Increase x-axis label size
ax.tick_params(axis='x', which='both', labelsize=30)

# Remove borders and ticks
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.tick_params(axis='x', which='both', bottom=False, top=False)
ax.tick_params(axis='y', which='both', left=False, right=False)

# Make background transparent
fig.patch.set_alpha(0.0)
ax.patch.set_alpha(0.0)

st.sidebar.markdown("Histogram budoucích zápasů dle kola")

st.sidebar.pyplot(fig)


# Filter fixtures based on selected matchday range
fixtures = fixtures[
    (fixtures["matchday"] >= selected_matchday_range[0]) & 
    (fixtures["matchday"] <= selected_matchday_range[1])
]



club_average_opponent_elo = calculate_average_elo(selected_matchday_range[0], selected_matchday_range[1], PROJECT_ROOT=PROJECT_ROOT).sort_values(by="position", ascending=True)


expected_points = get_expected_points(fixtures)

club_average_opponent_elo = club_average_opponent_elo.merge(expected_points, on='club_id', how='left')
club_average_opponent_elo["total_points"] = np.round(club_average_opponent_elo["points"] + club_average_opponent_elo["total_expected_points"])
club_average_opponent_elo["total_home_points"] = np.round(club_average_opponent_elo["points_home"] + club_average_opponent_elo["home_team_expected_points"])
club_average_opponent_elo["total_away_points"] = np.round(club_average_opponent_elo["points_away"] + club_average_opponent_elo["away_team_expected_points"])
club_average_opponent_elo = club_average_opponent_elo.sort_values(by="total_points", ascending=False).reset_index(drop=True)
club_average_opponent_elo["expected_position"] = club_average_opponent_elo.index + 1
club_average_opponent_elo["position_diff"] = club_average_opponent_elo["position"] - club_average_opponent_elo["expected_position"]
club_average_opponent_elo["position_diff_str"] = club_average_opponent_elo["position_diff"].apply(
    lambda x: f"({int(x):+d}) " if pd.notnull(x) and x != 0 else ""
)

club_average_opponent_elo = club_average_opponent_elo.sort_values(by="total_home_points", ascending=False).reset_index(drop=True)
club_average_opponent_elo["expected_position_home"] = club_average_opponent_elo.index + 1
club_average_opponent_elo["home_position_diff"] = club_average_opponent_elo["position_home"] - club_average_opponent_elo["expected_position_home"]
club_average_opponent_elo["home_position_diff_str"] = club_average_opponent_elo["home_position_diff"].apply(
    lambda x: f"({int(x):+d}) " if pd.notnull(x) and x != 0 else ""
)

club_average_opponent_elo = club_average_opponent_elo.sort_values(by="total_away_points", ascending=False).reset_index(drop=True)
club_average_opponent_elo["expected_position_away"] = club_average_opponent_elo.index + 1
club_average_opponent_elo["away_position_diff"] = club_average_opponent_elo["position_away"] - club_average_opponent_elo["expected_position_away"]
club_average_opponent_elo["away_position_diff_str"] = club_average_opponent_elo["away_position_diff"].apply(
    lambda x: f"({int(x):+d}) " if pd.notnull(x) and x != 0 else ""
)


st.title("Chance Liga 2025/2026")
st.subheader("Jaký klub má v základní části nejtěžší los?")

# Custom CSS for expander color
st.markdown("""
<style>
    /* Change expander background and label color */
    .stExpander {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        border: 2px solid #AEFF00 !important;
    }
    .stExpander > summary {
        color: #111A67 !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

with st.expander("**Dokumentace (klikněte pro skrytí)**", expanded=True, icon="ℹ️", ):
    st.markdown("""
    ⚽️ **Tato aplikace slouží k vizualizaci a analýze losu týmů v Chance lize na základě ELO ratingů.**
    
    Umožňuje:
    - 📊 Porovnat obtížnost losu jednotlivých klubů podle průměrného ELO soupeřů v daném rozmezí kol.
    - 🏆 Zobrazit očekávaný počet bodů, které by kluby měly získat do konce základní části, včetně rozdělení na domácí a venkovní zápasy.
    - 🔍 Filtrovat a porovnávat maximálně tři kluby najednou a zobrazit jejich nadcházející zápasy včetně detailních grafů ELO rozdílů.
    - 🎚️ Interaktivně měnit rozsah kol, pro která se výpočty provádějí.
    - 📅 Pro každý klub zobrazit detailní tabulku zápasů, grafy a očekávané body.
    """)

    st.markdown("### 🧮 Co je ELO rating?")

    st.markdown(
        "ELO rating je číselný systém pro hodnocení síly týmů nebo hráčů na základě jejich výsledků. "
        "Původně byl vyvinut pro šachy ♟️, ale dnes se používá i ve fotbale ⚽️."
    )
    st.markdown(
        "- Každý tým má své ELO skóre.\n"
        "- Po každém zápase se skóre upraví podle očekávaného výsledku a skutečného výsledku.\n"
        "- Pokud slabší tým porazí silnější, získá více bodů, než kdyby vyhrál favorit. 🚀"
        "ELO tak umožňuje objektivně porovnávat sílu týmů na základě jejich výkonů. 📊"
    )

    st.markdown("#### 📐 Výpočet očekávaného výsledku zápasu")
    st.markdown("Pravděpodobnost výhry domácího týmu:")
    st.latex(r"E_H = \frac{1}{1 + 10^{(R_B - R_A + A_{H})/400}}")
    st.markdown("Pravděpodobnost výhry venkovního týmu:")
    st.latex(r"E_A = \frac{1}{1 + 10^{(R_A - R_H + A_{H})/400}}")
    st.markdown("Pravděpodobnost remízy:")
    st.latex(r"E_D = 1 - (E_H + E_A)")

    # Streamlit does not support inline LaTeX in markdown, only block-level formulas via st.latex.
    st.markdown("kde $R_H$ je ELO rating domácího týmu, $R_A$ je ELO rating soupeře, $A_H$ je domácí výhoda.")

# Initialize session state for selected club
if "selected_club_ids" not in st.session_state:
    st.session_state["selected_club_ids"] = []


st.markdown("""
<style>
    /* Sidebar background for light mode */
    [data-testid=stSidebar] {
        background-color: #AEFF00;
    }

    /* Buttons in light mode */
    .stButton button {
        background-color: #FAFAFA;
        font-weight: bold;
        color: #577F00;
        border: 1px solid #577F00;
    }
    .stButton button:hover {
        background-color: #AEFF00;
        color: #577F00;
        border: 1px solid #577F00;
    }
    .stButton > button:focus {
        background-color: #FAFAFA !important;
        color: #577F00 !important;
        border: 1px solid #577F00 !important;
    }

    /* Text colors for light mode */
    .st-emotion-cache-1373cj4 {
        color: #111A67;
    }
    .st-emotion-cache-89jlt8 {
        color: #111A67;
    }
    .st-ar {
        background: #111A67;
    }
    .st-ae {
        color: #111A67;
    }

    /* Background for a specific class in light mode */
    .st-emotion-cache-1dj3ksd {
        background-color: #111A67;
    }


    /* === Dark mode overrides === */
    body.dark [data-testid=stSidebar] {
        background-color: #4a5a00;  /* darker green for sidebar in dark mode */
    }

    body.dark .stButton button {
        background-color: #222;   /* dark button background */
        font-weight: bold;
        color: #a5d300;           /* brighter green text */
        border: 1px solid #a5d300;
    }
    body.dark .stButton button:hover {
        background-color: #9ecf00; /* bright green on hover */
        color: #222;
        border: 1px solid #9ecf00;
    }
    body.dark .stButton > button:focus {
        background-color: #222 !important;
        color: #a5d300 !important;
        border: 1px solid #a5d300 !important;
    }

    body.dark .st-emotion-cache-1373cj4,
    body.dark .st-emotion-cache-89jlt8,
    body.dark .st-ae {
        color: #cde066;  /* lighter text color for dark mode */
    }

    body.dark .st-emotion-cache-1dj3ksd,
    body.dark .st-ar {
        background-color: #222;   /* dark background in dark mode */
    }
</style>
""", unsafe_allow_html=True)



with st.sidebar:
    st.markdown("## Vyběr klubů")
    st.markdown("Kliknutním zobrazíte/skryjete nadcházející zápasy")
    for idx, row in club_average_opponent_elo[["club_id", "scoreboard", "club_logo"]].iterrows():
        club_id = row["club_id"]
        scoreboard = row["scoreboard"]
        club_logo = row["club_logo"]
        cols = st.columns([1, 2])  # Adjust the ratio as needed
        with cols[0]:
            st.image(os.path.join(PROJECT_ROOT, club_logo), width=30, output_format="auto")
        with cols[1]:
            if st.button(f"{scoreboard}", key=scoreboard):  # Unique key for each button
                if club_id in st.session_state["selected_club_ids"]:
                    st.session_state["selected_club_ids"].remove(club_id)
                elif len(st.session_state["selected_club_ids"]) < 3:
                    st.session_state["selected_club_ids"].append(club_id)
                else:
                    st.error("Maximální počet klubů pro srovnání dosažen")
    
if st.session_state["selected_club_ids"]:
    if st.button("Reset filtru", key="clear_filter"):
        st.session_state.pop("selected_club_ids", None)
        if "selected_club_ids" not in st.session_state:
            st.session_state["selected_club_ids"] = []

filtered_club_average_opponent_elo = club_average_opponent_elo.sort_values(by="position", ascending=False)


# Show selected clubs
if st.session_state["selected_club_ids"]:
    selected_club_names = [club_mapping[club_id]["club_name"] for club_id in st.session_state["selected_club_ids"]]
    filtered_club_average_opponent_elo = club_average_opponent_elo[club_average_opponent_elo["club_name"].isin(selected_club_names)].sort_values(by='position', ascending=False)
    st.success(f"Vyfiltrované kluby: {', '.join(selected_club_names)}")


cols = st.columns(max(1, len(st.session_state["selected_club_ids"])), gap="medium")

for idx, club_id in enumerate(st.session_state["selected_club_ids"]):
    elo = club_elo[club_elo["club_id"] == club_id]["elo_rating"].values[0]
    # Apply filtering
    filtered_fixtures = fixtures[
        (fixtures["home_team_id"] == club_id) | (fixtures["away_team_id"] == club_id)
    ]
    filtered_fixtures["home_away"] = np.where(filtered_fixtures["home_team_id"] == club_id, "Home", "Away")
    filtered_fixtures["club_id"] = club_id
    filtered_fixtures["club_elo"] = np.where(filtered_fixtures["home_team_id"] == club_id, filtered_fixtures["home_team_elo"], filtered_fixtures["away_team_elo"])
    filtered_fixtures["elo_diff"] = np.where(filtered_fixtures["home_team_id"] == club_id, filtered_fixtures["home_team_elo"] - filtered_fixtures["away_team_elo"], filtered_fixtures["away_team_elo"] - filtered_fixtures["home_team_elo"])
    filtered_fixtures = filtered_fixtures[pd.to_datetime(filtered_fixtures["event_date"]) >= today]
    filtered_fixtures["opponent"] = filtered_fixtures.apply(
        lambda row: row["home_team"] if row["home_away"] == "Away" else row["away_team"], axis=1
    )
    filtered_fixtures["opponent_elo"] = filtered_fixtures.apply(
        lambda row: row["home_team_elo"] if row["home_away"] == "Away" else row["away_team_elo"], axis=1
    )
    filtered_fixtures["opponent_id"] = filtered_fixtures.apply(
        lambda row: row["home_team_id"] if row["home_away"] == "Away" else row["away_team_id"], axis=1
    )
    # Convert event_date to Unix timestamp
    filtered_fixtures["event_timestamp"] = filtered_fixtures["event_date"].apply(lambda x: x.timestamp())
   
    fixtures_table = filtered_fixtures[["matchday", "event_timestamp", "home_team","away_team","home_team_elo","away_team_elo"]]
    fixtures_table['home_team_elo'] = fixtures_table['home_team_elo'].astype(int).apply(lambda x: f"{x:,}".replace(",", ""))
    fixtures_table['away_team_elo'] = fixtures_table['away_team_elo'].astype(int).apply(lambda x: f"{x:,}".replace(",", ""))

    fixtures_table["event_timestamp"] = filtered_fixtures.apply(
        lambda row: datetime.datetime.fromtimestamp(row["event_timestamp"]).strftime('%Y-%m-%d') + ' ' + row["event_time"], axis=1
    )
    fixtures_table.columns = ['Matchday','Datum','Domácí','Hosté','ELO Domácí', 'ELO Hosté']
    fixtures_table = fixtures_table.set_index("Matchday")

    fig_elo_diff = get_elo_diff_bar_chart(filtered_fixtures, PROJECT_ROOT=PROJECT_ROOT)
    fig_elo = get_elo_fixtures_bar_chart(filtered_fixtures, PROJECT_ROOT=PROJECT_ROOT)

    with cols[idx]:
        st.image(os.path.join(PROJECT_ROOT, club_mapping[club_id]['club_logo']), width=50, output_format="auto")
        st.header(f"{club_mapping[club_id]['club_name']}")
        st.subheader(f'Očekávané body: {np.round(expected_points[expected_points["club_id"]==club_id]["total_expected_points"].iloc[0]).astype(int)}')
        st.markdown(f"**za {selected_matchday_range[0]}. - {selected_matchday_range[1]}. kolo**" if selected_matchday_range[0] != selected_matchday_range[1] else f"**za {selected_matchday_range[0]}. kolo**")
        st.plotly_chart(fig_elo)
        st.plotly_chart(fig_elo_diff)
        st.dataframe(fixtures_table.sort_values(by='Matchday'), use_container_width=True)

st.divider()

st.markdown("### Očekávaný počet bodů")

filtered_club_average_opponent_elo = filtered_club_average_opponent_elo.sort_values(by="expected_position", ascending=False)
# Create figure
fig_ep = go.Figure()

# Add the club's own ELO rating (wider, gray bars)
fig_ep.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["total_points"],
    name="Celkem",
    orientation='h',
    marker=dict(color='#AEFF00'),
    width=0.9,
    text=np.round(filtered_club_average_opponent_elo["total_points"]),
    textfont=dict(color='grey', size=10),
    textposition='outside',
    textangle=0  # Rotate text to be vertical
))

# Add the average opponent ELO (thinner, colored bars)
fig_ep.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["points"],
    name="Aktuální body",
    orientation='h',
    marker=dict(color='#111A67'),
    width=0.9,
    text=filtered_club_average_opponent_elo["points"],
    textfont=dict(color='white', size=10),
    textposition='inside',
    textangle=0  # Rotate text to be vertical
))

# Add club logos
for idx, row in filtered_club_average_opponent_elo.iterrows():
    club_info = next((item for item in club_mapping.values() if item["club_name"] == row["club_name"]), None)
    if club_info:
        fig_ep.add_layout_image(
            dict(
                source=Image.open(os.path.join(PROJECT_ROOT, club_info["club_logo"])),
                xref="paper", yref="y",
                x=-0.01, y=row["club_name"],
                sizex=0.05, sizey=0.9,
                xanchor="right", yanchor="middle"
            )
        )
        fig_ep.add_annotation(
            x=row["points"] + row["total_expected_points"]/2,
            y=row["club_name"],
            text=f"+{np.round(row["total_expected_points"]).astype(int)}",
            showarrow=False,
            font=dict(size=10, color="green")
        )

# Layout adjustments
fig_ep.update_layout(
    barmode='overlay',  # Overlapping bars
    yaxis=dict(
        tickmode='array',
        tickvals=filtered_club_average_opponent_elo["club_name"],
        ticktext=filtered_club_average_opponent_elo["position_diff_str"] + filtered_club_average_opponent_elo["expected_position"].astype(str) + ". " + filtered_club_average_opponent_elo["scoreboard"].astype(str),
        tickfont=dict(size=10),
        tickangle=0,
        automargin=True,
        ticklabelposition="outside",
        ticklen=25,
        tickcolor='rgba(0,0,0,0)',
    ),
    xaxis=dict(
        #type = 'log',
        showgrid=False,
        gridcolor='rgba(0,0,0,0.3)',  # Slightly visible vertical grid lines
        gridwidth=1,
        griddash='dot' # Dashed grid lines
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5,
        traceorder="reversed"  # Reverse the legend order
    ),
    margin=dict(l=10, r=10, t=20, b=100),  # Adjust margins as needed
)

filtered_club_average_opponent_elo = filtered_club_average_opponent_elo.sort_values(by='expected_position_home',ascending=False)

# Create figure
fig_ep_home = go.Figure()

# Add the club's own ELO rating (wider, gray bars)
fig_ep_home.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["total_home_points"],
    name="Očekávané body doma",
    orientation='h',
    marker=dict(color='rgba(0,0,0,0.15)'),
    width=0.9,
    text=np.round(filtered_club_average_opponent_elo["total_home_points"]),
    textfont=dict(color='grey', size=10),
    textposition='outside',
    textangle=0
))

# Add the average opponent ELO (thinner, colored bars)
fig_ep_home.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["points_home"],
    name="Aktulání body doma",
    orientation='h',
    marker=dict(color='#585e94'),
    width=0.9,
    text=filtered_club_average_opponent_elo["points_home"],
    textfont=dict(color='white', size=10),
    textposition='inside',
    textangle=0
))

# Add club logos
for idx, row in filtered_club_average_opponent_elo.iterrows():
    club_info = next((item for item in club_mapping.values() if item["club_name"] == row["club_name"]), None)
    if club_info:
        fig_ep_home.add_layout_image(
            dict(
                source=Image.open(os.path.join(PROJECT_ROOT, club_info["club_logo"])),
                xref="paper", yref="y",
                x=-0.01, y=row["club_name"],
                sizex=0.05, sizey=0.9,
                xanchor="right", yanchor="middle"
            )
        )
        fig_ep_home.add_annotation(
            x=row["points_home"] + row["home_team_expected_points"]/2,
            y=row["club_name"],
            text=f"+{np.round(row["home_team_expected_points"]).astype(int)}",
            showarrow=False,
            font=dict(size=10, color="grey")
        )

# Layout adjustments
fig_ep_home.update_layout(
    barmode='overlay',  # Overlapping bars
    yaxis=dict(
        tickmode='array',
        tickvals=filtered_club_average_opponent_elo["club_name"],
        ticktext=filtered_club_average_opponent_elo["home_position_diff_str"] + filtered_club_average_opponent_elo["expected_position_home"].astype(str) + ". " + filtered_club_average_opponent_elo["scoreboard"].astype(str),
        tickfont=dict(size=10),
        tickangle=0,
        automargin=True,
        ticklabelposition="outside",
        ticklen=25,
        tickcolor='rgba(0,0,0,0)',
    ),
    xaxis=dict(
        #type = 'log',
        showgrid=False,
        gridcolor='rgba(0,0,0,0.3)',  # Slightly visible vertical grid lines
        gridwidth=1,
        griddash='dot' # Dashed grid lines
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5,
        traceorder="reversed"  # Reverse the legend order
    ),
    margin=dict(l=10, r=10, t=20, b=100),  # Adjust margins as needed
)

filtered_club_average_opponent_elo = filtered_club_average_opponent_elo.sort_values(by='expected_position_away',ascending=False)

# Create figure
fig_ep_away = go.Figure()

# Add the club's own ELO rating (wider, gray bars)
fig_ep_away.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["total_away_points"],
    name="Očekávané body venku",
    orientation='h',
    marker=dict(color='rgba(0,0,0,0.15)'),
    width=0.9,
    text=np.round(filtered_club_average_opponent_elo["total_away_points"]),
    textfont=dict(color='grey', size=10),
    textposition='outside',
    textangle=0
))

# Add the average opponent ELO (thinner, colored bars)
fig_ep_away.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["points_away"],
    name="Aktulání body venku",
    orientation='h',
    marker=dict(color='#9fa3c2'),
    width=0.9,
    text=filtered_club_average_opponent_elo["points_away"],
    textfont=dict(color='white', size=10),
    textposition='inside',
    textangle=0
))

# Add club logos
for idx, row in filtered_club_average_opponent_elo.iterrows():
    club_info = next((item for item in club_mapping.values() if item["club_name"] == row["club_name"]), None)
    if club_info:
        fig_ep_away.add_layout_image(
            dict(
                source=Image.open(os.path.join(PROJECT_ROOT, club_info["club_logo"])),
                xref="paper", yref="y",
                x=-0.01, y=row["club_name"],
                sizex=0.05, sizey=0.9,
                xanchor="right", yanchor="middle"
            )
        )
        fig_ep_away.add_annotation(
            x=row["points_away"] + row["away_team_expected_points"]/2,
            y=row["club_name"],
            text=f"+{np.round(row["away_team_expected_points"]).astype(int)}",
            showarrow=False,
            font=dict(size=10, color="grey")
        )

# Layout adjustments
fig_ep_away.update_layout(
    barmode='overlay',  # Overlapping bars
    yaxis=dict(
        tickmode='array',
        tickvals=filtered_club_average_opponent_elo["club_name"],
        ticktext=filtered_club_average_opponent_elo["away_position_diff_str"] + filtered_club_average_opponent_elo["expected_position_away"].astype(str) + ". " + filtered_club_average_opponent_elo["scoreboard"].astype(str),
        tickfont=dict(size=10),
        tickangle=0,
        automargin=True,
        ticklabelposition="outside",
        ticklen=25,
        tickcolor='rgba(0,0,0,0)',
    ),
    xaxis=dict(
        #type = 'log',
        showgrid=False,
        gridcolor='rgba(0,0,0,0.3)',  # Slightly visible vertical grid lines
        gridwidth=1,
        griddash='dot' # Dashed grid lines
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5,
        traceorder="reversed"  # Reverse the legend order
    ),
    margin=dict(l=10, r=10, t=20, b=100),  # Adjust margins as needed
)

filtered_club_average_opponent_elo = filtered_club_average_opponent_elo.sort_values(by="position", ascending=False)

# Create figure
fig1 = go.Figure()

# Add the club's own ELO rating (wider, gray bars)
fig1.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["club_elo"],
    name="Klubové ELO",
    orientation='h',
    marker=dict(color='rgba(0,0,0,0.2)'),
    width=0.9
))

# Add the average opponent ELO (thinner, colored bars)
fig1.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["average_opponent_elo"],
    name="Průměrné ELO soupeře",
    orientation='h',
    marker=dict(color='#111A67'),
    width=0.6,
    text=filtered_club_average_opponent_elo["average_opponent_elo"],
    textfont=dict(color='black', size=10),
    textposition='outside'
))

# Add club logos
for idx, row in filtered_club_average_opponent_elo.iterrows():
    club_info = next((item for item in club_mapping.values() if item["club_name"] == row["club_name"]), None)
    if club_info:
        fig1.add_layout_image(
            dict(
                source=Image.open(os.path.join(PROJECT_ROOT, club_info["club_logo"])),
                xref="paper", yref="y",
                x=-0.01, y=row["club_name"],
                sizex=0.05, sizey=0.9,
                xanchor="right", yanchor="middle"
            )
        )

# Layout adjustments
fig1.update_layout(
    barmode='overlay',  # Overlapping bars
    yaxis=dict(
        tickmode='array',
        tickvals=filtered_club_average_opponent_elo["club_name"],
        ticktext=filtered_club_average_opponent_elo["position"].astype(str) + ". " + filtered_club_average_opponent_elo["scoreboard"].astype(str) + " (" + filtered_club_average_opponent_elo["points"].astype(str) + " b.)",
        tickfont=dict(size=10),
        tickangle=0,
        automargin=True,
        ticklabelposition="outside",
        ticklen=25,
        tickcolor='rgba(0,0,0,0)',
    ),
    xaxis=dict(
        type = 'log',
        showgrid=True,
        gridcolor='rgba(0,0,0,0.3)',  # Slightly visible vertical grid lines
        gridwidth=1,
        griddash='dot' # Dashed grid lines
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5,
        traceorder="reversed"  # Reverse the legend order
    ),
    margin=dict(l=100, r=20, t=20, b=100),  # Adjust margins as needed
)

# Create figure
fig2 = go.Figure()

# Add the club's own ELO rating (wider, gray bars)
fig2.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["club_elo"],
    name="Klubové ELO",
    orientation='h',
    marker=dict(color='rgba(0,0,0,0.2)'),
    width=0.9
))

# Add the average opponent ELO (thinner, colored bars)
fig2.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["average_home_opponent_elo"],
    name="Průměrné ELO soupeře - doma",
    orientation='h',
    marker=dict(color='#585e94'),
    width=0.6,  # Thinner bars
    text=filtered_club_average_opponent_elo["average_home_opponent_elo"].astype(int),
    textfont = dict(color = 'black', size = 10),
    textposition='outside'
))

# Add club logos
for idx, row in filtered_club_average_opponent_elo.iterrows():
    club_info = next((item for item in club_mapping.values() if item["club_name"] == row["club_name"]), None)
    if club_info:
        fig2.add_layout_image(
            dict(
            source=Image.open(os.path.join(PROJECT_ROOT, club_info["club_logo"])),
            xref="paper", yref="y",
            x=-0.01, y=row["club_name"],
            sizex=0.05, sizey=0.9,
            xanchor="right", yanchor="middle"
            )
        )

# Layout adjustments
fig2.update_layout(
    barmode='overlay',  # Overlapping bars
    yaxis=dict(
        tickmode='array',
        tickvals=filtered_club_average_opponent_elo["club_name"],
        ticktext=filtered_club_average_opponent_elo["position"].astype(str) + ". " + filtered_club_average_opponent_elo["scoreboard"].astype(str) + " (" + filtered_club_average_opponent_elo["points"].astype(str) + " b.)",
        tickfont=dict(size=10),
        tickangle=0,
        automargin=True,
        ticklabelposition="outside",
        ticklen=25,
        tickcolor='rgba(0,0,0,0)',
    ),
    xaxis=dict(
        type = 'log',
        showgrid=True,
        gridcolor='rgba(0,0,0,0.3)',  # Slightly visible vertical grid lines
        gridwidth=1,
        griddash='dot' # Dashed grid lines
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5,
        traceorder="reversed"
    ),
    margin=dict(l=100, r=20, t=20, b=100)  # Adjust margins as needed
)


# Create figure
fig3 = go.Figure()

# Add the club's own ELO rating (wider, gray bars)
fig3.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["club_elo"],
    name="Klubové ELO",
    orientation='h',
    marker=dict(color='rgba(0,0,0,0.2)'),
    width=0.9
))

# Add the average opponent ELO (thinner, colored bars)
fig3.add_trace(go.Bar(
    y=filtered_club_average_opponent_elo["club_name"],
    x=filtered_club_average_opponent_elo["average_away_opponent_elo"],
    name="Průměrné ELO soupeře - venku",
    orientation='h',
    marker=dict(color='#9fa3c2'),
    width=0.6,  # Thinner bars
    text=filtered_club_average_opponent_elo["average_away_opponent_elo"].astype(int),
    textfont = dict(color = 'black', size = 10),
    textposition='outside'
))

# Add club logos
for idx, row in filtered_club_average_opponent_elo.iterrows():
    club_info = next((item for item in club_mapping.values() if item["club_name"] == row["club_name"]), None)
    if club_info:
        fig3.add_layout_image(
            dict(
                source=Image.open(os.path.join(PROJECT_ROOT, club_info["club_logo"])),
                xref="paper", yref="y",
                x=-0.01, y=row["club_name"],
                sizex=0.05, sizey=0.9,
                xanchor="right", yanchor="middle"
            )
        )

# Layout adjustments
fig3.update_layout(
    barmode='overlay',  # Overlapping bars
    yaxis=dict(
        tickmode='array',
        tickvals=filtered_club_average_opponent_elo["club_name"],
        ticktext=filtered_club_average_opponent_elo["position"].astype(str) + ". " + filtered_club_average_opponent_elo["scoreboard"].astype(str) + " (" + filtered_club_average_opponent_elo["points"].astype(str) + " b.)",
        tickfont=dict(size=10),
        tickangle=0,
        automargin=True,
        ticklabelposition="outside",
        ticklen=25,
        tickcolor='rgba(0,0,0,0)',
    ),
    xaxis=dict(
        type = 'log',
        showgrid=True,
        gridcolor='rgba(0,0,0,0.3)',  # Slightly visible vertical grid lines
        gridwidth=1,
        griddash='dot' # Dashed grid lines
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5,
        traceorder="reversed"
    ),
    margin=dict(l=100, r=20, t=20, b=100)  # Adjust margins as needed
)

cols = st.columns(3, gap="small")
with cols[0]:
    st.markdown('##### Celkem')
    st.plotly_chart(fig_ep, use_container_width=True, height = 1000)
with cols[1]:
    st.markdown('##### Domácí zápasy')
    st.plotly_chart(fig_ep_home, use_container_width=True, height = 1000)
with cols[2]:
    st.markdown('##### Venkovní zápasy')
    st.plotly_chart(fig_ep_away, use_container_width=True, height = 1000)

st.divider()
st.markdown("### Průměrné ELO soupeře")
cols = st.columns(3, gap="small")
with cols[0]:
    st.markdown('##### Celkem')
    st.plotly_chart(fig1, use_container_width=True, height = 1000)
with cols[1]:
    st.markdown('##### Domácí zápasy')
    st.plotly_chart(fig2, use_container_width=True, height = 1000)
with cols[2]:
    st.markdown('##### Venkovní zápasy')
    st.plotly_chart(fig3, use_container_width=True, height = 1000)

