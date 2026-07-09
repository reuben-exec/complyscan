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
 * Temperature-based compliance color (continuous gradient).
 * Maps score 0→1 to red→amber→green using HSL interpolation
 * through the same 3 color stops used in the compliance gauge:
 *   0.0 → red   (hsl(0,   72%, 51%))
 *   0.5 → amber (hsl(38,  92%, 50%))
 *   1.0 → green (hsl(142, 71%, 45%))
 * Returns an HSL string suitable for inline `style` props.
 */
export function getComplianceColor(score: number): string {
  const clamped = Math.max(0, Math.min(1, score));

  let hue: number, sat: number, light: number;

  if (clamped <= 0.5) {
    const t = clamped / 0.5; // 0→1
    hue = 0 + t * 38;
    sat = 72 + t * (92 - 72);
    light = 51 + t * (50 - 51);
  } else {
    const t = (clamped - 0.5) / 0.5; // 0→1
    hue = 38 + t * (142 - 38);
    sat = 92 + t * (71 - 92);
    light = 50 + t * (45 - 50);
  }

  return `hsl(${hue.toFixed(0)}, ${sat.toFixed(0)}%, ${light.toFixed(0)}%)`;
}

/**
 * UI-only score-to-color thresholds (returns Tailwind class names).
 * Deliberately lower than backend thresholds (0.80/0.50) for visual comfort:
 *   COMPLIANT >= 0.70, PARTIAL >= 0.40, NON_COMPLIANT > 0
 * These affect only CSS colors, not compliance logic.
 * See backend/core/config.py for authoritative score thresholds.
 * NOTE: For inline `style` props use getComplianceColor() instead.
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
