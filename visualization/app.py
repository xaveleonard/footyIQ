import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]

sys.path.append(str(project_root))

import streamlit as st
import pandas as pd

from analysis.analysis_engine import AnalyticsEngine
from analysis.rankings_engine import RankingsEngine
from analysis.matchup_engine import MatchupEngine


# ===========================================================
# PAGE CONFIG
# ===========================================================

st.set_page_config(
    page_title="Fantasy League Analytics",
    page_icon="📊",
    layout="wide"
)


# ===========================================================
# CONFIG
# ===========================================================

DATA_PATH = "data/raw/2026/teams.parquet"


# ===========================================================
# LOAD ANALYTICS
# ===========================================================

@st.cache_data
def load_analytics():

    # ------------------------------------------------------
    # INITIALIZE ENGINES
    # ------------------------------------------------------

    analytics_engine = AnalyticsEngine(
        DATA_PATH
    )

    rankings_engine = RankingsEngine()

    matchup_engine = MatchupEngine()

    # ------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------

    analytics_engine.load_data()

    # ------------------------------------------------------
    # BUILD ANALYTICS
    # ------------------------------------------------------

    season = analytics_engine.build_analytics(
        analytics_engine.df
    )

    recent = analytics_engine.build_analytics(
        analytics_engine.recent_df
    )

    # ------------------------------------------------------
    # RECENT FORM
    # ------------------------------------------------------

    recent_form_change = (
        analytics_engine.compute_recent_form_change(
            season["averages"],
            recent["averages"]
        )
    )

    # ------------------------------------------------------
    # STRENGTHS / WEAKNESSES
    # ------------------------------------------------------

    profiles = (
        analytics_engine.identify_strengths_weaknesses(
            season["ranks"]
        )
    )

    # ------------------------------------------------------
    # POWER RANKINGS
    # ------------------------------------------------------

    power_rankings = (
        rankings_engine.compute_power_rankings(
            season["percentiles"],
            season["win_rates"],
            season["volatility"]
        )
    )

    # ------------------------------------------------------
    # CATEGORY LEADERBOARDS
    # ------------------------------------------------------

    leaderboards = (
        rankings_engine.build_category_leaderboards(
            season
        )
    )

    return {
        "season": season,
        "recent": recent,
        "recent_form_change": recent_form_change,
        "profiles": profiles,
        "power_rankings": power_rankings,
        "leaderboards": leaderboards,
        "matchup_engine": matchup_engine
    }


# ===========================================================
# LOAD APP DATA
# ===========================================================

data = load_analytics()

season = data["season"]

recent = data["recent"]

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

teams = sorted(
    season["averages"].index.tolist()
)


# ===========================================================
# SIDEBAR NAVIGATION
# ===========================================================

st.sidebar.title(
    "Fantasy Analytics"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Matchup View",
        "Team Analysis",
        "Category Leaderboards",
        "Power Rankings"
    ]
)


# ===========================================================
# MATCHUP VIEW
# ===========================================================

if page == "Matchup View":

    st.title("Head-to-Head Matchup")

    # ------------------------------------------------------
    # TEAM SELECTORS
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # BUILD MATCHUP
    # ------------------------------------------------------

    matchup = (
        matchup_engine.build_head_to_head(
            team_a,
            team_b,
            season,
            recent_form_change
        )
    )

    projected_score = matchup[
        "projected_score"
    ]

    comparison_table = matchup[
        "comparison_table"
    ]

    # ------------------------------------------------------
    # MATCHUP SUMMARY
    # ------------------------------------------------------

    st.subheader("Matchup Summary")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:

        st.metric(
            label=f"{team_a} Projected Categories",
            value=projected_score[team_a]
        )

    with summary_col2:

        st.metric(
            label=f"{team_b} Projected Categories",
            value=projected_score[team_b]
        )

    # ------------------------------------------------------
    # CATEGORY COMPARISON
    # ------------------------------------------------------

    st.subheader("Category Comparison")

    st.dataframe(
        comparison_table,
        use_container_width=True
    )


# ===========================================================
# TEAM ANALYSIS
# ===========================================================

elif page == "Team Analysis":

    st.title("Team Analysis")

    # ------------------------------------------------------
    # TEAM SELECTOR
    # ------------------------------------------------------

    selected_team = st.selectbox(
        "Select Team",
        teams
    )

    # ------------------------------------------------------
    # POWER RANKING
    # ------------------------------------------------------

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
                2
            )
        )

    # ------------------------------------------------------
    # STRENGTHS / WEAKNESSES
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # CATEGORY BREAKDOWN
    # ------------------------------------------------------

    st.subheader(
        "Category Breakdown"
    )

    rows = []

    for category in season[
        "averages"
    ].columns:

        rows.append({

            "Category": category,

            "Rank": season[
                "ranks"
            ].loc[
                selected_team,
                category
            ],

            "Average": season[
                "averages"
            ].loc[
                selected_team,
                category
            ],

            "Form vs Avg %": round(
                recent_form_change.loc[
                    selected_team,
                    category
                ],
                1
            ),

            "Win Rate %": season[
                "win_rates"
            ].loc[
                selected_team,
                category
            ],

            "Volatility %": season[
                "volatility"
            ].loc[
                selected_team,
                category
            ]
        })

    report_df = pd.DataFrame(rows)

    st.dataframe(
        report_df,
        use_container_width=True
    )


# ===========================================================
# CATEGORY LEADERBOARDS
# ===========================================================

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

    st.dataframe(
        leaderboard,
        use_container_width=True
    )


# ===========================================================
# POWER RANKINGS
# ===========================================================

elif page == "Power Rankings":

    st.title("Overall Power Rankings")

    st.dataframe(
        power_rankings.round(2),
        use_container_width=True
    )