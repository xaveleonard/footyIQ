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
