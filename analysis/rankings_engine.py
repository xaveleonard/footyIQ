import pandas as pd


# ===========================================================
# CATEGORY WEIGHTS
# ===========================================================

CATEGORY_WEIGHTS = {
    "score": 3,
    "spoils": 2,
    "kicks": 1,
    "handballs": 1,
    "marks": 1,
    "hitouts": 1,
    "tackles": 1,
    "cp": 1,
    "clearances": 1,
    "r50": 1
}

WEIGHT_SERIES = pd.Series(
    CATEGORY_WEIGHTS
)

TOTAL_WEIGHT = WEIGHT_SERIES.sum()


# ===========================================================
# RANKINGS ENGINE
# ===========================================================

class RankingsEngine:

    # =======================================================
    # WEIGHTED WIN SCORE
    # =======================================================

    def weighted_win_score(
        self,
        win_rates
    ):

        return (
            win_rates.mul(WEIGHT_SERIES)
            .sum(axis=1)
            / TOTAL_WEIGHT
        )

    # =======================================================
    # POWER RANKINGS
    # =======================================================

    def compute_power_rankings(
        self,
        percentiles,
        win_rates,
        volatility
    ):

        win_component = (
            self.weighted_win_score(
                win_rates
            )
        )

        percentile_component = (
            percentiles.mean(axis=1)
        )

        consistency_component = (
            100 -
            volatility.mean(axis=1)
        )

        power_score = (
            (win_component * 0.50) +
            (percentile_component * 0.30) +
            (consistency_component * 0.20)
        )

        rankings = pd.DataFrame({
            "Team": power_score.index,
            "Power Score": power_score.values
        })

        rankings["Power Rank"] = (
            rankings["Power Score"]
            .rank(
                ascending=False,
                method="min"
            )
            .astype(int)
        )

        return (
            rankings[
                [
                    "Power Rank",
                    "Team",
                    "Power Score"
                ]
            ]
            .sort_values("Power Rank")
            .reset_index(drop=True)
        )

    # =======================================================
    # CATEGORY LEADERBOARDS
    # =======================================================

    def build_category_leaderboards(
        self,
        season
    ):

        leaderboards = {}

        for category in season[
            "averages"
        ].columns:

            leaderboard = pd.DataFrame({
                "Rank": season["ranks"][
                    category
                ],
                "Team": season["averages"].index,
                "Average": season["averages"][
                    category
                ],
                "Win Rate %": season[
                    "win_rates"
                ][category],
                "Volatility %": season[
                    "volatility"
                ][category]
            })

            leaderboards[category] = (
                leaderboard
                .sort_values("Rank")
                .reset_index(drop=True)
            )

        return leaderboards