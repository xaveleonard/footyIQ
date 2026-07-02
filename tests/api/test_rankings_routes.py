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
