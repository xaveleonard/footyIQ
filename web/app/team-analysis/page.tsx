import { BarChart3 } from "lucide-react";

import { StatusBarChart } from "@/components/charts/status-bar-chart";
import { PageHeader } from "@/components/page-header";
import { ParamSelect } from "@/components/param-select";
import { ParamTabs } from "@/components/param-tabs";
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
import { getTeamDetail, getTeams } from "@/lib/api";
import {
  categoryLabel,
  formatNumber,
  formatPercent,
  formatSignedPercent,
  formatVolatility,
} from "@/lib/format";
import type { RankingsWindow } from "@/lib/types";

const WINDOW_OPTIONS = [
  { value: "season", label: "Season" },
  { value: "last3", label: "Last 3 Rounds" },
];

interface PageProps {
  searchParams: Promise<{ team?: string; window?: string }>;
}

export default async function TeamAnalysisPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const teams = await getTeams();
  const team = params.team && teams.includes(params.team) ? params.team : teams[0];
  const window: RankingsWindow = params.window === "last3" ? "last3" : "season";

  const detail = await getTeamDetail(team, window);

  const teamCount = teams.length;
  const chartData = detail.categories.map((stat) => ({
    category: stat.category,
    label: categoryLabel(stat.category),
    percentile:
      teamCount > 1 ? (100 * (teamCount - stat.rank)) / (teamCount - 1) : 100,
    status: detail.strengths.includes(stat.category)
      ? ("good" as const)
      : detail.weaknesses.includes(stat.category)
        ? ("serious" as const)
        : ("neutral" as const),
  }));

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        icon={BarChart3}
        title="Team Analysis"
        description="Deep dive on a single team's season."
      />

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <ParamSelect
          paramName="team"
          value={team}
          options={teams.map((t) => ({ value: t, label: t }))}
        />
        <ParamTabs paramName="window" value={window} options={WINDOW_OPTIONS} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Power Rank</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">#{detail.power_rank}</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Power Score</CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">
            {formatNumber(detail.power_score)}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Strengths</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {detail.strengths.length === 0 ? (
              <span className="text-sm text-muted-foreground">None</span>
            ) : (
              detail.strengths.map((category) => (
                <Badge key={category} variant="default">
                  {categoryLabel(category)}
                </Badge>
              ))
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Weaknesses</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {detail.weaknesses.length === 0 ? (
              <span className="text-sm text-muted-foreground">None</span>
            ) : (
              detail.weaknesses.map((category) => (
                <Badge key={category} variant="destructive">
                  {categoryLabel(category)}
                </Badge>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            Category Percentile — {window === "last3" ? "Last 3 Rounds" : "Season"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <StatusBarChart data={chartData} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            Category Breakdown — {window === "last3" ? "Last 3 Rounds" : "Season"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Category</TableHead>
                <TableHead className="text-right">Rank</TableHead>
                <TableHead className="text-right">Average</TableHead>
                <TableHead className="text-right">Form vs Avg</TableHead>
                <TableHead className="text-right">Win Rate</TableHead>
                <TableHead className="text-right">Volatility</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {detail.categories.map((stat) => (
                <TableRow key={stat.category}>
                  <TableCell className="font-medium">{categoryLabel(stat.category)}</TableCell>
                  <TableCell className="text-right tabular-nums">{stat.rank}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatNumber(stat.average)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatSignedPercent(stat.form_change)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatPercent(stat.win_rate)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatVolatility(stat.volatility)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
