from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_analytics_bundle
from api.schemas.rankings import LeaderboardEntry, PowerRankingEntry
from api.serializers import (
    build_all_leaderboards_response,
    build_leaderboard_response,
    build_power_rankings_response,
)

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/power", response_model=list[PowerRankingEntry])
def get_power_rankings(bundle: dict = Depends(get_analytics_bundle)):
    return build_power_rankings_response(bundle)


@router.get("/leaderboards", response_model=dict[str, list[LeaderboardEntry]])
def get_all_leaderboards(bundle: dict = Depends(get_analytics_bundle)):
    return build_all_leaderboards_response(bundle)


@router.get("/leaderboards/{category}", response_model=list[LeaderboardEntry])
def get_leaderboard(category: str, bundle: dict = Depends(get_analytics_bundle)):
    result = build_leaderboard_response(bundle, category)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown category: {category}")

    return result
