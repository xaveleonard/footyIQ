import { Medal } from "lucide-react";

import { PageHeader } from "@/components/page-header";
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
import { getLeagueRecords } from "@/lib/api";
import { categoryLabel, formatNumber } from "@/lib/format";

export default async function RecordsPage() {
  const records = await getLeagueRecords();

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        icon={Medal}
        title="League Records"
        description="The single best round ever recorded in each category, and who did it."
      />

      <Card>
        <CardHeader>
          <CardTitle>All-Time Bests</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Category</TableHead>
                <TableHead className="text-right">Record</TableHead>
                <TableHead>Held By</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {records.map((record) => (
                <TableRow key={record.category}>
                  <TableCell className="font-medium">
                    {categoryLabel(record.category)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatNumber(record.value, 0)}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1.5">
                      {record.holders.map((holder, index) => (
                        <Badge key={`${holder.team_name}-${holder.round}-${index}`} variant="outline">
                          {holder.team_name} (R{holder.round})
                        </Badge>
                      ))}
                    </div>
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
