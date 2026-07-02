export const CATEGORIES = [
  "score",
  "kicks",
  "handballs",
  "marks",
  "hitouts",
  "tackles",
  "cp",
  "clearances",
  "r50",
  "spoils",
] as const;

export type Category = (typeof CATEGORIES)[number];
