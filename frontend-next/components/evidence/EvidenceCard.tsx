"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { EvidenceItem } from "@/types";
import {
  Robot,
  Warning,
  CheckCircle,
  FileText,
  Info,
  CaretDown,
  CaretRight,
  Lightning,
} from "@phosphor-icons/react/dist/ssr";

interface EvidenceCardProps {
  evidence: EvidenceItem;
  onOverride?: (item: EvidenceItem) => void;
}

function getConfidenceColor(confidence: number | null) {
  if (confidence === null) return "text-neutral-500 dark:text-neutral-400";
  if (confidence >= 0.75) return "text-emerald-600 dark:text-emerald-400";
  if (confidence >= 0.5) return "text-amber-600 dark:text-amber-400";
  return "text-rose-600 dark:text-rose-400";
}

function getConfidenceBg(confidence: number | null) {
  if (confidence === null) return "bg-neutral-100 dark:bg-slate-700 text-neutral-500 dark:text-neutral-400";
  if (confidence >= 0.75) return "bg-emerald-50 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-700";
  if (confidence >= 0.5) return "bg-amber-50 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-700";
  return "bg-rose-50 dark:bg-rose-900/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-700";
}

function getConfidenceLabel(confidence: number | null) {
  if (confidence === null) return "No Data";
  if (confidence >= 0.75) return "High";
  if (confidence >= 0.5) return "Medium";
  return "Low";
}

