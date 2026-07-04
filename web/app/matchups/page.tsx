import type { CSSProperties } from "react";

import { DivergingBarChart } from "@/components/charts/diverging-bar-chart";
import { ParamSelect } from "@/components/param-select";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ApiError, getHeadToHead, getMatchupHistory, getTeams } from "@/lib/api";
import { categoryLabel, formatNumber, formatPercent } from "@/lib/format";
import type { HeadToHeadResponse, MatchupHistoryResponse, RoundOutcome } from "@/lib/types";

interface PageProps {
  searchParams: Promise<{ team_a?: string; team_b?: string }>;
}

function resultBadgeStyle(result: RoundOutcome): CSSProperties {
  switch (result) {
    case "W":
      return {
        backgroundColor: "color-mix(in oklch, var(--status-good) 15%, transparent)",
        color: "var(--status-good)",
      };
    case "L":
      return {
        backgroundColor: "color-mix(in oklch, var(--status-critical) 15%, transparent)",
        color: "var(--status-critical)",
      };
    default:
      return { backgroundColor: "var(--muted)", color: "var(--muted-foreground)" };
  }
}

export default async function MatchupsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const teams = await getTeams();

  const teamA = params.team_a && teams.includes(params.team_a) ? params.team_a : teams[0];
  const fallbackB = teams.find((t) => t !== teamA) ?? teams[0];
  const teamB =
    params.team_b && teams.includes(params.team_b) && params.team_b !== teamA
      ? params.team_b
      : fallbackB;

  const teamOptions = teams.map((t) => ({ value: t, label: t }));

  let headToHead: HeadToHeadResponse | undefined;
  let history: MatchupHistoryResponse | undefined;
  let error: string | null = null;

  try {
    [headToHead, history] = await Promise.all([
      getHeadToHead(teamA, teamB),
      getMatchupHistory(teamA, teamB),
    ]);
  } catch (err) {
    error = err instanceof ApiError ? err.message : "Failed to load matchup data.";
  }

  const categoryChartData = headToHead?.categories.map((row) => ({
    label: categoryLabel(row.category),
    value: row.team_b_rank - row.team_a_rank,
  }));

  const roundChartData = history?.rounds.map((round) => ({
    label: String(round.round),
    value: round.team_a_score - round.team_b_score,
  }));

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Head-to-Head Matchup</h1>
        <p className="text-sm text-muted-foreground">
          Projected category comparison and simulated round history.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <ParamSelect paramName="team_a" value={teamA} options={teamOptions} placeholder="Team A" />
        <ParamSelect paramName="team_b" value={teamB} options={teamOptions} placeholder="Team B" />
      </div>

      {error || !headToHead || !history ? (
        <Card>
          <CardContent className="py-8 text-center text-sm text-muted-foreground">
            {error ?? "Select two different teams to compare."}
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>{teamA}</CardTitle>
              </CardHeader>
              <CardContent className="text-3xl font-semibold">
                {headToHead.team_a_score}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>{teamB}</CardTitle>
              </CardHeader>
              <CardContent className="text-3xl font-semibold">
                {headToHead.team_b_score}
              </CardContent>
            </Card>
          </div>
          <p className="text-xs text-muted-foreground">
            Score = 3 pts &middot; Spoils = 2 pts &middot; all other categories = 1 pt
          </p>

          <Card>
            <CardHeader>
              <CardTitle>Category Advantage</CardTitle>
            </CardHeader>
            <CardContent>
              <DivergingBarChart
                data={categoryChartData ?? []}
                positiveLabel={teamA}
                negativeLabel={teamB}
                orientation="horizontal"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Category Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">{teamA}</TableHead>
                    <TableHead className="text-right">{teamB}</TableHead>
                    <TableHead className="text-right">Projected</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {headToHead.categories.map((row) => (
                    <TableRow key={row.category}>
                      <TableCell className="font-medium">
                        {categoryLabel(row.category)}
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {formatNumber(row.team_a_avg)}{" "}
                        <span className="text-muted-foreground">(#{row.team_a_rank})</span>
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {formatNumber(row.team_b_avg)}{" "}
                        <span className="text-muted-foreground">(#{row.team_b_rank})</span>
                      </TableCell>
                      <TableCell className="text-right">
                        <Badge variant={row.projected_winner === "tie" ? "outline" : "default"}>
                          {row.projected_winner === "tie"
                            ? "Tie"
                            : row.projected_winner === "team_a"
                              ? teamA
                              : teamB}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Historical Matchup Simulation</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-semibold">
                    {formatPercent(history.summary.team_a_win_pct)}
                  </div>
                  <div className="text-xs text-muted-foreground">{teamA} Win %</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold">{history.summary.draws}</div>
                  <div className="text-xs text-muted-foreground">Draws</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold">
                    {formatPercent(history.summary.team_b_win_pct)}
                  </div>
                  <div className="text-xs text-muted-foreground">{teamB} Win %</div>
                </div>
              </div>

              <DivergingBarChart
                data={roundChartData ?? []}
                positiveLabel={teamA}
                negativeLabel={teamB}
                orientation="vertical"
              />

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Round</TableHead>
                    <TableHead className="text-right">{teamA}</TableHead>
                    <TableHead className="text-right">{teamB}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {history.rounds.map((round) => (
                    <TableRow key={round.round}>
                      <TableCell>{round.round}</TableCell>
                      <TableCell className="text-right">
                        <span
                          className="rounded px-1.5 py-0.5 text-xs font-semibold"
                          style={resultBadgeStyle(round.team_a_result)}
                        >
                          {round.team_a_result}
                        </span>{" "}
                        <span className="tabular-nums">{round.team_a_score}</span>
                      </TableCell>
                      <TableCell className="text-right">
                        <span className="tabular-nums">{round.team_b_score}</span>{" "}
                        <span
                          className="rounded px-1.5 py-0.5 text-xs font-semibold"
                          style={resultBadgeStyle(round.team_b_result)}
                        >
                          {round.team_b_result}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
