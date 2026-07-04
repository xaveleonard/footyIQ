import type { ReactNode } from "react";

import { ThemeToggle } from "@/components/theme-toggle";

import { BottomTabBar } from "./bottom-tab-bar";
import { Sidebar } from "./sidebar";

export function NavShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b px-4 py-3 md:hidden">
          <span className="text-lg font-semibold tracking-tight">footyIQ</span>
          <ThemeToggle />
        </header>
        <main className="flex-1 px-4 py-6 pb-20 md:px-8 md:py-8 md:pb-8">
          <div className="mx-auto w-full max-w-5xl">{children}</div>
        </main>
      </div>
      <BottomTabBar />
    </div>
  );
}
