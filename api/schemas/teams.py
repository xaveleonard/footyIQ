from pydantic import BaseModel


class CategoryStat(BaseModel):
    category: str
    average: float
    rank: int
    win_rate: float
    volatility: float
    form_change: float


class TeamDetail(BaseModel):
    team_name: str
    power_rank: int
    power_score: float
    strengths: list[str]
    weaknesses: list[str]
    categories: list[CategoryStat]
