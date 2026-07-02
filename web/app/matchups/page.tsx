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
import { cn } from "@/lib/utils";

interface PageProps {
  searchParams: Promise<{ team_a?: string; team_b?: string }>;
}

function resultBadgeClass(result: RoundOutcome) {
  switch (result) {
    case "W":
      return "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300";
    case "L":
      return "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300";
    default:
      return "bg-muted text-muted-foreground";
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
                          className={cn(
                            "rounded px-1.5 py-0.5 text-xs font-semibold",
                            resultBadgeClass(round.team_a_result)
                          )}
                        >
                          {round.team_a_result}
                        </span>{" "}
                        <span className="tabular-nums">{round.team_a_score}</span>
                      </TableCell>
                      <TableCell className="text-right">
                        <span className="tabular-nums">{round.team_b_score}</span>{" "}
                        <span
                          className={cn(
                            "rounded px-1.5 py-0.5 text-xs font-semibold",
                            resultBadgeClass(round.team_b_result)
                          )}
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
