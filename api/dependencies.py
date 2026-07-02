from functools import lru_cache

from analysis.analytics_engine import AnalyticsEngine
from analysis.rankings_engine import RankingsEngine
from analysis.matchup_engine import MatchupEngine

from api.config import get_settings


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

    profiles = analytics_engine.identify_strengths_weaknesses(season["ranks"])

    power_rankings = rankings_engine.compute_power_rankings(
        season["percentiles"], season["win_rates"], season["volatility"]
    )

    leaderboards = rankings_engine.build_category_leaderboards(season)

    return {
        "season": season,
        "recent_form_change": recent_form_change,
        "profiles": profiles,
        "power_rankings": power_rankings,
        "leaderboards": leaderboards,
        "matchup_engine": matchup_engine,
        "raw_df": analytics_engine.df,
    }


@lru_cache
def get_analytics_bundle() -> dict:
    settings = get_settings()
    return build_analytics_bundle(settings.data_path)
