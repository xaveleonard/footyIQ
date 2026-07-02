from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_analytics_bundle
from api.schemas.teams import TeamDetail
from api.serializers import build_team_detail

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[str])
def list_teams(bundle: dict = Depends(get_analytics_bundle)):
    return sorted(bundle["season"]["averages"].index.tolist())


@router.get("/{team_name}", response_model=TeamDetail)
def get_team(team_name: str, bundle: dict = Depends(get_analytics_bundle)):
    detail = build_team_detail(bundle, team_name)

    if detail is None:
        raise HTTPException(status_code=404, detail=f"Unknown team: {team_name}")

    return detail
