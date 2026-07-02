import pandas as pd

from analysis.constants import CATEGORY_COLS, CATEGORY_WEIGHTS


# ===========================================================
# MATCHUP ENGINE
# ===========================================================

class MatchupEngine:

    def __init__(self):

        self.category_weights = CATEGORY_WEIGHTS

    # =======================================================
    # HEAD TO HEAD MATCHUP
    # =======================================================

    def build_head_to_head(
        self,
        team_a,
        team_b,
        season,
        recent_form_change
    ):
        """
        Builds head-to-head comparison data.
        """

        rows = []

        projected_a_score = 0
        projected_b_score = 0

        for category in season[
            "averages"
        ].columns:

            a_avg = season[
                "averages"
            ].loc[team_a, category]

            b_avg = season[
                "averages"
            ].loc[team_b, category]

            a_rank = season[
                "ranks"
            ].loc[team_a, category]

            b_rank = season[
                "ranks"
            ].loc[team_b, category]

            a_form = recent_form_change.loc[
                team_a,
                category
            ]

            b_form = recent_form_change.loc[
                team_b,
                category
            ]

            a_vol = season[
                "volatility"
            ].loc[team_a, category]

            b_vol = season[
                "volatility"
            ].loc[team_b, category]

            # ===================================================
            # CATEGORY WEIGHT
            # ===================================================

            weight = self.category_weights.get(
                category,
                1
            )

            # ===================================================
            # PROJECTED CATEGORY WINNER
            # USING RANKS
            # LOWER RANK = BETTER
            # ===================================================

            if a_rank < b_rank:

                projected_winner = team_a

                projected_a_score += weight

            elif b_rank < a_rank:

                projected_winner = team_b

                projected_b_score += weight

            else:

                projected_winner = "Tie"

                projected_a_score += (
                    weight / 2
                )

                projected_b_score += (
                    weight / 2
                )

            rows.append({

                "Category": category,

                # TEAM A
                f"{team_a} Avg": a_avg,
                f"{team_a} Rank": a_rank,
                f"{team_a} Form": round(
                    a_form,
                    1
                ),
                f"{team_a} Vol": a_vol,

                # TEAM B
                f"{team_b} Avg": b_avg,
                f"{team_b} Rank": b_rank,
                f"{team_b} Form": round(
                    b_form,
                    1
                ),
                f"{team_b} Vol": b_vol,

                # RESULT
                "Projected Winner": projected_winner
            })

        comparison_df = pd.DataFrame(rows)

        return {

            "team_a": team_a,
            "team_b": team_b,

            "projected_score": {

                team_a: int(projected_a_score),

                team_b: int(projected_b_score)
            },

            "comparison_table": comparison_df
        }

    # =======================================================
    # ROUND BY ROUND MATCHUP HISTORY
    # =======================================================

    # =======================================================
    # ROUND BY ROUND MATCHUP HISTORY
    # =======================================================

    def build_round_matchup_history(
        self,
        team_a,
        team_b,
        raw_df
    ):

        # ===================================================
        # STAT COLUMNS
        # ===================================================

        stat_columns = CATEGORY_COLS

        # ===================================================
        # TEAM DATA
        # ===================================================

        team_a_df = (
            raw_df[
                raw_df["team_name"] == team_a
            ]
            .sort_values("round")
            .reset_index(drop=True)
        )

        team_b_df = (
            raw_df[
                raw_df["team_name"] == team_b
            ]
            .sort_values("round")
            .reset_index(drop=True)
        )

        rounds = min(
            len(team_a_df),
            len(team_b_df)
        )

        team_a_df = (
            team_a_df.iloc[:rounds]
        )

        team_b_df = (
            team_b_df.iloc[:rounds]
        )

        # ===================================================
        # BUILD H2H RESULTS
        # ===================================================

        results = []

        team_a_wins = 0
        team_b_wins = 0
        draws = 0

        for i in range(rounds):

            a_categories = 0
            b_categories = 0

            for stat in stat_columns:

                a_value = (
                    team_a_df.iloc[i][stat]
                )

                b_value = (
                    team_b_df.iloc[i][stat]
                )

                # ===========================================
                # CATEGORY WEIGHTING
                # ===========================================

                weight = CATEGORY_WEIGHTS.get(stat, 1)

                # ===========================================
                # CATEGORY WINNER
                # ===========================================

                if a_value > b_value:

                    a_categories += weight

                elif b_value > a_value:

                    b_categories += weight

                else:

                    split_weight = (
                        weight / 2
                    )

                    a_categories += split_weight
                    b_categories += split_weight

            # ===============================================
            # ROUND RESULT
            # ===============================================

            if a_categories > b_categories:

                a_result = "W"
                b_result = "L"

                team_a_wins += 1

            elif b_categories > a_categories:

                a_result = "L"
                b_result = "W"

                team_b_wins += 1

            else:

                a_result = "D"
                b_result = "D"

                draws += 1

            results.append({

                "Round":
                    int(
                        team_a_df.iloc[i]["round"]
                    ),

                f"{team_a} Result":
                    a_result,

                f"{team_a} Score":
                    int(a_categories),

                f"{team_b} Score":
                    int(b_categories),

                f"{team_b} Result":
                    b_result
            })

        # ===================================================
        # SUMMARY
        # ===================================================

        total_matchups = rounds

        summary = {

            "team_a_wins":
                team_a_wins,

            "team_b_wins":
                team_b_wins,

            "draws":
                draws,

            "team_a_win_pct":
                round(
                    (
                        team_a_wins
                        / total_matchups
                    ) * 100,
                    1
                ),

            "team_b_win_pct":
                round(
                    (
                        team_b_wins
                        / total_matchups
                    ) * 100,
                    1
                )
        }

        # ===================================================
        # DISPLAY TABLES
        # ===================================================

        team_a_display = (
            team_a_df[
                ["round"] + stat_columns
            ]
            .copy()
        )

        team_b_display = (
            team_b_df[
                ["round"] + stat_columns
            ]
            .copy()
        )

        return {

            "team_a_rounds":
                team_a_display,

            "team_b_rounds":
                team_b_display,

            "head_to_head_table":
                pd.DataFrame(results),

            "summary":
                summary
        }