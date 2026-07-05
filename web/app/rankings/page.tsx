import { Trophy } from "lucide-react";

import { TeamBarChart } from "@/components/charts/team-bar-chart";
import { PageHeader } from "@/components/page-header";
import { ParamTabs } from "@/components/param-tabs";
import { PowerScoreMethodology } from "@/components/power-score-methodology";
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
import { getPowerRankings } from "@/lib/api";
import { formatNumber } from "@/lib/format";
import type { RankingsWindow } from "@/lib/types";

const WINDOW_OPTIONS = [
  { value: "season", label: "Season" },
  { value: "last3", label: "Last 3 Rounds" },
];

interface PageProps {
  searchParams: Promise<{ window?: string }>;
}

export default async function RankingsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const window: RankingsWindow = params.window === "last3" ? "last3" : "season";

  const rankings = await getPowerRankings(window);

  const chartData = rankings.map((entry) => ({
    name: entry.team_name,
    value: entry.power_score,
  }));

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        icon={Trophy}
        title="Power Rankings"
        description="Blended from category win rate, percentile strength, and consistency."
      />

      <PowerScoreMethodology />

      <ParamTabs paramName="window" value={window} options={WINDOW_OPTIONS} />

      <Card>
        <CardHeader>
          <CardTitle>Power Score by Team</CardTitle>
        </CardHeader>
        <CardContent>
          <TeamBarChart data={chartData} valueLabel="Power Score" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{window === "last3" ? "Last 3 Rounds" : "Season"} Standings</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">Rank</TableHead>
                <TableHead>Team</TableHead>
                <TableHead className="text-right">Power Score</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rankings.map((entry) => (
                <TableRow key={entry.team_name}>
                  <TableCell>
                    <Badge variant={entry.power_rank <= 3 ? "default" : "outline"}>
                      #{entry.power_rank}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-medium">{entry.team_name}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatNumber(entry.power_score)}
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
