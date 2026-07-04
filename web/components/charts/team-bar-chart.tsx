"use client";

import { Bar, BarChart, CartesianGrid, LabelList, XAxis, YAxis } from "recharts";

import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

export interface TeamBarDatum {
  name: string;
  value: number;
}

interface TeamBarChartProps {
  data: TeamBarDatum[];
  valueLabel: string;
}

export function TeamBarChart({ data, valueLabel }: TeamBarChartProps) {
  const chartConfig = {
    value: { label: valueLabel, color: "var(--chart-1)" },
  } satisfies ChartConfig;

  const height = Math.max(240, data.length * 32);

  return (
    <ChartContainer config={chartConfig} className="aspect-auto w-full" style={{ height }}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 32 }}>
        <CartesianGrid horizontal={false} />
        <XAxis type="number" dataKey="value" hide />
        <YAxis
          type="category"
          dataKey="name"
          tickLine={false}
          axisLine={false}
          width={140}
          tick={{ fontSize: 12 }}
          interval={0}
        />
        <ChartTooltip cursor={{ fill: "var(--muted)" }} content={<ChartTooltipContent hideLabel />} />
        <Bar dataKey="value" fill="var(--color-value)" radius={4}>
          <LabelList
            dataKey="value"
            position="right"
            formatter={(value: string | number | boolean | null | undefined) =>
              typeof value === "number" ? value.toFixed(1) : ""
            }
            className="fill-foreground"
            fontSize={12}
          />
        </Bar>
      </BarChart>
    </ChartContainer>
  );
}
