"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  SquaresFour,
  CloudArrowUp,
  CaretLeft,
  CaretRight,
  ShieldCheck,
  Heartbeat,
} from "@phosphor-icons/react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/lib/store";
import { getChapters } from "@/lib/api";
import type { ChapterInfo } from "@/types";
import { Logo } from "@/components/layout/Logo";

const chapterIcons: Record<string, React.ReactNode> = {
  HIC: <Heartbeat className="h-4 w-4" weight="fill" />,
  PRE: <ShieldCheck className="h-4 w-4" weight="fill" />,
};

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useAppStore();
  const [chapters, setChapters] = useState<ChapterInfo[]>([]);

  useEffect(() => {
    getChapters()
      .then((res) => setChapters(res.chapters))
      .catch(() => {
        setChapters([
          { code: "HIC", name: "Hospital Infection Control" },
          { code: "PRE", name: "Patient Rights & Education" },
        ]);
      });
  }, []);

  const isActive = (path: string) => pathname === `${path}/` || pathname === `${path}`;

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-sidebar text-sidebar-foreground transition-all duration-300 flex flex-col pb-16",
        sidebarCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Brand */}
      <div className="flex items-center px-4 h-16 border-b border-border shrink-0">
        <Logo collapsed={sidebarCollapsed} />
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        <Link
          href="/"
          className={cn(
            "flex items-center gap-3 px-3 py-2.5 rounded-[2px] text-sm font-medium transition-all",
            isActive("")
              ? "bg-sidebar-accent/20 text-sidebar-accent"
              : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-slate-100 dark:hover:bg-white/5"
          )}
        >
          <SquaresFour className="h-4 w-4 shrink-0" weight="bold" />
          {!sidebarCollapsed && <span>Dashboard</span>}
        </Link>

        <Link
          href="/upload/"
          className={cn(
            "flex items-center gap-3 px-3 py-2.5 rounded-[2px] text-sm font-medium transition-all",
            isActive("/upload")
              ? "bg-sidebar-accent/20 text-sidebar-accent"
              : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-slate-100 dark:hover:bg-white/5"
          )}
        >
          <CloudArrowUp className="h-4 w-4 shrink-0" />
          {!sidebarCollapsed && <span>Upload</span>}
        </Link>

        {!sidebarCollapsed && (
          <div className="pt-4 pb-2 px-3">
            <span className="text-[11px] font-semibold uppercase tracking-widest text-sidebar-foreground/40">
              Chapters
            </span>
          </div>
        )}

        {chapters.map((ch) => (
          <Link
            key={ch.code}
            href={`/chapter/${ch.code}/`}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-[2px] text-sm font-medium transition-all",
              pathname?.includes(`/chapter/${ch.code}`)
                ? "bg-sidebar-accent/20 text-sidebar-accent"
                : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-slate-100 dark:hover:bg-white/5"
            )}
          >
            {chapterIcons[ch.code] || <SquaresFour className="h-4 w-4 shrink-0" />}
            {!sidebarCollapsed && <span>{ch.code}</span>}
          </Link>
        ))}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t border-border p-2 shrink-0">
        <button
          onClick={toggleSidebar}
          className="flex items-center justify-center w-full h-8 rounded-[2px] text-slate-400 dark:text-white/50 hover:text-slate-700 dark:hover:text-white/80 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
        >
          {sidebarCollapsed ? (
            <CaretRight className="h-4 w-4" weight="bold" />
          ) : (
            <CaretLeft className="h-4 w-4" weight="bold" />
          )}
        </button>
      </div>

      {/* Version */}
      {!sidebarCollapsed && (
        <div className="px-4 py-3 border-t border-border text-[11px] text-sidebar-foreground/30 shrink-0">
          v0.1.0 MVP
        </div>
      )}
    </aside>
  );
}
