from __future__ import annotations

import math

import numpy as np
import pandas as pd

from analysis.constants import CATEGORY_COLS

# ===========================================================
# GENERIC HELPERS
#
# Route handlers never call .to_dict()/.to_json() directly -
# everything funnels through here so pandas/numpy internals
# never leak into the JSON response.
# ===========================================================


def _clean_value(value):
    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        value = float(value)
        return None if math.isnan(value) else value

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, float) and math.isnan(value):
        return None

    return value


def _clean_record(record: dict) -> dict:
    return {key: _clean_value(value) for key, value in record.items()}


def df_records(df: pd.DataFrame) -> list[dict]:
    records = df.reset_index(drop=True).to_dict(orient="records")
    return [_clean_record(record) for record in records]


# ===========================================================
# TEAMS
# ===========================================================


def build_team_detail(bundle: dict, team_name: str) -> dict | None:
    season = bundle["season"]

    if team_name not in season["averages"].index:
        return None

    power_rankings = bundle["windows"]["season"]["power_rankings"]
    power_row = power_rankings[power_rankings["Team"] == team_name].iloc[0]

    profile = bundle["profiles"][team_name]

    categories = []
    for category in CATEGORY_COLS:
        categories.append(_clean_record({
            "category": category,
            "average": season["averages"].loc[team_name, category],
            "rank": season["ranks"].loc[team_name, category],
            "win_rate": season["win_rates"].loc[team_name, category],
            "volatility": season["volatility"].loc[team_name, category],
            "form_change": bundle["recent_form_change"].loc[team_name, category],
        }))

    return _clean_record({
        "team_name": team_name,
        "power_rank": power_row["Power Rank"],
        "power_score": power_row["Power Score"],
        "strengths": profile["strengths"],
        "weaknesses": profile["weaknesses"],
        "categories": categories,
    })


# ===========================================================
# RANKINGS / LEADERBOARDS
# ===========================================================


def build_power_rankings_response(bundle: dict, window: str = "season") -> list[dict]:
    df = bundle["windows"][window]["power_rankings"].rename(columns={
        "Power Rank": "power_rank",
        "Team": "team_name",
        "Power Score": "power_score",
    })
    return df_records(df)


def build_leaderboard_response(
    bundle: dict, category: str, window: str = "season"
) -> list[dict] | None:
    leaderboards = bundle["windows"][window]["leaderboards"]

    if category not in leaderboards:
        return None

    df = leaderboards[category].rename(columns={
        "Rank": "rank",
        "Team": "team_name",
        "Average": "average",
        "Win Rate %": "win_rate",
        "Volatility %": "volatility",
    })
    return df_records(df)


def build_all_leaderboards_response(bundle: dict, window: str = "season") -> dict[str, list[dict]]:
    return {
        category: build_leaderboard_response(bundle, category, window)
        for category in bundle["windows"][window]["leaderboards"]
    }


# ===========================================================
# LEAGUE RECORDS
# ===========================================================


def build_league_records_response(bundle: dict) -> list[dict]:
    records = bundle["league_records"]

    return [
        _clean_record({
            "category": category,
            "value": record["value"],
            "holders": [_clean_record(holder) for holder in record["holders"]],
        })
        for category, record in records.items()
    ]


# ===========================================================
# MATCHUPS
#
# MatchupEngine produces dynamically-named columns like
# f"{team_a} Avg" and a literal "Tie" winner value - fine for a
# pandas Styler, bad for typed JSON. Everything below normalizes
# that into stable team_a_*/team_b_* keys so the frontend has one
# fixed shape regardless of which two teams were selected.
# ===========================================================


def build_head_to_head_response(bundle: dict, team_a: str, team_b: str) -> dict:
    matchup_engine = bundle["matchup_engine"]

    result = matchup_engine.build_head_to_head(
        team_a, team_b, bundle["season"], bundle["recent_form_change"]
    )

    categories = []
    for _, row in result["comparison_table"].iterrows():
        winner = row["Projected Winner"]

        if winner == team_a:
            normalized_winner = "team_a"
        elif winner == team_b:
            normalized_winner = "team_b"
        else:
            normalized_winner = "tie"

        categories.append(_clean_record({
            "category": row["Category"],
            "team_a_avg": row[f"{team_a} Avg"],
            "team_a_rank": row[f"{team_a} Rank"],
            "team_a_form": row[f"{team_a} Form"],
            "team_a_volatility": row[f"{team_a} Vol"],
            "team_b_avg": row[f"{team_b} Avg"],
            "team_b_rank": row[f"{team_b} Rank"],
            "team_b_form": row[f"{team_b} Form"],
            "team_b_volatility": row[f"{team_b} Vol"],
            "projected_winner": normalized_winner,
        }))

    return {
        "team_a": team_a,
        "team_b": team_b,
        "team_a_score": int(result["projected_score"][team_a]),
        "team_b_score": int(result["projected_score"][team_b]),
        "categories": categories,
    }


def build_matchup_history_response(bundle: dict, team_a: str, team_b: str) -> dict:
    matchup_engine = bundle["matchup_engine"]

    history = matchup_engine.build_round_matchup_history(team_a, team_b, bundle["raw_df"])

    rounds = []
    for _, row in history["head_to_head_table"].iterrows():
        rounds.append(_clean_record({
            "round": row["Round"],
            "team_a_result": row[f"{team_a} Result"],
            "team_a_score": row[f"{team_a} Score"],
            "team_b_score": row[f"{team_b} Score"],
            "team_b_result": row[f"{team_b} Result"],
        }))

    return {
        "team_a": team_a,
        "team_b": team_b,
        "team_a_rounds": df_records(history["team_a_rounds"]),
        "team_b_rounds": df_records(history["team_b_rounds"]),
        "rounds": rounds,
        "summary": _clean_record(history["summary"]),
    }
