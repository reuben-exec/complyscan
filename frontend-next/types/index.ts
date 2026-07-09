export type ComplianceStatus =
  | "Compliant"
  | "Partial"
  | "Non-Compliant"
  | "Not Found";

export interface EvidenceItem {
  evidence_id: string;
  name: string;
  type: string;
  required: boolean;
  critical: boolean;
  status: ComplianceStatus;
  justification: string;
  llm_evaluated: boolean;
  llm_confidence: number | null;
  llm_justification: string | null;
  manually_overridden: boolean;
  override_note: string | null;
  llm_disagreement: boolean;
  llm_reasoning: string | null;
}

export interface RequirementResult {
  requirement_id: string;
  chapter: string;
  title: string;
  description: string;
  criticality: string;
  evidence_items: EvidenceItem[];
  overall_status: ComplianceStatus;
  compliance_score: number;
  disclaimer: string;
}

export interface ChapterInfo {
  code: string;
  name: string;
}

export interface ChapterStats {
  code: string;
  name: string;
  totalRequirements: number;
  avgScore: number;
}

export interface DashboardStats {
  avgScore: number;
  compliant: number;
  partial: number;
  nonCompliant: number;
  notFound: number;
  totalRequirements: number;
  chapters: ChapterStats[];
  documentName?: string;
}

export interface RequirementsResponse {
  chapter: string;
  requirements: { requirement_id: string; title: string; criticality: string }[];
  disclaimer: string;
}

export interface ChaptersResponse {
  chapters: ChapterInfo[];
  disclaimer: string;
}

export interface ExtractTextResponse {
  text: string;
  filename: string;
  format: string;
  char_count: number;
}

export interface OverrideResponse {
  result: RequirementResult;
  disclaimer: string;
}
