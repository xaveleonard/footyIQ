import { BarChart3, ListOrdered, Swords, Trophy } from "lucide-react";
import type { ComponentType } from "react";

export interface NavItem {
  href: string;
  label: string;
  icon: ComponentType<{ className?: string }>;
}

export const NAV_ITEMS: NavItem[] = [
  { href: "/rankings", label: "Rankings", icon: Trophy },
  { href: "/leaderboards", label: "Leaderboards", icon: ListOrdered },
  { href: "/team-analysis", label: "Teams", icon: BarChart3 },
  { href: "/matchups", label: "Matchups", icon: Swords },
];
