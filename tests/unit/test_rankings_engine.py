import pandas as pd
import pytest

from analysis.constants import CATEGORY_COLS, TOTAL_WEIGHT
from analysis.rankings_engine import RankingsEngine


@pytest.fixture
def engine():
    return RankingsEngine()


def _uniform_row(value):
    return {category: value for category in CATEGORY_COLS}


# ===========================================================
# WEIGHTED WIN SCORE
# ===========================================================

def test_weighted_win_score(engine):
    win_rates = pd.DataFrame(
        {
            "Team X": {**_uniform_row(0), "score": 100, "spoils": 50},
            "Team Y": _uniform_row(50),
        }
    ).T

    scores = engine.weighted_win_score(win_rates)

    # score(100*3) + spoils(50*2) + eight other cats at 0 = 400, /13 total weight
    assert scores["Team X"] == pytest.approx(400 / TOTAL_WEIGHT)
    # winning exactly half of everything uniformly -> a flat 50, regardless of weights
    assert scores["Team Y"] == pytest.approx(50.0)


# ===========================================================
# POWER RANKINGS
# ===========================================================

def test_compute_power_rankings_orders_by_score(engine):
    win_rates = pd.DataFrame(
        {
            "Team X": {**_uniform_row(0), "score": 100, "spoils": 50},
            "Team Y": _uniform_row(50),
        }
    ).T
    percentiles = pd.DataFrame(
        {"Team X": _uniform_row(80), "Team Y": _uniform_row(40)}
    ).T
    volatility = pd.DataFrame(
        {"Team X": _uniform_row(10), "Team Y": _uniform_row(30)}
    ).T

    rankings = engine.compute_power_rankings(percentiles, win_rates, volatility)

    x_score = (400 / TOTAL_WEIGHT) * 0.50 + 80 * 0.30 + (100 - 10) * 0.20
    y_score = 50.0 * 0.50 + 40 * 0.30 + (100 - 30) * 0.20

    x_row = rankings[rankings["Team"] == "Team X"].iloc[0]
    y_row = rankings[rankings["Team"] == "Team Y"].iloc[0]

    assert x_row["Power Score"] == pytest.approx(x_score)
    assert y_row["Power Score"] == pytest.approx(y_score)

    assert x_row["Power Rank"] == 1
    assert y_row["Power Rank"] == 2
    # sorted ascending by rank
    assert rankings["Power Rank"].tolist() == sorted(rankings["Power Rank"].tolist())


# ===========================================================
# CATEGORY LEADERBOARDS
# ===========================================================

def test_build_category_leaderboards_structure_and_sort(engine):
    season = {
        "averages": pd.DataFrame(
            {"score": [120.0, 90.0], "kicks": [200.0, 210.0]},
            index=["Team A", "Team B"],
        ),
        "ranks": pd.DataFrame(
            {"score": [1, 2], "kicks": [2, 1]},
            index=["Team A", "Team B"],
        ),
        "win_rates": pd.DataFrame(
            {"score": [75.0, 25.0], "kicks": [40.0, 60.0]},
            index=["Team A", "Team B"],
        ),
        "volatility": pd.DataFrame(
            {"score": [5.0, 8.0], "kicks": [3.0, 4.0]},
            index=["Team A", "Team B"],
        ),
    }

    leaderboards = engine.build_category_leaderboards(season)

    assert set(leaderboards.keys()) == {"score", "kicks"}

    score_board = leaderboards["score"]
    assert list(score_board["Team"]) == ["Team A", "Team B"]
    assert list(score_board["Rank"]) == [1, 2]
    assert score_board.iloc[0]["Average"] == 120.0

    kicks_board = leaderboards["kicks"]
    # kicks ranks are reversed (Team B is rank 1) -> leaderboard should re-sort
    assert list(kicks_board["Team"]) == ["Team B", "Team A"]
    assert list(kicks_board["Rank"]) == [1, 2]
