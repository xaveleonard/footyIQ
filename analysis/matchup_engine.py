import pandas as pd


# ===========================================================
# MATCHUP ENGINE
# ===========================================================

class MatchupEngine:

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

        projected_a_wins = 0

        projected_b_wins = 0

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
            # PROJECTED CATEGORY WINNER
            # ===================================================

            if a_avg > b_avg:

                projected_winner = team_a

                projected_a_wins += 1

            elif b_avg > a_avg:

                projected_winner = team_b

                projected_b_wins += 1

            else:

                projected_winner = "Tie"

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
                team_a: projected_a_wins,
                team_b: projected_b_wins
            },

            "comparison_table": comparison_df
        }