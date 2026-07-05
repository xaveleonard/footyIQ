import { ListOrdered } from "lucide-react";

import { TeamBarChart } from "@/components/charts/team-bar-chart";
import { PageHeader } from "@/components/page-header";
import { ParamSelect } from "@/components/param-select";
import { ParamTabs } from "@/components/param-tabs";
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
import { categoryLabel, formatNumber, formatPercent, formatVolatility } from "@/lib/format";
import type { RankingsWindow } from "@/lib/types";

const WINDOW_OPTIONS = [
  { value: "season", label: "Season" },
  { value: "last3", label: "Last 3 Rounds" },
];

interface PageProps {
  searchParams: Promise<{ category?: string; window?: string }>;
}

export default async function LeaderboardsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const requested = params.category ?? "score";
  const category = (CATEGORIES as readonly string[]).includes(requested) ? requested : "score";
  const window: RankingsWindow = params.window === "last3" ? "last3" : "season";

  const leaderboard = await getLeaderboard(category, window);

  const chartData = leaderboard.map((entry) => ({
    name: entry.team_name,
    value: entry.average,
  }));

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        icon={ListOrdered}
        title="Category Leaderboards"
        description="Season averages ranked by category."
      />

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <ParamSelect
          paramName="category"
          value={category}
          options={CATEGORIES.map((c) => ({ value: c, label: categoryLabel(c) }))}
        />
        <ParamTabs paramName="window" value={window} options={WINDOW_OPTIONS} />
      </div>

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
          <CardTitle>
            {categoryLabel(category)} — {window === "last3" ? "Last 3 Rounds" : "Season"}
          </CardTitle>
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
                    {formatVolatility(entry.volatility)}
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
