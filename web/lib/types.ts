export interface CategoryStat {
  category: string;
  average: number;
  rank: number;
  win_rate: number;
  // null when the category mean is 0 - coefficient of variation / % change
  // from a 0 baseline is mathematically undefined, not a real number
  volatility: number | null;
  form_change: number | null;
}

export interface TeamDetail {
  team_name: string;
  power_rank: number;
  power_score: number;
  strengths: string[];
  weaknesses: string[];
  categories: CategoryStat[];
}

export interface PowerRankingEntry {
  power_rank: number;
  team_name: string;
  power_score: number;
}

export interface LeaderboardEntry {
  rank: number;
  team_name: string;
  average: number;
  win_rate: number;
  volatility: number | null;
}

export type RankingsWindow = "season" | "last3";

export interface RecordHolder {
  team_name: string;
  round: number;
}

export interface CategoryRecord {
  category: string;
  value: number;
  holders: RecordHolder[];
}

export type ProjectedWinner = "team_a" | "team_b" | "tie";

export interface CategoryComparison {
  category: string;
  team_a_avg: number;
  team_a_rank: number;
  team_a_form: number | null;
  team_a_volatility: number | null;
  team_b_avg: number;
  team_b_rank: number;
  team_b_form: number | null;
  team_b_volatility: number | null;
  projected_winner: ProjectedWinner;
}

export interface HeadToHeadResponse {
  team_a: string;
  team_b: string;
  team_a_score: number;
  team_b_score: number;
  categories: CategoryComparison[];
}

export type RoundOutcome = "W" | "L" | "D";

export interface RoundResult {
  round: number;
  team_a_result: RoundOutcome;
  team_a_score: number;
  team_b_score: number;
  team_b_result: RoundOutcome;
}

export interface MatchupSummary {
  team_a_wins: number;
  team_b_wins: number;
  draws: number;
  team_a_win_pct: number;
  team_b_win_pct: number;
}

export interface RoundStats {
  round: number;
  score: number;
  kicks: number;
  handballs: number;
  marks: number;
  hitouts: number;
  tackles: number;
  cp: number;
  clearances: number;
  r50: number;
  spoils: number;
}

export interface MatchupHistoryResponse {
  team_a: string;
  team_b: string;
  team_a_rounds: RoundStats[];
  team_b_rounds: RoundStats[];
  rounds: RoundResult[];
  summary: MatchupSummary;
}
