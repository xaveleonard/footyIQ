from functools import lru_cache
from typing import Literal

from analysis.analytics_engine import AnalyticsEngine
from analysis.rankings_engine import RankingsEngine
from analysis.matchup_engine import MatchupEngine
from analysis.constants import RANKINGS_WINDOW_ROUNDS

from api.config import get_settings

Window = Literal["season", "last3"]


def _build_window(rankings_engine, analytics):
    return {
        "power_rankings": rankings_engine.compute_power_rankings(
            analytics["percentiles"], analytics["win_rates"], analytics["volatility"]
        ),
        "leaderboards": rankings_engine.build_category_leaderboards(analytics),
    }


def build_analytics_bundle(data_path: str) -> dict:
    """
    Relocated from visualization/app.py's load_analytics() (previously
    @st.cache_data). Assembles every derived dataset the frontend needs
    in one pass over the raw parquet data.
    """
    analytics_engine = AnalyticsEngine(data_path)
    rankings_engine = RankingsEngine()
    matchup_engine = MatchupEngine()

    analytics_engine.load_data()

    season = analytics_engine.build_analytics(analytics_engine.df)
    recent = analytics_engine.build_analytics(analytics_engine.recent_df)

    recent_form_change = analytics_engine.compute_recent_form_change(
        season["averages"], recent["averages"]
    )

    last3_df = analytics_engine.filter_last_n_rounds(
        analytics_engine.df, RANKINGS_WINDOW_ROUNDS
    )
    last3_analytics = analytics_engine.build_analytics(last3_df)

    # Every per-team view (Team Analysis, Power Rankings, Leaderboards) can be
    # scoped to either the full season or just the last 3 rounds - this is the
    # one dict everything else derives from per window.
    analytics_by_window = {"season": season, "last3": last3_analytics}

    profiles = {
        window: analytics_engine.identify_strengths_weaknesses(analytics["ranks"])
        for window, analytics in analytics_by_window.items()
    }

    windows = {
        window: _build_window(rankings_engine, analytics)
        for window, analytics in analytics_by_window.items()
    }

    league_records = analytics_engine.compute_league_records(analytics_engine.df)

    return {
        "season": season,
        "analytics_by_window": analytics_by_window,
        "recent_form_change": recent_form_change,
        "profiles": profiles,
        "windows": windows,
        "league_records": league_records,
        "matchup_engine": matchup_engine,
        "raw_df": analytics_engine.df,
    }


@lru_cache
def get_analytics_bundle() -> dict:
    settings = get_settings()
    return build_analytics_bundle(settings.data_path)
