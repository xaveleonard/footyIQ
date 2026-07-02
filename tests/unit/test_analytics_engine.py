import statistics

import pandas as pd
import pytest

from analysis.analytics_engine import AnalyticsEngine


@pytest.fixture
def engine():
    return AnalyticsEngine(data_path="unused")


# ===========================================================
# TEAM AVERAGES
# ===========================================================

def test_compute_team_averages(engine, teams_df):
    averages = engine.compute_team_averages(teams_df)

    assert averages.loc["Team A", "score"] == 105.0
    assert averages.loc["Team B", "score"] == 87.5
    assert averages.loc["Team C", "score"] == 87.5
    assert averages.loc["Team D", "score"] == 72.5

    assert averages.loc["Team A", "kicks"] == 202.5
    assert averages.loc["Team D", "kicks"] == 222.5

    # constant categories should average to the constant value for every team
    for team in ["Team A", "Team B", "Team C", "Team D"]:
        assert averages.loc[team, "handballs"] == 50.0


# ===========================================================
# CATEGORY RANKS (ties use method="min")
# ===========================================================

def test_compute_category_ranks_with_ties(engine, teams_df):
    averages = engine.compute_team_averages(teams_df)
    ranks = engine.compute_category_ranks(averages)

    # score: A=105 (1st), B & C tied at 87.5 (both 2nd, skip to 4th), D=72.5 (4th)
    assert ranks.loc["Team A", "score"] == 1
    assert ranks.loc["Team B", "score"] == 2
    assert ranks.loc["Team C", "score"] == 2
    assert ranks.loc["Team D", "score"] == 4

    # kicks: no ties, D > B > A > C
    assert ranks.loc["Team D", "kicks"] == 1
    assert ranks.loc["Team B", "kicks"] == 2
    assert ranks.loc["Team A", "kicks"] == 3
    assert ranks.loc["Team C", "kicks"] == 4

    # fully-tied constant category: everyone gets rank 1
    for team in ["Team A", "Team B", "Team C", "Team D"]:
        assert ranks.loc[team, "handballs"] == 1


# ===========================================================
# PERCENTILES
# ===========================================================

def test_compute_percentiles_with_ties(engine, teams_df):
    averages = engine.compute_team_averages(teams_df)
    percentiles = engine.compute_percentiles(averages)

    assert percentiles.loc["Team D", "score"] == 25.0
    assert percentiles.loc["Team B", "score"] == 62.5
    assert percentiles.loc["Team C", "score"] == 62.5
    assert percentiles.loc["Team A", "score"] == 100.0

    assert percentiles.loc["Team C", "kicks"] == 25.0
    assert percentiles.loc["Team A", "kicks"] == 50.0
    assert percentiles.loc["Team B", "kicks"] == 75.0
    assert percentiles.loc["Team D", "kicks"] == 100.0

    # fully tied column: average rank (1+2+3+4)/4 = 2.5 -> 62.5th percentile for all
    for team in ["Team A", "Team B", "Team C", "Team D"]:
        assert percentiles.loc[team, "handballs"] == 62.5


# ===========================================================
# VOLATILITY
# ===========================================================

def test_compute_volatility(engine, teams_df):
    volatility = engine.compute_volatility(teams_df)

    expected = {
        "Team A": statistics.stdev([100, 110]) / statistics.mean([100, 110]) * 100,
        "Team B": statistics.stdev([80, 95]) / statistics.mean([80, 95]) * 100,
        "Team C": statistics.stdev([90, 85]) / statistics.mean([90, 85]) * 100,
        "Team D": statistics.stdev([70, 75]) / statistics.mean([70, 75]) * 100,
    }

    for team, expected_volatility in expected.items():
        assert volatility.loc[team, "score"] == pytest.approx(expected_volatility, abs=0.01)

    # constant category: zero variance -> 0% volatility
    for team in ["Team A", "Team B", "Team C", "Team D"]:
        assert volatility.loc[team, "handballs"] == 0.0


# ===========================================================
# CATEGORY WIN RATES
# ===========================================================

