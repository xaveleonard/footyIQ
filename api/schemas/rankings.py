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
    volatility: float
