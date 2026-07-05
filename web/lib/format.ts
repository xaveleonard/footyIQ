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

export function formatSigned(value: number | null, decimals = 1): string {
  if (value === null) return "—";
  const formatted = Math.abs(value).toFixed(decimals);
  if (value > 0) return `+${formatted}`;
  if (value < 0) return `-${formatted}`;
  return formatted;
}

export function formatPercent(value: number | null, decimals = 1): string {
  if (value === null) return "—";
  return `${value.toFixed(decimals)}%`;
}

// Volatility is a coefficient of variation - mathematically undefined
// (0/0) when a category's mean is 0, e.g. zero hitouts across every game
// in a small window. Bakes in the "±...%" formatting used everywhere
// volatility is displayed, so null is handled consistently in one place.
export function formatVolatility(value: number | null, decimals = 1): string {
  if (value === null) return "—";
  return `±${value.toFixed(decimals)}%`;
}

// Same undefined-when-zero-baseline caveat as formatVolatility, for
// "% change vs season average" figures.
export function formatSignedPercent(value: number | null, decimals = 1): string {
  if (value === null) return "—";
  return `${formatSigned(value, decimals)}%`;
}
