import { StatusBarChart } from "@/components/charts/status-bar-chart";
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
import { getTeamDetail, getTeams } from "@/lib/api";
import {
  categoryLabel,
  formatNumber,
  formatPercent,
  formatSignedPercent,
  formatVolatility,
} from "@/lib/format";

interface PageProps {
  searchParams: Promise<{ team?: string }>;
}

export default async function TeamAnalysisPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const teams = await getTeams();
  const team = params.team && teams.includes(params.team) ? params.team : teams[0];

  const detail = await getTeamDetail(team);

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
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Team Analysis</h1>
        <p className="text-sm text-muted-foreground">Deep dive on a single team&apos;s season.</p>
      </div>

      <ParamSelect
        paramName="team"
        value={team}
        options={teams.map((t) => ({ value: t, label: t }))}
      />

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
          <CardTitle>Category Percentile</CardTitle>
        </CardHeader>
        <CardContent>
          <StatusBarChart data={chartData} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Category Breakdown</CardTitle>
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
