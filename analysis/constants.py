import pandas as pd

# ===========================================================
# CATEGORY COLUMNS
# ===========================================================

CATEGORY_COLS = [
    "score",
    "kicks",
    "handballs",
    "marks",
    "hitouts",
    "tackles",
    "cp",
    "clearances",
    "r50",
    "spoils"
]

RECENT_FORM_ROUNDS = 4

# window size for the "Last 3 Rounds" toggle on Power Rankings / Leaderboards
RANKINGS_WINDOW_ROUNDS = 3

# last round of the regular season - the Matchups tab is capped to this,
# since finals rounds have uneven participation (not every team plays every
# round), which breaks both the round-by-round pairing in
# MatchupEngine.build_round_matchup_history and would skew the averages/ranks
# feeding the projected head-to-head comparison. Bump this next season.
REGULAR_SEASON_END_ROUND = 20

# ===========================================================
# CATEGORY WEIGHTS
# ===========================================================

CATEGORY_WEIGHTS = {
    "score": 3,
    "spoils": 2,
    "kicks": 1,
    "handballs": 1,
    "marks": 1,
    "hitouts": 1,
    "tackles": 1,
    "cp": 1,
    "clearances": 1,
    "r50": 1
}

WEIGHT_SERIES = pd.Series(CATEGORY_WEIGHTS)

TOTAL_WEIGHT = WEIGHT_SERIES.sum()

# ===========================================================
# PLAYER DATA (deferred)
# ===========================================================

# TODO: players.parquet needs player_id -> team/round ownership mapping
# before it can be exposed via API (planned for a future feature)
