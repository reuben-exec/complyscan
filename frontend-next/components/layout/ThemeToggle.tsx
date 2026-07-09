"use client";

import { useTheme } from "@/lib/theme";
import { Sun, Moon } from "@phosphor-icons/react";

export function ThemeToggle() {
  const { theme, toggleTheme, mounted } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="fixed top-4 right-4 z-50 flex items-center justify-center h-9 w-9 rounded-full bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-300 shadow-sm hover:bg-white dark:hover:bg-slate-800 hover:text-slate-700 dark:hover:text-white transition-all"
      aria-label="Toggle theme"
    >
      {mounted && theme === "dark" ? (
        <Sun className="h-4 w-4" weight="fill" />
      ) : (
        <Moon className="h-4 w-4" weight="fill" />
      )}
    </button>
  );
}
