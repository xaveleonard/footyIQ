import pytest


def test_power_rankings_covers_all_teams_sorted(client):
    response = client.get("/rankings/power")

    assert response.status_code == 200
    body = response.json()

    assert len(body) == 4
    assert {entry["team_name"] for entry in body} == {"Team A", "Team B", "Team C", "Team D"}
    assert [entry["power_rank"] for entry in body] == sorted(entry["power_rank"] for entry in body)


def test_leaderboard_for_score(client):
    response = client.get("/rankings/leaderboards/score")

    assert response.status_code == 200
    body = response.json()

    top = next(entry for entry in body if entry["rank"] == 1)
    assert top["team_name"] == "Team A"
    assert top["average"] == 105.0


def test_leaderboard_unknown_category_returns_404(client):
    response = client.get("/rankings/leaderboards/not_a_category")

    assert response.status_code == 404


def test_all_leaderboards_covers_every_category(client):
    response = client.get("/rankings/leaderboards")

    assert response.status_code == 200
    body = response.json()

    assert "score" in body
    assert "kicks" in body
    assert len(body["score"]) == 4


# ===========================================================
# LAST-3-ROUNDS WINDOW
#
# Uses a dedicated 5-round fixture (not the shared 2-round
# teams_df) where a team's fortunes reverse partway through the
# season, so "season" and "last3" produce genuinely different
# rankings - proving the window filter actually changes the
# result, not just its magnitude.
# ===========================================================


def _row(round_number, matchup, team_name, score):
    rest = 50
    return {
        "round": round_number,
        "matchup": matchup,
        "team_id": hash(team_name) % 1000,
        "team_name": team_name,
        "score": score,
        "kicks": rest, "handballs": rest, "marks": rest, "hitouts": rest,
        "tackles": rest, "cp": rest, "clearances": rest, "r50": rest, "spoils": rest,
    }


@pytest.fixture
def windowed_client(tmp_path):
    import pandas as pd
    from fastapi.testclient import TestClient

    from api.dependencies import build_analytics_bundle, get_analytics_bundle
    from api.main import app

    rows = []
    # Team E dominates rounds 1-4, Team F dominates rounds 5-7. The
    # last-3 window (min_round = 7 - 3 + 1 = 5) falls entirely within
    # F's dominant stretch, while E still has more total dominant
    # rounds (4 vs 3) so it wins on season average - season favors E,
    # last3 favors F.
    for round_number, (e_score, f_score) in enumerate(
        [(100, 10), (100, 10), (100, 10), (100, 10), (10, 100), (10, 100), (10, 100)], start=1
    ):
        rows.append(_row(round_number, 1, "Team E", e_score))
        rows.append(_row(round_number, 1, "Team F", f_score))
        rows.append(_row(round_number, 2, "Team G", 50))
        rows.append(_row(round_number, 2, "Team H", 50))

    path = tmp_path / "teams.parquet"
    pd.DataFrame(rows).to_parquet(path, index=False)

    bundle = build_analytics_bundle(str(path))
    app.dependency_overrides[get_analytics_bundle] = lambda: bundle

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_leaderboard_window_last3_differs_from_season(windowed_client):
    season = windowed_client.get("/rankings/leaderboards/score", params={"window": "season"})
    last3 = windowed_client.get("/rankings/leaderboards/score", params={"window": "last3"})

    assert season.status_code == 200
    assert last3.status_code == 200

    season_top = next(e for e in season.json() if e["rank"] == 1)
    last3_top = next(e for e in last3.json() if e["rank"] == 1)

    # compute_team_averages() rounds to 2 decimal places
    assert season_top["team_name"] == "Team E"
    assert season_top["average"] == pytest.approx(round((100 * 4 + 10 * 3) / 7, 2))

    assert last3_top["team_name"] == "Team F"
    assert last3_top["average"] == pytest.approx(100.0)


def test_power_rankings_window_last3_differs_from_season(windowed_client):
    season = windowed_client.get("/rankings/power", params={"window": "season"})
    last3 = windowed_client.get("/rankings/power", params={"window": "last3"})

    season_top = next(e for e in season.json() if e["power_rank"] == 1)
    last3_top = next(e for e in last3.json() if e["power_rank"] == 1)

    assert season_top["team_name"] == "Team E"
    assert last3_top["team_name"] == "Team F"


def test_window_rejects_invalid_value(client):
    response = client.get("/rankings/power", params={"window": "not_a_window"})

    assert response.status_code == 422


# ===========================================================
# LEAGUE RECORDS
# ===========================================================


def test_league_records_single_holder(client):
    response = client.get("/rankings/records")

    assert response.status_code == 200
    body = response.json()

    score_record = next(r for r in body if r["category"] == "score")
    assert score_record["value"] == 110
    assert score_record["holders"] == [{"team_name": "Team A", "round": 2}]


def test_league_records_shows_every_tied_holder(client):
    response = client.get("/rankings/records")

    body = response.json()
    handballs_record = next(r for r in body if r["category"] == "handballs")

    assert handballs_record["value"] == 50
    assert len(handballs_record["holders"]) == 8


# ===========================================================
# ZERO-MEAN VOLATILITY (regression: a team averaging 0 in a
# category - e.g. zero hitouts across a small round window -
# makes the coefficient of variation 0/0, which previously
# reached the API as a bare NaN and crashed with a
# ResponseValidationError because the schema required a float)
# ===========================================================


@pytest.fixture
def zero_mean_client(tmp_path):
    import pandas as pd
    from fastapi.testclient import TestClient

    from api.dependencies import build_analytics_bundle, get_analytics_bundle
    from api.main import app

    def row(round_number, matchup, team_name, hitouts):
        rest = 50
        return {
            "round": round_number, "matchup": matchup, "team_id": hash(team_name) % 1000,
            "team_name": team_name, "score": rest, "kicks": rest, "handballs": rest,
            "marks": rest, "hitouts": hitouts, "tackles": rest, "cp": rest,
            "clearances": rest, "r50": rest, "spoils": rest,
        }

    rows = [
        row(1, 1, "Team P", 0), row(1, 1, "Team Q", 20),
        row(1, 2, "Team R", 15), row(1, 2, "Team S", 25),
        row(2, 1, "Team P", 0), row(2, 1, "Team Q", 22),
        row(2, 2, "Team R", 18), row(2, 2, "Team S", 19),
    ]

    path = tmp_path / "teams.parquet"
    pd.DataFrame(rows).to_parquet(path, index=False)

    bundle = build_analytics_bundle(str(path))
    app.dependency_overrides[get_analytics_bundle] = lambda: bundle

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_leaderboard_handles_zero_mean_volatility(zero_mean_client):
    response = zero_mean_client.get("/rankings/leaderboards/hitouts")

    assert response.status_code == 200
    body = response.json()

    team_p = next(e for e in body if e["team_name"] == "Team P")
    assert team_p["average"] == 0.0
    assert team_p["volatility"] is None

    team_q = next(e for e in body if e["team_name"] == "Team Q")
    assert team_q["volatility"] is not None


def test_team_detail_handles_zero_mean_volatility(zero_mean_client):
    response = zero_mean_client.get("/teams/Team P")

    assert response.status_code == 200
    body = response.json()

    hitouts_stat = next(c for c in body["categories"] if c["category"] == "hitouts")
    assert hitouts_stat["average"] == 0.0
    assert hitouts_stat["volatility"] is None
