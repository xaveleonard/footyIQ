from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_analytics_bundle
from api.schemas.matchups import HeadToHeadResponse, MatchupHistoryResponse
from api.serializers import build_head_to_head_response, build_matchup_history_response

router = APIRouter(prefix="/matchups", tags=["matchups"])


def _validate_teams(bundle: dict, team_a: str, team_b: str) -> None:
    if team_a == team_b:
        raise HTTPException(status_code=400, detail="team_a and team_b must be different teams")

    valid_teams = set(bundle["season"]["averages"].index)

    for team in (team_a, team_b):
        if team not in valid_teams:
            raise HTTPException(status_code=404, detail=f"Unknown team: {team}")


@router.get("/head-to-head", response_model=HeadToHeadResponse)
def get_head_to_head(
    team_a: str = Query(...),
    team_b: str = Query(...),
    bundle: dict = Depends(get_analytics_bundle),
):
    _validate_teams(bundle, team_a, team_b)
    return build_head_to_head_response(bundle, team_a, team_b)


@router.get("/history", response_model=MatchupHistoryResponse)
def get_matchup_history(
    team_a: str = Query(...),
    team_b: str = Query(...),
    bundle: dict = Depends(get_analytics_bundle),
):
    _validate_teams(bundle, team_a, team_b)
    return build_matchup_history_response(bundle, team_a, team_b)
