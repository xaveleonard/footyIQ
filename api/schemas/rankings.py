from typing import Optional

from pydantic import BaseModel


class PowerRankingEntry(BaseModel):
    power_rank: int
    team_name: str
    power_score: float


class LeaderboardEntry(BaseModel):
    rank: int
    team_name: str
    average: float
    win_rate: float
    # None when a team's mean for this category is 0 (e.g. zero hitouts across
    # every game in a small window) - the coefficient of variation is
    # mathematically undefined (0/0), not a real percentage.
    volatility: Optional[float]


class RecordHolder(BaseModel):
    team_name: str
    round: int


class CategoryRecord(BaseModel):
    category: str
    value: float
    holders: list[RecordHolder]
