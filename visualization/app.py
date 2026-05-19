import sys
from pathlib import Path

# ==========================================================
# PROJECT ROOT
# ==========================================================

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

# ==========================================================
# IMPORTS
# ==========================================================

import streamlit as st
import pandas as pd

from analysis.analytics_engine import AnalyticsEngine
from analysis.rankings_engine import RankingsEngine
from analysis.matchup_engine import MatchupEngine

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="footyIQ",
    page_icon="🧠",
    layout="wide"
)

# ==========================================================
# GLOBAL STYLING
# ==========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1400px;
    }

    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 14px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1rem;
    }

    th {
        text-align: center !important;
        vertical-align: middle !important;
        font-weight: 700 !important;
        padding: 10px;
        border: 1px solid #d1d5db;
    }

    td {
        text-align: center !important;
        vertical-align: middle !important;
        padding: 10px;
        border: 1px solid #d1d5db;
    }

    table td,
    table th {
        font-size: 14px !important;
    }

    @media (max-width: 768px) {

        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }

        div[data-testid="stMetric"] {
            padding: 0.75rem;
        }

        table td,
        table th {
            font-size: 12px !important;
            padding: 6px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# CONFIG
# ==========================================================

DATA_PATH = "data/raw/2026/teams.parquet"

# ==========================================================
# DISPLAY NAMES
# ==========================================================

DISPLAY_NAMES = {

    "score": "Score",
    "kicks": "Kicks",
    "handballs": "Handballs",
    "marks": "Marks",
    "hitouts": "Hitouts",
    "tackles": "Tackles",
    "cp": "CP",
    "clearances": "Clearances",
    "r50": "R50",
    "spoils": "Spoils",

    "round": "Round",

    "avg": "Avg",
    "form": "Form",
    "rank": "Rank",
    "vol": "Vol",
    "volatility": "Volatility"
}

# ==========================================================
# COLOURS
# ==========================================================

WIN_COLOUR = (
    "background-color: #dcfce7; "
    "color: #166534; "
    "font-weight: 600;"
)

LOSS_COLOUR = (
    "background-color: #fee2e2; "
    "color: #991b1b; "
    "font-weight: 600;"
)

DRAW_COLOUR = (
    "background-color: #e5e7eb; "
    "color: #374151; "
    "font-weight: 600;"
)

# ==========================================================
# PRETTIFY COLUMN NAMES
# ==========================================================

def prettify_column_name(col):

    lower_col = str(col).lower()

    if lower_col in DISPLAY_NAMES:
        return DISPLAY_NAMES[lower_col]

    return str(col)

# ==========================================================
# TABLE RENDER
# ==========================================================

def render_table(styled_df):

    st.markdown(
        styled_df.to_html(index=False),
        unsafe_allow_html=True
    )

# ==========================================================
# GENERIC TABLE FORMATTER
# ==========================================================

def format_table(df):

    df = df.copy()

    df.columns = [
        prettify_column_name(col)
        for col in df.columns
    ]

    df = df.reset_index(drop=True)

    format_dict = {}

    for col in df.columns:

        if "Volatility" in col:

            format_dict[col] = "±{:.1f}%"

        elif pd.api.types.is_numeric_dtype(df[col]):

            format_dict[col] = "{:.1f}"

    return (
        df.style
        .hide(axis="index")
        .format(format_dict)
    )

# ==========================================================
# MATCHUP TABLE STYLING
# ==========================================================

def style_matchup_comparison(
    df,
    team_a,
    team_b
):

    df = df.reset_index(drop=True)

    df = df.rename(
        columns={
            f"{team_a} Vol":
                f"{team_a} Volatility",

            f"{team_b} Vol":
                f"{team_b} Volatility"
        }
    )

    def colour_cells(row):

        styles = [""] * len(row)

        a_rank_col = f"{team_a} Rank"
        b_rank_col = f"{team_b} Rank"

        for i, col in enumerate(row.index):

            if "Rank" in col:

                if row[a_rank_col] < row[b_rank_col]:

                    if team_a in col:
                        styles[i] = WIN_COLOUR

                    elif team_b in col:
                        styles[i] = LOSS_COLOUR

                elif row[b_rank_col] < row[a_rank_col]:

                    if team_a in col:
                        styles[i] = LOSS_COLOUR

                    elif team_b in col:
                        styles[i] = WIN_COLOUR

                else:

                    styles[i] = DRAW_COLOUR

        return styles

    format_dict = {}

    for col in df.columns:

        if "Rank" in col:

            format_dict[col] = "{:.0f}"

        elif "Volatility" in col:

            format_dict[col] = "±{:.1f}%"

        elif pd.api.types.is_numeric_dtype(df[col]):

            format_dict[col] = "{:.1f}"

    return (
        df.style
        .hide(axis="index")
        .apply(
            colour_cells,
            axis=1
        )
        .format(format_dict)
    )

# ==========================================================
# RESULT COLOURING
# ==========================================================

def colour_result(val):

    if val == "W":
        return WIN_COLOUR

    elif val == "L":
        return LOSS_COLOUR

    elif val == "D":
        return DRAW_COLOUR

    return ""

# ==========================================================
# ROUND COMPARISON STYLING
# ==========================================================

def style_round_comparison(
    team_a_df,
    team_b_df
):

    team_a_styled = (
        team_a_df
        .reset_index(drop=True)
        .copy()
    )

    team_b_styled = (
        team_b_df
        .reset_index(drop=True)
        .copy()
    )

    team_a_styled.columns = [
        prettify_column_name(col)
        for col in team_a_styled.columns
    ]

    team_b_styled.columns = [
        prettify_column_name(col)
        for col in team_b_styled.columns
    ]

    def style_team_a(row_idx):

        styles = []

        for col in team_a_styled.columns:

            if col == "Round":

                styles.append("")
                continue

            a_val = team_a_styled.loc[
                row_idx,
                col
            ]

            b_val = team_b_styled.loc[
                row_idx,
                col
            ]

            if a_val > b_val:

                styles.append(WIN_COLOUR)

            elif a_val < b_val:

                styles.append(LOSS_COLOUR)

            else:

                styles.append(DRAW_COLOUR)

        return styles

    def style_team_b(row_idx):

        styles = []

        for col in team_b_styled.columns:

            if col == "Round":

                styles.append("")
                continue

            a_val = team_a_styled.loc[
                row_idx,
                col
            ]

            b_val = team_b_styled.loc[
                row_idx,
                col
            ]

            if b_val > a_val:

                styles.append(WIN_COLOUR)

            elif b_val < a_val:

                styles.append(LOSS_COLOUR)

            else:

                styles.append(DRAW_COLOUR)

        return styles

    styled_a = (
        team_a_styled.style
        .hide(axis="index")
        .apply(
            lambda x: style_team_a(x.name),
            axis=1
        )
    )

    styled_b = (
        team_b_styled.style
        .hide(axis="index")
        .apply(
            lambda x: style_team_b(x.name),
            axis=1
        )
    )

    return styled_a, styled_b

# ==========================================================
# LOAD ANALYTICS
# ==========================================================

@st.cache_data
def load_analytics():

    analytics_engine = AnalyticsEngine(
        DATA_PATH
    )

    rankings_engine = RankingsEngine()

    matchup_engine = MatchupEngine()

    analytics_engine.load_data()

    season = analytics_engine.build_analytics(
        analytics_engine.df
    )

    recent = analytics_engine.build_analytics(
        analytics_engine.recent_df
    )

    recent_form_change = (
        analytics_engine.compute_recent_form_change(
            season["averages"],
            recent["averages"]
        )
    )

    profiles = (
        analytics_engine.identify_strengths_weaknesses(
            season["ranks"]
        )
    )

    power_rankings = (
        rankings_engine.compute_power_rankings(
            season["percentiles"],
            season["win_rates"],
            season["volatility"]
        )
    )

    leaderboards = (
        rankings_engine.build_category_leaderboards(
            season
        )
    )

    return {

        "season": season,

        "recent_form_change":
            recent_form_change,

        "profiles": profiles,

        "power_rankings":
            power_rankings,

        "leaderboards":
            leaderboards,

        "matchup_engine":
            matchup_engine,

        "raw_df":
            analytics_engine.df
    }

# ==========================================================
# LOAD DATA
# ==========================================================

data = load_analytics()

season = data["season"]

recent_form_change = data[
    "recent_form_change"
]

profiles = data["profiles"]

power_rankings = data[
    "power_rankings"
]

leaderboards = data[
    "leaderboards"
]

matchup_engine = data[
    "matchup_engine"
]

raw_df = data["raw_df"]

teams = sorted(
    season["averages"].index.tolist()
)

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("footyIQ")

page = st.sidebar.radio(
    "Navigation",
    [
        "Matchup View",
        "Team Analysis",
        "Category Leaderboards",
        "Power Rankings"
    ]
)

# ==========================================================
# MATCHUP VIEW
# ==========================================================

if page == "Matchup View":

    st.title("Head-to-Head Matchup")

    col1, col2 = st.columns(2)

    with col1:

        team_a = st.selectbox(
            "Select Team A",
            teams,
            index=0
        )

    with col2:

        team_b = st.selectbox(
            "Select Team B",
            teams,
            index=1
        )

    matchup = matchup_engine.build_head_to_head(
        team_a,
        team_b,
        season,
        recent_form_change
    )

    projected_score = matchup[
        "projected_score"
    ]

    comparison_table = matchup[
        "comparison_table"
    ]

    st.subheader("Matchup Summary")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:

        st.metric(
            label=f"{team_a} Weighted Matchup Score",
            value=projected_score[team_a]
        )

    with summary_col2:

        st.metric(
            label=f"{team_b} Weighted Matchup Score",
            value=projected_score[team_b]
        )

    st.caption(
        "Score = 3 pts | Spoils = 2 pts | All other categories = 1 pt"
    )

    st.subheader("Category Comparison")

    styled_comparison = (
        style_matchup_comparison(
            comparison_table,
            team_a,
            team_b
        )
    )

    render_table(styled_comparison)

    # ======================================================
    # HISTORICAL MATCHUP
    # ======================================================

    st.subheader(
        "Historical Matchup Simulation"
    )

    historical = (
        matchup_engine.build_round_matchup_history(
            team_a,
            team_b,
            raw_df
        )
    )

    summary = historical["summary"]

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:

        st.metric(
            f"{team_a} Win %",
            f"{summary['team_a_win_pct']}%"
        )

    with summary_col2:

        st.metric(
            "Draws",
            summary["draws"]
        )

    with summary_col3:

        st.metric(
            f"{team_b} Win %",
            f"{summary['team_b_win_pct']}%"
        )

    styled_team_a, styled_team_b = (
        style_round_comparison(
            historical["team_a_rounds"],
            historical["team_b_rounds"]
        )
    )

    st.markdown(f"### {team_a}")
    render_table(styled_team_a)

    st.markdown(
        "### Head-to-Head Results"
    )

    styled_h2h = (
        historical[
            "head_to_head_table"
        ]
        .reset_index(drop=True)
        .style
        .hide(axis="index")
        .map(
            colour_result,
            subset=[
                f"{team_a} Result",
                f"{team_b} Result"
            ]
        )
    )

    render_table(styled_h2h)

    st.markdown(f"### {team_b}")
    render_table(styled_team_b)

# ==========================================================
# TEAM ANALYSIS
# ==========================================================

elif page == "Team Analysis":

    st.title("Team Analysis")

    selected_team = st.selectbox(
        "Select Team",
        teams
    )

    team_power = power_rankings[
        power_rankings["Team"] ==
        selected_team
    ].iloc[0]

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:

        st.metric(
            "Power Rank",
            f"#{team_power['Power Rank']}"
        )

    with metric_col2:

        st.metric(
            "Power Score",
            round(
                team_power["Power Score"],
                1
            )
        )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Strengths")

        strengths = profiles[
            selected_team
        ]["strengths"]

        if strengths:

            for s in strengths:
                st.success(s)

        else:
            st.write("None")

    with col2:

        st.subheader("Weaknesses")

        weaknesses = profiles[
            selected_team
        ]["weaknesses"]

        if weaknesses:

            for w in weaknesses:
                st.error(w)

        else:
            st.write("None")

    st.subheader(
        "Category Breakdown"
    )

    rows = []

    for category in season[
        "averages"
    ].columns:

        rows.append({

            "Category":
                prettify_column_name(category),

            "Rank":
                season["ranks"].loc[
                    selected_team,
                    category
                ],

            "Average":
                round(
                    season["averages"].loc[
                        selected_team,
                        category
                    ],
                    1
                ),

            "Form vs Avg %":
                round(
                    recent_form_change.loc[
                        selected_team,
                        category
                    ],
                    1
                ),

            "Win Rate %":
                round(
                    season["win_rates"].loc[
                        selected_team,
                        category
                    ],
                    1
                ),

            "Volatility %":
                round(
                    season["volatility"].loc[
                        selected_team,
                        category
                    ],
                    1
                )
        })

    report_df = pd.DataFrame(rows)

    styled_report = format_table(
        report_df
    )

    render_table(styled_report)

# ==========================================================
# CATEGORY LEADERBOARDS
# ==========================================================

elif page == "Category Leaderboards":

    st.title(
        "Category Leaderboards"
    )

    selected_category = st.selectbox(
        "Select Category",
        list(leaderboards.keys())
    )

    leaderboard = leaderboards[
        selected_category
    ]

    styled_leaderboard = format_table(
        leaderboard
    )

    render_table(styled_leaderboard)

# ==========================================================
# POWER RANKINGS
# ==========================================================

elif page == "Power Rankings":

    st.title("Overall Power Rankings")

    styled_power = format_table(
        power_rankings.round(1)
    )

    render_table(styled_power)