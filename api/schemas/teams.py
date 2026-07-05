from typing import Optional

from pydantic import BaseModel


class CategoryStat(BaseModel):
    category: str
    average: float
    rank: int
    win_rate: float
    # None when the mean for this category is 0 (coefficient of variation /
    # % change from a 0 baseline is mathematically undefined, not a real number)
    volatility: Optional[float]
    form_change: Optional[float]


class TeamDetail(BaseModel):
    team_name: str
    power_rank: int
    power_score: float
    strengths: list[str]
    weaknesses: list[str]
    categories: list[CategoryStat]
