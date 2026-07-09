import type {
  ChaptersResponse,
  RequirementsResponse,
  RequirementResult,
  ExtractTextResponse,
  OverrideResponse,
  DashboardStats,
  ChapterStats,
} from "@/types";

const API_BASE = "/api";

/** Read persisted Zustand store from localStorage and compute dashboard stats. */
export function getDashboardStats(): DashboardStats {
  // Default empty stats
  const empty: DashboardStats = {
    avgScore: 0,
    compliant: 0,
    partial: 0,
    nonCompliant: 0,
    notFound: 0,
    totalRequirements: 0,
    chapters: [],
    documentName: undefined,
  };

  try {
    const raw = localStorage.getItem("complyscan-storage");
    if (!raw) return empty;

    const parsed = JSON.parse(raw);
    // Zustand persist wraps state in { state: { ... }, version: N }
    const state = parsed?.state ?? parsed;
    const results: RequirementResult[] = state?.results ?? [];
    const documentName: string | undefined = state?.documentName || undefined;

    if (results.length === 0) return { ...empty, documentName };

    // Aggregate stats from all results
    let compliant = 0;
    let partial = 0;
    let nonCompliant = 0;
    let notFound = 0;
    let totalScore = 0;
    let totalEvidence = 0;

    for (const r of results) {
      switch (r.overall_status) {
        case "Compliant":
          compliant++;
          break;
        case "Partial":
          partial++;
          break;
        case "Non-Compliant":
          nonCompliant++;
          break;
        case "Not Found":
          notFound++;
          break;
      }
      totalScore += r.compliance_score;
      totalEvidence += r.evidence_items?.length ?? 0;
    }

    const avgScore = results.length > 0 ? totalScore / results.length : 0;

    // Group by chapter
    const chapterMap = new Map<
      string,
      { code: string; name: string; totalRequirements: number; scoreSum: number }
    >();

    for (const r of results) {
      const existing = chapterMap.get(r.chapter);
      if (existing) {
        existing.totalRequirements++;
        existing.scoreSum += r.compliance_score;
      } else {
        chapterMap.set(r.chapter, {
          code: r.chapter,
          name: r.chapter, // Will be overridden below if we have a name map
          totalRequirements: 1,
          scoreSum: r.compliance_score,
        });
      }
    }

    // Fetch chapter names from the API (synchronous fetch for names)
    const chapterNames: Record<string, string> = {
      HIC: "Hospital Infection Control",
      PRE: "Patient Rights & Education",
    };

    const chapters: ChapterStats[] = Array.from(chapterMap.values()).map(
      (ch) => ({
        code: ch.code,
        name: chapterNames[ch.code] ?? ch.name,
        totalRequirements: ch.totalRequirements,
        avgScore: ch.totalRequirements > 0 ? ch.scoreSum / ch.totalRequirements : 0,
      })
    );

    return {
      avgScore,
      compliant,
      partial,
      nonCompliant,
      notFound,
      totalRequirements: totalEvidence,
      chapters,
      documentName,
    };
  } catch {
    return empty;
  }
}

export async function getChapters(): Promise<ChaptersResponse> {
  const res = await fetch(`${API_BASE}/chapters`);
  if (!res.ok) throw new Error("Failed to fetch chapters");
  return res.json();
}

export async function getRequirements(
  chapter: string
): Promise<RequirementsResponse> {
  const res = await fetch(`${API_BASE}/requirements/${chapter}`);
  if (!res.ok) throw new Error(`Failed to fetch requirements for ${chapter}`);
  return res.json();
}

export async function extractText(file: File): Promise<ExtractTextResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/extract-text`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Failed to extract text");
  }
  return res.json();
}

export async function analyzeText(
  requirementId: string,
  text: string
): Promise<RequirementResult> {
  const res = await fetch(`${API_BASE}/analyze-text/${requirementId}`, {
    method: "POST",
    headers: { "Content-Type": "text/plain" },
    body: text,
  });
  if (!res.ok) throw new Error(`Analysis failed for ${requirementId}`);
  return res.json();
}

export async function analyzeSemantic(
  requirementId: string,
  text: string
): Promise<RequirementResult> {
  const res = await fetch(`${API_BASE}/analyze-semantic/${requirementId}`, {
    method: "POST",
    headers: { "Content-Type": "text/plain" },
    body: text,
  });
  if (!res.ok) throw new Error(`Semantic analysis failed for ${requirementId}`);
  return res.json();
}

export async function overrideEvidence(
  result: RequirementResult,
  evidenceId: string,
  newStatus: string,
  overrideNote: string
): Promise<OverrideResponse> {
  const res = await fetch(`${API_BASE}/override`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ result, evidence_id: evidenceId, new_status: newStatus, override_note: overrideNote }),
  });
  if (!res.ok) throw new Error("Override failed");
  return res.json();
}

export async function generateReport(
  result: RequirementResult
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(result),
  });
  if (!res.ok) throw new Error("Report generation failed");
  return res.blob();
}
