import pandas as pd
import pytest

from analysis.matchup_engine import MatchupEngine


@pytest.fixture
def engine():
    return MatchupEngine()


# ===========================================================
# HEAD TO HEAD (projected, rank-based)
# ===========================================================

def test_build_head_to_head_projected_scores_and_ties(engine):
    # score (weight 3): Team A ranked better -> Team A wins
    # kicks (weight 1): Team B ranked better -> Team B wins
    # spoils (weight 2): tied rank -> split evenly
    season = {
        "averages": pd.DataFrame(
            {"score": [110.0, 90.0], "kicks": [190.0, 210.0], "spoils": [20.0, 20.0]},
            index=["Team A", "Team B"],
        ),
        "ranks": pd.DataFrame(
            {"score": [1, 2], "kicks": [2, 1], "spoils": [1, 1]},
            index=["Team A", "Team B"],
        ),
        "volatility": pd.DataFrame(
            {"score": [5.0, 8.0], "kicks": [3.0, 4.0], "spoils": [2.0, 2.0]},
            index=["Team A", "Team B"],
        ),
    }
    recent_form_change = pd.DataFrame(
        {"score": [5.0, -3.0], "kicks": [0.0, 0.0], "spoils": [2.5, -2.5]},
        index=["Team A", "Team B"],
    )

    result = engine.build_head_to_head("Team A", "Team B", season, recent_form_change)

    # score(3) + spoils tie(2/2=1) = 4 for A; kicks(1) + spoils tie(1) = 2 for B
    assert result["projected_score"]["Team A"] == 4
    assert result["projected_score"]["Team B"] == 2

    table = result["comparison_table"].set_index("Category")
    assert table.loc["score", "Projected Winner"] == "Team A"
    assert table.loc["kicks", "Projected Winner"] == "Team B"
    assert table.loc["spoils", "Projected Winner"] == "Tie"


# ===========================================================
# ROUND-BY-ROUND MATCHUP HISTORY
# ===========================================================

def _round_row(round_number, team_name, score, spoils, rest=50):
    row = {
        "round": round_number,
        "team_name": team_name,
        "score": score,
        "spoils": spoils,
        "kicks": rest, "handballs": rest, "marks": rest, "hitouts": rest,
        "tackles": rest, "cp": rest, "clearances": rest, "r50": rest,
    }
    return row


def test_build_round_matchup_history_weighted_results(engine):
    raw_df = pd.DataFrame([
        # round 1: A wins on score(3) + spoils(2) while the 8 tied categories
        # split evenly (4 each) -> A=9, B=4
        _round_row(1, "Team A", score=100, spoils=30),
        _round_row(1, "Team B", score=80, spoils=20),
        # round 2: B wins score + spoils -> B=9, A=4
        _round_row(2, "Team A", score=70, spoils=10),
        _round_row(2, "Team B", score=90, spoils=40),
        # round 3: every category tied -> a dead-even draw
        _round_row(3, "Team A", score=85, spoils=25),
        _round_row(3, "Team B", score=85, spoils=25),
    ])

    history = engine.build_round_matchup_history("Team A", "Team B", raw_df)

    results = history["head_to_head_table"].set_index("Round")

    assert results.loc[1, "Team A Result"] == "W"
    assert results.loc[1, "Team A Score"] == 9
    assert results.loc[1, "Team B Score"] == 4
    assert results.loc[1, "Team B Result"] == "L"

    assert results.loc[2, "Team A Result"] == "L"
    assert results.loc[2, "Team B Result"] == "W"

    assert results.loc[3, "Team A Result"] == "D"
    assert results.loc[3, "Team B Result"] == "D"

    summary = history["summary"]
    assert summary["team_a_wins"] == 1
    assert summary["team_b_wins"] == 1
    assert summary["draws"] == 1
    assert summary["team_a_win_pct"] == pytest.approx(33.3)
    assert summary["team_b_win_pct"] == pytest.approx(33.3)

    assert list(history["team_a_rounds"]["score"]) == [100, 70, 85]
