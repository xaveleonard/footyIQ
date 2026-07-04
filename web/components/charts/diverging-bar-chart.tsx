"use client";

import { Bar, BarChart, CartesianGrid, Cell, LabelList, ReferenceLine, XAxis, YAxis } from "recharts";

import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";

export interface DivergingBarDatum {
  label: string;
  value: number;
}

interface DivergingBarChartProps {
  data: DivergingBarDatum[];
  positiveLabel: string;
  negativeLabel: string;
  orientation?: "horizontal" | "vertical";
}

const chartConfig = {
  value: { label: "Value" },
} satisfies ChartConfig;

function colorFor(value: number): string {
  if (value > 0.001) return "var(--diverging-a)";
  if (value < -0.001) return "var(--diverging-b)";
  return "var(--diverging-neutral)";
}

function ChartLegend({
  positiveLabel,
  negativeLabel,
}: {
  positiveLabel: string;
  negativeLabel: string;
}) {
  return (
    <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground">
      <span className="flex items-center gap-1.5">
        <span
          className="h-2.5 w-2.5 shrink-0 rounded-[2px]"
          style={{ backgroundColor: "var(--diverging-a)" }}
        />
        {positiveLabel}
      </span>
      <span className="flex items-center gap-1.5">
        <span
          className="h-2.5 w-2.5 shrink-0 rounded-[2px]"
          style={{ backgroundColor: "var(--diverging-b)" }}
        />
        {negativeLabel}
      </span>
    </div>
  );
}

export function DivergingBarChart({
  data,
  positiveLabel,
  negativeLabel,
  orientation = "horizontal",
}: DivergingBarChartProps) {
  const maxAbs = Math.max(1, ...data.map((d) => Math.abs(d.value)));
  const domain: [number, number] = [-maxAbs, maxAbs];

  if (orientation === "horizontal") {
    const height = Math.max(240, data.length * 32);

    return (
      <div className="flex flex-col gap-3">
        <ChartLegend positiveLabel={positiveLabel} negativeLabel={negativeLabel} />
        <ChartContainer config={chartConfig} className="aspect-auto w-full" style={{ height }}>
          <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
            <CartesianGrid horizontal={false} />
            <XAxis type="number" domain={domain} hide />
            <YAxis
              type="category"
              dataKey="label"
              tickLine={false}
              axisLine={false}
              width={110}
              tick={{ fontSize: 12 }}
              interval={0}
            />
            <ReferenceLine x={0} stroke="var(--border)" />
            <ChartTooltip cursor={{ fill: "var(--muted)" }} content={<ChartTooltipContent hideLabel />} />
            <Bar dataKey="value" radius={4}>
              {data.map((entry, index) => (
                <Cell key={index} fill={colorFor(entry.value)} />
              ))}
              <LabelList
                dataKey="value"
                position="insideEnd"
                className="fill-white"
                fontSize={12}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <ChartLegend positiveLabel={positiveLabel} negativeLabel={negativeLabel} />
      <ChartContainer config={chartConfig} className="aspect-auto w-full" style={{ height: 240 }}>
        <BarChart data={data} margin={{ top: 8, bottom: 8 }}>
          <CartesianGrid vertical={false} />
          <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fontSize: 12 }} interval={0} />
          <YAxis type="number" domain={domain} hide />
          <ReferenceLine y={0} stroke="var(--border)" />
          <ChartTooltip cursor={{ fill: "var(--muted)" }} content={<ChartTooltipContent hideLabel />} />
          <Bar dataKey="value" radius={4}>
            {data.map((entry, index) => (
              <Cell key={index} fill={colorFor(entry.value)} />
            ))}
          </Bar>
        </BarChart>
      </ChartContainer>
    </div>
  );
}
