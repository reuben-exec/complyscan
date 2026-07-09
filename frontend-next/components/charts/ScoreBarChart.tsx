"use client";

import { formatScore, getScoreColor } from "@/lib/utils";
import type { RequirementResult } from "@/types";

interface ScoreBarChartProps {
  results: RequirementResult[];
  limit?: number;
}

export function ScoreBarChart({ results, limit = 10 }: ScoreBarChartProps) {
  const sorted = [...results]
    .sort((a, b) => a.compliance_score - b.compliance_score)
    .slice(0, limit);

  if (sorted.length === 0) {
    return (
      <div className="flex items-center justify-center h-[200px] text-muted-foreground text-sm">
        No analysis data yet
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {sorted.map((r, i) => (
        <div key={r.requirement_id} className="flex items-center gap-3">
          <span className="text-xs font-mono text-muted-foreground w-20 shrink-0 truncate">
            {r.requirement_id}
          </span>
          <div className="flex-1 h-5 bg-muted rounded-[2px] overflow-hidden">
            <div
              className={`h-full ${getScoreColor(r.compliance_score)} score-bar-fill rounded-[2px]`}
              style={{ "--score-width": `${r.compliance_score * 100}%` } as React.CSSProperties}
            />
          </div>
          <span className="text-xs font-medium w-10 text-right shrink-0">
            {formatScore(r.compliance_score)}
          </span>
        </div>
      ))}
    </div>
  );
}