export function EvidenceCard({ evidence: item, onOverride }: EvidenceCardProps) {
  const [reasoningOpen, setReasoningOpen] = useState(false);

  const hasLlmData = item.llm_evaluated || item.llm_confidence !== null;
  const confidence = item.llm_confidence ?? 0;
  const hasReasoning = item.llm_reasoning && item.llm_reasoning.trim().length > 0;

  return (
    <Card className="relative overflow-hidden">
      <div className="p-3.5 sm:p-4">
        <div className="flex items-start gap-3">
          <div
            className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${
              item.status === "Compliant"
                ? "bg-emerald-100 text-emerald-600"
                : item.status === "Partial"
                  ? "bg-amber-100 text-amber-600"
                  : item.status === "Non-Compliant"
                    ? "bg-rose-100 text-rose-600"
                    : "bg-neutral-100 text-neutral-500"
            }`}
          >
            {item.status === "Compliant" ? (
              <CheckCircle className="h-3.5 w-3.5" weight="fill" />
            ) : item.status === "Partial" ? (
              <Warning className="h-3.5 w-3.5" weight="fill" />
            ) : item.status === "Non-Compliant" ? (
              <Warning className="h-3.5 w-3.5" weight="fill" />
            ) : (
              <FileText className="h-3.5 w-3.5" weight="regular" />
            )}
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0 flex-1">
                <div className="mb-1.5 flex items-center gap-2 flex-wrap">
                  <h4 className="text-sm font-semibold text-neutral-800 dark:text-neutral-100 leading-tight">
                    {item.name}
                  </h4>
                  <Badge variant={item.required ? "destructive" : "secondary"} className="shrink-0">
                    {item.required ? "Required" : "Optional"}
                  </Badge>
                </div>

                <div className="mb-2.5 flex items-center gap-1.5 flex-wrap">
                  <Badge variant="outline" className="capitalize">
                    {item.type}
                  </Badge>
                  <Badge variant={statusToVariant(item.status)}>{item.status}</Badge>
                  {item.critical && (
                    <Badge variant="destructive">
                      <Lightning className="mr-0.5 h-2.5 w-2.5" weight="fill" />
                      Critical
                    </Badge>
                  )}
                </div>
              </div>
            </div>

            {item.manually_overridden && (
              <div className="mb-2.5 flex items-center gap-1.5 rounded bg-blue-50 dark:bg-blue-950/50 px-2 py-1.5 text-xs text-blue-700 dark:text-blue-300 border border-blue-100 dark:border-blue-800">
                <Info className="h-3.5 w-3.5 shrink-0" weight="fill" />
                <span className="font-medium">Manually overridden</span>
                {item.override_note && (
                  <span className="text-blue-500 ml-0.5">: {item.override_note}</span>
                )}
              </div>
            )}

            {item.justification && (
              <div className="mb-2">
                <p className="text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed">
                  {item.justification}
                </p>
              </div>
            )}

            {item.llm_disagreement && hasLlmData && (
              <div className="mb-2 flex items-center gap-1.5 rounded bg-orange-50 dark:bg-orange-950/50 px-2 py-1.5 text-xs text-orange-700 dark:text-orange-300 border border-orange-200 dark:border-orange-800">
                <Warning className="h-3.5 w-3.5 shrink-0" weight="fill" />
                <span className="font-medium">High disagreement</span>
                <span className="text-orange-500 ml-0.5">
                  - LLM overrode initial analysis. Review recommended.
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* LLM Assessment Panel */}
      {hasLlmData && (
        <div className="border-t border-indigo-100 dark:border-indigo-800 bg-indigo-50/30 dark:bg-indigo-950/30 px-3.5 sm:px-4 py-3">
          <div className="flex items-center gap-1.5 mb-2">
            <Robot className="h-4 w-4 text-indigo-500 dark:text-indigo-400" weight="regular" />
            <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
              LLM Assessment
            </span>
          </div>

          <div className="space-y-2">
            {/* Confidence Level Badge */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-500 dark:text-neutral-400">Confidence Level</span>
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${getConfidenceBg(confidence)}`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${getConfidenceColor(confidence).replace(/text-/g, "bg-")}`} />
                {getConfidenceLabel(confidence)}
              </span>
            </div>

            {/* Confidence Bar */}
            <div className="h-1.5 w-full rounded-full bg-neutral-100 dark:bg-slate-700">
              <div
                className={`h-1.5 rounded-full transition-all ${
                  confidence >= 0.75
                    ? "bg-emerald-500"
                    : confidence >= 0.5
                      ? "bg-amber-500"
                      : "bg-rose-500"
                }`}
                style={{ width: `${Math.round(confidence * 100)}%` }}
              />
            </div>

            {/* Confidence % */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-500 dark:text-neutral-400">Confidence</span>
              <span className={`text-xs font-semibold ${getConfidenceColor(confidence)}`}>
                {Math.round(confidence * 100)}%
              </span>
            </div>

            {/* Justification */}
            {item.llm_justification && (
              <div className="pt-1">
                <span className="text-xs font-medium text-neutral-500 dark:text-neutral-400 block mb-1">
                  Assessment
                </span>
                <p className="text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed bg-white dark:bg-slate-800 rounded-md p-2 border border-neutral-100 dark:border-slate-600">
                  {item.llm_justification}
                </p>
              </div>
            )}

            {/* Chain-of-Thought Reasoning (collapsible) */}
            {hasReasoning && (
              <div className="pt-1">
                <button
                  onClick={() => setReasoningOpen(!reasoningOpen)}
                  className="flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 transition-colors cursor-pointer w-full text-left"
                >
                  {reasoningOpen ? (
                    <CaretDown className="h-3 w-3" weight="bold" />
                  ) : (
                    <CaretRight className="h-3 w-3" weight="bold" />
                  )}
                  <span>Chain-of-thought Reasoning</span>
                </button>
                {reasoningOpen && (
                  <div className="mt-1.5 bg-indigo-50/50 dark:bg-indigo-950/50 rounded-md p-2 border border-indigo-100 dark:border-indigo-800">
                    <p className="text-[11px] text-neutral-600 dark:text-neutral-400 leading-relaxed whitespace-pre-wrap">
                      {item.llm_reasoning}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}

function statusToVariant(status: string) {
  switch (status) {
    case "Compliant":
      return "default";
    case "Partial":
      return "secondary";
    case "Non-Compliant":
      return "destructive";
    case "Not Found":
      return "outline";
    default:
      return "outline";
  }
}
