import { TeamBarChart } from "@/components/charts/team-bar-chart";
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

export default async function RankingsPage() {
  const rankings = await getPowerRankings();

  const chartData = rankings.map((entry) => ({
    name: entry.team_name,
    value: entry.power_score,
  }));

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Power Rankings</h1>
        <p className="text-sm text-muted-foreground">
          Blended from category win rate, percentile strength, and consistency.
        </p>
      </div>

      <PowerScoreMethodology />

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
          <CardTitle>Season Standings</CardTitle>
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
