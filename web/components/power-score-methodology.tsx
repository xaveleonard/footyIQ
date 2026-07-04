"use client";

import { Activity, ChevronDown, Percent, Trophy } from "lucide-react";
import type { ComponentType } from "react";

import { Card, CardContent } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

interface Ingredient {
  label: string;
  weight: number;
  color: string;
  icon: ComponentType<{ className?: string }>;
  blurb: string;
}

const INGREDIENTS: Ingredient[] = [
  {
    label: "Win Rate",
    weight: 50,
    color: "var(--chart-1)",
    icon: Trophy,
    blurb:
      "How often you beat the league category-by-category, each round. Score counts 3×, Spoils 2×, everything else 1×.",
  },
  {
    label: "Percentile",
    weight: 30,
    color: "var(--chart-2)",
    icon: Percent,
    blurb: "Your average percentile across all 10 stats, ranked against the whole league.",
  },
  {
    label: "Consistency",
    weight: 20,
    color: "var(--chart-3)",
    icon: Activity,
    blurb: "Rewards steady output round to round — big swings drag this down.",
  },
];

export function PowerScoreMethodology() {
  return (
    <Card>
      <Collapsible>
        <CollapsibleTrigger className="group flex w-full items-center justify-between px-(--card-spacing) py-(--card-spacing) text-left">
          <span className="font-heading text-base leading-snug font-medium">
            How is Power Score calculated?
          </span>
          <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground transition-transform group-data-[panel-open]:rotate-180" />
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="flex flex-col gap-4 pt-4">
            <p className="text-sm text-muted-foreground">
              Three ingredients, blended into one number:
            </p>

            <div className="flex h-7 w-full gap-0.5">
              {INGREDIENTS.map((ingredient, index) => (
                <div
                  key={ingredient.label}
                  className={cn(
                    "flex items-center justify-center text-xs font-medium text-white",
                    index === 0 && "rounded-l-md",
                    index === INGREDIENTS.length - 1 && "rounded-r-md"
                  )}
                  style={{ width: `${ingredient.weight}%`, backgroundColor: ingredient.color }}
                >
                  {ingredient.weight}%
                </div>
              ))}
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {INGREDIENTS.map((ingredient) => {
                const Icon = ingredient.icon;
                return (
                  <div key={ingredient.label} className="flex flex-col gap-1.5">
                    <div className="flex items-center gap-2">
                      <span
                        className="flex size-6 shrink-0 items-center justify-center rounded-full"
                        style={{ backgroundColor: ingredient.color }}
                      >
                        <Icon className="size-3.5 text-white" />
                      </span>
                      <span className="text-sm font-medium text-foreground">
                        {ingredient.label}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {ingredient.weight}%
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">{ingredient.blurb}</p>
                  </div>
                );
              })}
            </div>

            <code className="rounded-md bg-muted px-3 py-2 text-xs text-muted-foreground">
              Power Score = 0.5 &times; Win Rate + 0.3 &times; Percentile + 0.2 &times;
              Consistency
            </code>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}
