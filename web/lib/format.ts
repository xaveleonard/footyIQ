const CATEGORY_LABELS: Record<string, string> = {
  score: "Score",
  kicks: "Kicks",
  handballs: "Handballs",
  marks: "Marks",
  hitouts: "Hitouts",
  tackles: "Tackles",
  cp: "CP",
  clearances: "Clearances",
  r50: "R50",
  spoils: "Spoils",
};

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] ?? category;
}

export function formatNumber(value: number, decimals = 1): string {
  return value.toFixed(decimals);
}

export function formatSigned(value: number, decimals = 1): string {
  const formatted = Math.abs(value).toFixed(decimals);
  if (value > 0) return `+${formatted}`;
  if (value < 0) return `-${formatted}`;
  return formatted;
}

export function formatPercent(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`;
}
