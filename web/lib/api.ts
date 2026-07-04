import type {
  CategoryRecord,
  HeadToHeadResponse,
  LeaderboardEntry,
  MatchupHistoryResponse,
  PowerRankingEntry,
  RankingsWindow,
  TeamDetail,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function apiFetch<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(path, API_BASE_URL);

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      url.searchParams.set(key, value);
    }
  }

  const response = await fetch(url.toString(), { cache: "no-store" });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body?.detail ?? response.statusText);
  }

  return response.json() as Promise<T>;
}

export function getTeams(): Promise<string[]> {
  return apiFetch<string[]>("/teams");
}

export function getTeamDetail(teamName: string): Promise<TeamDetail> {
  return apiFetch<TeamDetail>(`/teams/${encodeURIComponent(teamName)}`);
}

export function getPowerRankings(window: RankingsWindow = "season"): Promise<PowerRankingEntry[]> {
  return apiFetch<PowerRankingEntry[]>("/rankings/power", { window });
}

export function getLeaderboard(
  category: string,
  window: RankingsWindow = "season"
): Promise<LeaderboardEntry[]> {
  return apiFetch<LeaderboardEntry[]>(`/rankings/leaderboards/${encodeURIComponent(category)}`, {
    window,
  });
}

export function getAllLeaderboards(
  window: RankingsWindow = "season"
): Promise<Record<string, LeaderboardEntry[]>> {
  return apiFetch<Record<string, LeaderboardEntry[]>>("/rankings/leaderboards", { window });
}

export function getLeagueRecords(): Promise<CategoryRecord[]> {
  return apiFetch<CategoryRecord[]>("/rankings/records");
}

export function getHeadToHead(teamA: string, teamB: string): Promise<HeadToHeadResponse> {
  return apiFetch<HeadToHeadResponse>("/matchups/head-to-head", { team_a: teamA, team_b: teamB });
}

export function getMatchupHistory(teamA: string, teamB: string): Promise<MatchupHistoryResponse> {
  return apiFetch<MatchupHistoryResponse>("/matchups/history", { team_a: teamA, team_b: teamB });
}
