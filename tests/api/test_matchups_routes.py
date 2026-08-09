import pytest


def test_head_to_head_normalizes_dynamic_columns(client):
    response = client.get("/matchups/head-to-head", params={"team_a": "Team A", "team_b": "Team B"})

    assert response.status_code == 200
    body = response.json()

    categories = {c["category"]: c for c in body["categories"]}

    # score: Team A rank 1 vs Team B rank 2 -> Team A wins
    assert categories["score"]["projected_winner"] == "team_a"
    # kicks: Team A rank 3 vs Team B rank 2 -> Team B wins
    assert categories["kicks"]["projected_winner"] == "team_b"
    # every other category is fully tied league-wide -> tie
    assert categories["handballs"]["projected_winner"] == "tie"


def test_head_to_head_same_team_returns_400(client):
    response = client.get("/matchups/head-to-head", params={"team_a": "Team A", "team_b": "Team A"})

    assert response.status_code == 400


def test_head_to_head_unknown_team_returns_404(client):
    response = client.get("/matchups/head-to-head", params={"team_a": "Team A", "team_b": "Nope"})

    assert response.status_code == 404


def test_matchup_history_simulated_rounds(client):
    response = client.get("/matchups/history", params={"team_a": "Team A", "team_b": "Team B"})

    assert response.status_code == 200
    body = response.json()

    # Team A out-scores Team B's same-index round in both simulated rounds
    assert body["summary"]["team_a_wins"] == 2
    assert body["summary"]["team_b_wins"] == 0
    assert body["summary"]["team_a_win_pct"] == 100.0

    assert len(body["team_a_rounds"]) == 2
    assert len(body["team_b_rounds"]) == 2


# ===========================================================
# FINALS EXCLUSION (regression: finals rounds have uneven
# per-team participation - e.g. a bye - which would otherwise
# misalign build_round_matchup_history's chronological-index
# pairing, and skew the season averages/ranks feeding the
# projected comparison, if not excluded)
# ===========================================================


def _row(round_number, matchup, team_name, score):
    rest = 50
    return {
        "round": round_number, "matchup": matchup, "team_id": hash(team_name) % 1000,
        "team_name": team_name, "score": score, "kicks": rest, "handballs": rest,
        "marks": rest, "hitouts": rest, "tackles": rest, "cp": rest,
        "clearances": rest, "r50": rest, "spoils": rest,
    }


@pytest.fixture
def finals_client(tmp_path, monkeypatch):
    import pandas as pd
    from fastapi.testclient import TestClient

    import api.dependencies as dependencies_module
    from api.dependencies import build_analytics_bundle, get_analytics_bundle
    from api.main import app

    # Treat rounds 1-3 as the "regular season" for this test, rounds 4-5 as
    # finals - small numbers so the fixture stays readable, same mechanism
    # as the real REGULAR_SEASON_END_ROUND=20.
    monkeypatch.setattr(dependencies_module, "REGULAR_SEASON_END_ROUND", 3)

    rows = [
        *[_row(r, 1, "Team P", 100) for r in (1, 2, 3)],
        *[_row(r, 1, "Team Q", 50) for r in (1, 2, 3)],
        *[_row(r, 2, "Team R", 50) for r in (1, 2, 3)],
        *[_row(r, 2, "Team S", 50) for r in (1, 2, 3)],
        # round 4 (finals): Team P and Team S have a bye
        _row(4, 1, "Team Q", 200),
        _row(4, 1, "Team R", 50),
        # round 5 (finals): everyone plays, wildly different scores from the
        # "regular season" - if this leaked into the projection or history,
        # it would change the outcome
        _row(5, 1, "Team P", 10),
        _row(5, 1, "Team Q", 200),
        _row(5, 2, "Team R", 50),
        _row(5, 2, "Team S", 50),
    ]

    path = tmp_path / "teams.parquet"
    pd.DataFrame(rows).to_parquet(path, index=False)

    bundle = build_analytics_bundle(str(path))
    app.dependency_overrides[get_analytics_bundle] = lambda: bundle

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_head_to_head_excludes_finals_rounds(finals_client):
    response = finals_client.get(
        "/matchups/head-to-head", params={"team_a": "Team P", "team_b": "Team Q"}
    )

    assert response.status_code == 200
    body = response.json()

    score = next(c for c in body["categories"] if c["category"] == "score")
    # Regular season only: P averages 100, Q averages 50 -> P projected to
    # win. If finals rounds leaked in, Q's finals scores (200, 200) would
    # pull its average well above P's and likely flip this.
    assert score["team_a_avg"] == pytest.approx(100.0)
    assert score["team_b_avg"] == pytest.approx(50.0)
    assert score["projected_winner"] == "team_a"


def test_matchup_history_excludes_finals_rounds(finals_client):
    response = finals_client.get(
        "/matchups/history", params={"team_a": "Team P", "team_b": "Team Q"}
    )

    assert response.status_code == 200
    body = response.json()

    # Only the 3 regular-season rounds, never round 4 or 5 - and Team P's
    # round-4 bye (a shorter row count than Team Q) never gets misaligned
    # against Team Q's round-4/5 finals rows.
    assert len(body["rounds"]) == 3
    assert {r["round"] for r in body["rounds"]} == {1, 2, 3}

    for round_result in body["rounds"]:
        assert round_result["team_a_result"] == "W"
        assert round_result["team_b_result"] == "L"
