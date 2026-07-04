import { TeamBarChart } from "@/components/charts/team-bar-chart";
import { ParamSelect } from "@/components/param-select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getLeaderboard } from "@/lib/api";
import { CATEGORIES } from "@/lib/categories";
import { categoryLabel, formatNumber, formatPercent } from "@/lib/format";

interface PageProps {
  searchParams: Promise<{ category?: string }>;
}

export default async function LeaderboardsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const requested = params.category ?? "score";
  const category = (CATEGORIES as readonly string[]).includes(requested) ? requested : "score";

  const leaderboard = await getLeaderboard(category);

  const chartData = leaderboard.map((entry) => ({
    name: entry.team_name,
    value: entry.average,
  }));

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Category Leaderboards</h1>
        <p className="text-sm text-muted-foreground">Season averages ranked by category.</p>
      </div>

      <ParamSelect
        paramName="category"
        value={category}
        options={CATEGORIES.map((c) => ({ value: c, label: categoryLabel(c) }))}
      />

      <Card>
        <CardHeader>
          <CardTitle>{categoryLabel(category)} Average by Team</CardTitle>
        </CardHeader>
        <CardContent>
          <TeamBarChart data={chartData} valueLabel="Average" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{categoryLabel(category)}</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">Rank</TableHead>
                <TableHead>Team</TableHead>
                <TableHead className="text-right">Average</TableHead>
                <TableHead className="text-right">Win Rate</TableHead>
                <TableHead className="text-right">Volatility</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leaderboard.map((entry) => (
                <TableRow key={entry.team_name}>
                  <TableCell>{entry.rank}</TableCell>
                  <TableCell className="font-medium">{entry.team_name}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatNumber(entry.average)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatPercent(entry.win_rate)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    ±{formatPercent(entry.volatility)}
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
