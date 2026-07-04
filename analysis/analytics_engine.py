import pandas as pd
import numpy as np

from analysis.constants import CATEGORY_COLS, RECENT_FORM_ROUNDS


# ===========================================================
# ANALYTICS ENGINE
# ===========================================================

class AnalyticsEngine:

    def __init__(self, data_path):

        self.data_path = data_path

        self.df = None

        self.recent_df = None

    # =======================================================
    # LOAD DATA
    # =======================================================

    def load_data(self):

        self.df = pd.read_parquet(
            self.data_path
        )

        self.recent_df = self.filter_last_n_rounds(
            self.df,
            RECENT_FORM_ROUNDS
        )

    # =======================================================
    # FILTER TO LAST N ROUNDS
    # =======================================================

    def filter_last_n_rounds(self, df, n_rounds):

        latest_round = df["round"].max()

        min_round = (
            latest_round -
            n_rounds +
            1
        )

        return df[
            df["round"] >= min_round
        ].copy()

    # =======================================================
    # TEAM AVERAGES
    # =======================================================

    def compute_team_averages(self, df):

        return (
            df.groupby("team_name")[CATEGORY_COLS]
            .mean()
            .round(2)
        )

    # =======================================================
    # CATEGORY RANKS
    # =======================================================

    def compute_category_ranks(
        self,
        averages
    ):

        return (
            averages.rank(
                ascending=False,
                method="min"
            )
            .astype(int)
        )

    # =======================================================
    # PERCENTILES
    # =======================================================

    def compute_percentiles(
        self,
        averages
    ):

        return (
            averages.rank(pct=True)
            * 100
        ).round(1)

    # =======================================================
    # VOLATILITY
    # =======================================================

    def compute_volatility(self, df):

        grouped = (
            df.groupby("team_name")[CATEGORY_COLS]
        )

        means = grouped.mean()

        stds = grouped.std()

        return (
            (stds / means) * 100
        ).round(2)

    # =======================================================
    # CATEGORY WIN RATES
    # =======================================================

    def compute_category_win_rates(
        self,
        df
    ):

        matchup_df = (
            df.sort_values(
                [
                    "round",
                    "matchup",
                    "team_name"
                ]
            )
            .groupby(
                ["round", "matchup"]
            )
            .filter(lambda x: len(x) == 2)
        )

        rows = []

        for (_, _), group in matchup_df.groupby(
            ["round", "matchup"]
        ):

            t1 = group.iloc[0]

            t2 = group.iloc[1]

            comparison = (
                t1[CATEGORY_COLS] >
                t2[CATEGORY_COLS]
            )

            reverse_comparison = (
                t2[CATEGORY_COLS] >
                t1[CATEGORY_COLS]
            )

            rows.append(pd.DataFrame({
                "team_name": np.where(
                    comparison,
                    t1["team_name"],
                    np.where(
                        reverse_comparison,
                        t2["team_name"],
                        None
                    )
                ),
                "category": CATEGORY_COLS
            }))

        wins_df = pd.concat(rows)

        wins_df = wins_df.dropna()

        win_counts = (
            wins_df.groupby(
                ["team_name", "category"]
            )
            .size()
            .unstack(fill_value=0)
        )

        games_played = (
            df.groupby("team_name")
            .size()
        )

        return (
            (
                win_counts.div(
                    games_played,
                    axis=0
                ) * 100
            )
            .round(1)
            .reindex(columns=CATEGORY_COLS)
            .fillna(0)
        )

    # =======================================================
    # RECENT FORM CHANGE
    # =======================================================

    def compute_recent_form_change(
        self,
        season_averages,
        recent_averages
    ):

        return (
            (
                recent_averages -
                season_averages
            ) / season_averages
        ) * 100

    # =======================================================
    # STRENGTHS / WEAKNESSES
    # =======================================================

    def identify_strengths_weaknesses(
        self,
        ranks
    ):

        profiles = {}

        for team in ranks.index:

            team_ranks = ranks.loc[team]

            profiles[team] = {
                "strengths": list(
                    team_ranks[
                        team_ranks <= 4
                    ].index
                ),
                "weaknesses": list(
                    team_ranks[
                        team_ranks >= 13
                    ].index
                )
            }

        return profiles

    # =======================================================
    # LEAGUE RECORDS
    # =======================================================

    def compute_league_records(self, df):

        records = {}

        for category in CATEGORY_COLS:

            max_value = df[category].max()

            holders = (
                df[df[category] == max_value][["team_name", "round"]]
                .drop_duplicates()
                .sort_values(["round", "team_name"])
            )

            records[category] = {
                "value": max_value,
                "holders": holders.to_dict("records"),
            }

        return records

    # =======================================================
    # BUILD ANALYTICS
    # =======================================================

    def build_analytics(self, df):

        averages = self.compute_team_averages(df)

        return {
            "averages": averages,
            "ranks": self.compute_category_ranks(
                averages
            ),
            "percentiles": self.compute_percentiles(
                averages
            ),
            "win_rates": self.compute_category_win_rates(
                df
            ),
            "volatility": self.compute_volatility(
                df
            )
        }