import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "Compliant":
      return "text-status-compliant";
    case "Partial":
      return "text-status-partial";
    case "Non-Compliant":
      return "text-status-noncompliant";
    case "Not Found":
      return "text-status-notfound";
    default:
      return "text-muted-foreground";
  }
}

export function getStatusBg(status: string): string {
  switch (status) {
    case "Compliant":
      return "bg-status-compliant/10 text-status-compliant";
    case "Partial":
      return "bg-status-partial/10 text-status-partial";
    case "Non-Compliant":
      return "bg-status-noncompliant/10 text-status-noncompliant";
    case "Not Found":
      return "bg-status-notfound/10 text-status-notfound";
    default:
      return "bg-muted text-muted-foreground";
  }
}

/**
 * UI-only score-to-color thresholds.
 * Deliberately lower than backend thresholds (0.80/0.50) for visual comfort:
 *   COMPLIANT >= 0.70, PARTIAL >= 0.40, NON_COMPLIANT > 0
 * These affect only CSS colors, not compliance logic.
 * See backend/core/config.py for authoritative score thresholds.
 */
export function getScoreColor(score: number): string {
  if (score >= 0.7) return "bg-status-compliant";
  if (score >= 0.4) return "bg-status-partial";
  if (score > 0) return "bg-status-noncompliant";
  return "bg-status-notfound";
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
