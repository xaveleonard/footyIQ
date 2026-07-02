def test_list_teams_returns_sorted_names(client):
    response = client.get("/teams")

    assert response.status_code == 200
    assert response.json() == ["Team A", "Team B", "Team C", "Team D"]


def test_get_team_detail(client):
    response = client.get("/teams/Team A")

    assert response.status_code == 200
    body = response.json()

    assert body["team_name"] == "Team A"

    score_stat = next(c for c in body["categories"] if c["category"] == "score")
    assert score_stat["average"] == 105.0
    assert score_stat["rank"] == 1


def test_get_team_detail_unknown_team_returns_404(client):
    response = client.get("/teams/Not A Real Team")

    assert response.status_code == 404
