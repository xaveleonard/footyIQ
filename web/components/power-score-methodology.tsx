"use client";

import { ChevronDown } from "lucide-react";

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Card, CardContent } from "@/components/ui/card";

export function PowerScoreMethodology() {
  return (
    <Card>
      <Collapsible>
        <CollapsibleTrigger className="group flex w-full items-center justify-between px-(--card-spacing) py-(--card-spacing) text-left">
          <span className="font-heading text-base leading-snug font-medium">
            How is Power Score calculated?
          </span>
          <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground transition-transform group-data-[panel-open]:rotate-180" />
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="flex flex-col gap-4 pt-4 text-sm text-muted-foreground">
            <p>
              Power Score blends three components into a single number, each measuring a
              different thing about a team&apos;s season:
            </p>

            <div className="flex flex-col gap-1">
              <p className="font-medium text-foreground">Category Win Rate — 50%</p>
              <p>
                Every round, your team&apos;s stats are compared category-by-category against
                your actual opponent, and you &quot;win&quot; a category if your value is
                higher. Win rate is the % of games won in that category across the season.
                The 10 category win rates are then combined into one number using weights
                that reflect how much each category is worth in a real matchup:{" "}
                <span className="font-medium text-foreground">Score counts 3&times;</span>,{" "}
                <span className="font-medium text-foreground">Spoils count 2&times;</span>,
                and the other 8 categories (Kicks, Handballs, Marks, Hitouts, Tackles, CP,
                Clearances, R50) each count 1&times;.
              </p>
            </div>

            <div className="flex flex-col gap-1">
              <p className="font-medium text-foreground">Percentile Strength — 30%</p>
              <p>
                For each of the 10 statistical categories, your team&apos;s season average is
                ranked against every other team in the league and converted to a percentile
                (0–100, where 100 is best in the league). This component is the average
                percentile across all 10 categories — a team that&apos;s consistently near
                the top of the league scores higher here, independent of how its actual
                head-to-head matchups played out.
              </p>
            </div>

            <div className="flex flex-col gap-1">
              <p className="font-medium text-foreground">Consistency — 20%</p>
              <p>
                This measures how stable a team&apos;s week-to-week output is, not how good
                it is. For each category, volatility is the coefficient of variation
                (standard deviation &divide; average, as a %) — a high number means big
                swings round to round, a low number means steady, predictable output. This
                component is 100 minus the average volatility across categories, so steadier
                teams score higher here, rewarding reliability over boom-or-bust performances.
              </p>
            </div>

            <p>
              Putting it together:{" "}
              <span className="font-medium text-foreground">
                Power Score = (Win Rate × 0.50) + (Percentile Strength × 0.30) + (Consistency
                × 0.20)
              </span>
              . Teams are then ranked from highest to lowest Power Score.
            </p>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}
