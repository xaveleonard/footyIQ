import pandas as pd
import pytest

from analysis.constants import CATEGORY_COLS

# ===========================================================
# FIXTURE SCHEDULE
#
# 4 teams, 2 rounds, round-robin style pairing:
#   Round 1: A vs B, C vs D
#   Round 2: A vs C, B vs D
#
# Only "score" and "kicks" vary meaningfully between rows so
# expected values can be hand-computed; every other category
# is held constant at 50 for every team/round, which deliberately
# exercises the tie-handling paths (equal ranks, 0% win rate).
# ===========================================================

_CONSTANT_CATEGORIES = {
    "handballs": 50,
    "marks": 50,
    "hitouts": 50,
    "tackles": 50,
    "cp": 50,
    "clearances": 50,
    "r50": 50,
    "spoils": 50,
}

_ROWS = [
    # round, matchup, team_name, score, kicks
    (1, 1, "Team A", 100, 200),
    (1, 1, "Team B", 80, 210),
    (1, 2, "Team C", 90, 190),
    (1, 2, "Team D", 70, 220),
    (2, 1, "Team A", 110, 205),
    (2, 1, "Team C", 85, 195),
    (2, 2, "Team B", 95, 215),
    (2, 2, "Team D", 75, 225),
]


@pytest.fixture
def teams_df():
    records = []

    for round_number, matchup, team_name, score, kicks in _ROWS:
        record = {
            "round": round_number,
            "matchup": matchup,
            "team_id": hash(team_name) % 1000,
            "team_name": team_name,
            "score": score,
            "kicks": kicks,
            **_CONSTANT_CATEGORIES,
        }
        records.append(record)

    df = pd.DataFrame(records)

    assert set(CATEGORY_COLS).issubset(df.columns)

    return df


@pytest.fixture
def teams_parquet_path(tmp_path, teams_df):
    path = tmp_path / "teams.parquet"
    teams_df.to_parquet(path, index=False)
    return path
