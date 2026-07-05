from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import Window, get_analytics_bundle
from api.schemas.rankings import CategoryRecord, LeaderboardEntry, PowerRankingEntry
from api.serializers import (
    build_all_leaderboards_response,
    build_leaderboard_response,
    build_league_records_response,
    build_power_rankings_response,
)

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/power", response_model=list[PowerRankingEntry])
def get_power_rankings(window: Window = "season", bundle: dict = Depends(get_analytics_bundle)):
    return build_power_rankings_response(bundle, window)


@router.get("/leaderboards", response_model=dict[str, list[LeaderboardEntry]])
def get_all_leaderboards(window: Window = "season", bundle: dict = Depends(get_analytics_bundle)):
    return build_all_leaderboards_response(bundle, window)


@router.get("/leaderboards/{category}", response_model=list[LeaderboardEntry])
def get_leaderboard(
    category: str, window: Window = "season", bundle: dict = Depends(get_analytics_bundle)
):
    result = build_leaderboard_response(bundle, category, window)

    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown category: {category}")

    return result


@router.get("/records", response_model=list[CategoryRecord])
def get_league_records(bundle: dict = Depends(get_analytics_bundle)):
    return build_league_records_response(bundle)