def test_compute_category_win_rates(engine, teams_df):
    win_rates = engine.compute_category_win_rates(teams_df)

    # score: A wins both its games (2/2=100%), B wins 1/2, C wins 1/2, D wins 0/2
    assert win_rates.loc["Team A", "score"] == 100.0
    assert win_rates.loc["Team B", "score"] == 50.0
    assert win_rates.loc["Team C", "score"] == 50.0
    assert win_rates.loc["Team D", "score"] == 0.0

    # kicks: A 1/2, B 1/2, C 0/2, D 2/2
    assert win_rates.loc["Team A", "kicks"] == 50.0
    assert win_rates.loc["Team B", "kicks"] == 50.0
    assert win_rates.loc["Team C", "kicks"] == 0.0
    assert win_rates.loc["Team D", "kicks"] == 100.0

    # constant categories are always tied -> nobody wins them
    for team in ["Team A", "Team B", "Team C", "Team D"]:
        assert win_rates.loc[team, "handballs"] == 0.0


# ===========================================================
# RECENT FORM CHANGE (pure formula, independent of load_data windowing)
# ===========================================================

def test_compute_recent_form_change(engine):
    season_averages = pd.DataFrame({"score": [100.0, 50.0]}, index=["Team A", "Team B"])
    recent_averages = pd.DataFrame({"score": [110.0, 40.0]}, index=["Team A", "Team B"])

    change = engine.compute_recent_form_change(season_averages, recent_averages)

    assert change.loc["Team A", "score"] == pytest.approx(10.0)
    assert change.loc["Team B", "score"] == pytest.approx(-20.0)


# ===========================================================
# STRENGTHS / WEAKNESSES (boundary behaviour)
# ===========================================================

def test_identify_strengths_weaknesses_boundaries(engine):
    # rank <= 4 is a strength, rank >= 13 is a weakness (thresholds tuned for
    # a larger league; a small ranks table lets us hit both boundaries directly)
    ranks = pd.DataFrame(
        {
            "score": [4, 5, 12, 13],
            "kicks": [1, 8, 8, 16],
        },
        index=["Team A", "Team B", "Team C", "Team D"],
    )

    profiles = engine.identify_strengths_weaknesses(ranks)

    assert "score" in profiles["Team A"]["strengths"]
    assert "score" not in profiles["Team B"]["strengths"]
    assert "score" not in profiles["Team B"]["weaknesses"]
    assert "score" not in profiles["Team C"]["weaknesses"]
    assert "score" in profiles["Team D"]["weaknesses"]

    assert "kicks" in profiles["Team A"]["strengths"]
    assert "kicks" in profiles["Team D"]["weaknesses"]


# ===========================================================
# LOAD DATA (parquet round-trip + recent-window slicing)
# ===========================================================

def test_load_data_reads_parquet(teams_parquet_path, teams_df):
    engine = AnalyticsEngine(data_path=teams_parquet_path)
    engine.load_data()

    assert len(engine.df) == len(teams_df)
    # RECENT_FORM_ROUNDS=4 but the fixture only has 2 rounds, so the
    # "recent" window covers every row that exists
    assert len(engine.recent_df) == len(engine.df)


def test_load_data_recent_window_excludes_old_rounds(tmp_path, engine):
    # 5 rounds of a single team so the RECENT_FORM_ROUNDS=4 window
    # excludes round 1 (min_round = 5 - 4 + 1 = 2)
    rows = []
    for round_number in range(1, 6):
        rows.append({
            "round": round_number,
            "matchup": 1,
            "team_id": 1,
            "team_name": "Team A",
            "score": 100,
            "kicks": 200,
            "handballs": 50, "marks": 50, "hitouts": 50, "tackles": 50,
            "cp": 50, "clearances": 50, "r50": 50, "spoils": 50,
        })

    path = tmp_path / "teams.parquet"
    pd.DataFrame(rows).to_parquet(path, index=False)

    engine.data_path = path
    engine.load_data()

    assert sorted(engine.df["round"].unique()) == [1, 2, 3, 4, 5]
    assert sorted(engine.recent_df["round"].unique()) == [2, 3, 4, 5]


# ===========================================================
# BUILD ANALYTICS (structural check)
# ===========================================================

def test_build_analytics_returns_expected_keys(engine, teams_df):
    result = engine.build_analytics(teams_df)

    assert set(result.keys()) == {"averages", "ranks", "percentiles", "win_rates", "volatility"}
    assert result["averages"].loc["Team A", "score"] == 105.0
