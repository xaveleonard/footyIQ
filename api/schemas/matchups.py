from typing import Literal, Optional

from pydantic import BaseModel


class CategoryComparison(BaseModel):
    category: str
    team_a_avg: float
    team_a_rank: int
    # None when a team's category mean is 0 - the underlying % calculations
    # (coefficient of variation, % change from a 0 baseline) are undefined
    team_a_form: Optional[float]
    team_a_volatility: Optional[float]
    team_b_avg: float
    team_b_rank: int
    team_b_form: Optional[float]
    team_b_volatility: Optional[float]
    projected_winner: Literal["team_a", "team_b", "tie"]


class HeadToHeadResponse(BaseModel):
    team_a: str
    team_b: str
    team_a_score: int
    team_b_score: int
    categories: list[CategoryComparison]


class RoundResult(BaseModel):
    round: int
    team_a_result: Literal["W", "L", "D"]
    team_a_score: int
    team_b_score: int
    team_b_result: Literal["W", "L", "D"]


class MatchupSummary(BaseModel):
    team_a_wins: int
    team_b_wins: int
    draws: int
    team_a_win_pct: float
    team_b_win_pct: float


class MatchupHistoryResponse(BaseModel):
    team_a: str
    team_b: str
    team_a_rounds: list[dict]
    team_b_rounds: list[dict]
    rounds: list[RoundResult]
    summary: MatchupSummary
