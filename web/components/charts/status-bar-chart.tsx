"use client";

import { Bar, BarChart, CartesianGrid, Cell, LabelList, ReferenceLine, XAxis, YAxis } from "recharts";

import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

export interface StatusBarDatum {
  category: string;
  label: string;
  percentile: number;
  status: "good" | "serious" | "neutral";
}

interface StatusBarChartProps {
  data: StatusBarDatum[];
}

const STATUS_COLOR: Record<StatusBarDatum["status"], string> = {
  good: "var(--status-good)",
  serious: "var(--status-serious)",
  neutral: "var(--muted-foreground)",
};

const chartConfig = {
  percentile: { label: "Percentile" },
} satisfies ChartConfig;

export function StatusBarChart({ data }: StatusBarChartProps) {
  const height = Math.max(260, data.length * 32);

  return (
    <ChartContainer config={chartConfig} className="aspect-auto w-full" style={{ height }}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 32 }}>
        <CartesianGrid horizontal={false} />
        <XAxis type="number" dataKey="percentile" domain={[0, 100]} hide />
        <YAxis
          type="category"
          dataKey="label"
          tickLine={false}
          axisLine={false}
          width={110}
          tick={{ fontSize: 12 }}
          interval={0}
        />
        <ReferenceLine x={50} stroke="var(--border)" />
        <ChartTooltip cursor={{ fill: "var(--muted)" }} content={<ChartTooltipContent hideLabel />} />
        <Bar dataKey="percentile" radius={4}>
          {data.map((entry) => (
            <Cell key={entry.category} fill={STATUS_COLOR[entry.status]} />
          ))}
          <LabelList
            dataKey="percentile"
            position="right"
            formatter={(value: string | number | boolean | null | undefined) =>
              typeof value === "number" ? value.toFixed(0) : ""
            }
            className="fill-foreground"
            fontSize={12}
          />
        </Bar>
      </BarChart>
    </ChartContainer>
  );
}
