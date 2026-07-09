"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Play,
  Sparkle,
  DownloadSimple,
  Spinner,
} from "@phosphor-icons/react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sidebar } from "@/components/layout/Sidebar";
import { EvidenceCard } from "@/components/evidence/EvidenceCard";
import { OverrideModal } from "@/components/evidence/OverrideModal";
import { useAppStore } from "@/lib/store";
import { getRequirements } from "@/lib/api";
import { formatScore, getStatusBg } from "@/lib/utils";
import { toast } from "sonner";
import type { EvidenceItem } from "@/types";

interface RequirementInfo {
  requirement_id: string;
  title: string;
  criticality: string;
}

export default function RequirementClient({
  code,
  reqId,
}: {
  code: string;
  reqId: string;
}) {
  const {
    sidebarCollapsed,
    extractedText,
    results,
    isAnalyzing,
    analyzeKeyword,
    analyzeSemantic,
    overrideEvidence,
    exportReport,
  } = useAppStore();

  const [requirement, setRequirement] = useState<RequirementInfo | null>(null);
  const [overrideModal, setOverrideModal] = useState<{
    open: boolean;
    evidence: EvidenceItem | null;
  }>({ open: false, evidence: null });

  const result = results.find((r) => r.requirement_id === reqId);

  useEffect(() => {
    getRequirements(code).then((res) => {
      const req = res.requirements.find(
        (r) => r.requirement_id === reqId
      );
      if (req) setRequirement(req);
    });
  }, [code, reqId]);

  const handleOverride = (evidenceId: string, newStatus: string, note: string) => {
    if (!result) return;
    overrideEvidence(result, evidenceId, newStatus, note).then(() => {
      toast.success("Evidence status updated");
    });
  };

  const handleExport = () => {
    if (!result) return;
    exportReport(result).then(() => {
      toast.success("Report downloaded");
    });
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main
        className={`flex-1 transition-all duration-300 ${
          sidebarCollapsed ? "ml-16" : "ml-64"
        }`}
      >
        <div className="p-6 pt-20 max-w-[1400px] mx-auto">
          {/* Breadcrumb */}
          <div className="mb-4 flex items-center gap-2 text-sm text-muted-foreground">
            <Link href="/" className="hover:text-foreground transition-colors">
              Dashboard
            </Link>
            <span>/</span>
            <Link
              href={`/chapter/${code}/`}
              className="hover:text-foreground transition-colors"
            >
              {code}
            </Link>
            <span>/</span>
            <span className="text-foreground">{reqId}</span>
          </div>

          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-6">
            <div>
              <h1 className="text-2xl font-display font-bold tracking-tight">
                {requirement?.title || reqId}
              </h1>
              <p className="mt-1 text-sm text-muted-foreground font-mono">
                {reqId} · {requirement?.criticality || "Unknown"} criticality
              </p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button
                variant="outline"
                size="sm"
                onClick={handleExport}
                disabled={!result}
                className="rounded-[2px]"
              >
                <DownloadSimple className="h-4 w-4" weight="bold" />
                Export PDF
              </Button>
            </div>
          </div>

          {/* Split Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Document Text */}
            <div>
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Document Text</CardTitle>
                </CardHeader>
                <CardContent>
                  {extractedText ? (
                    <div className="max-h-[600px] overflow-y-auto text-sm leading-relaxed whitespace-pre-wrap font-body text-foreground/80">
                      {extractedText}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground text-sm">
                      No document uploaded.
                      <br />
                      <Link
                        href="/upload/"
                        className="text-primary hover:underline mt-2 inline-block"
                      >
                        Upload a PDF
                      </Link>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Right: Analysis Results */}
            <div>
              {/* Analysis Controls */}
              <Card className="mb-4">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <Button
                      onClick={() => analyzeKeyword(reqId)}
                      disabled={isAnalyzing || !extractedText}
                      className="rounded-[2px]"
                      size="sm"
                    >
                      {isAnalyzing ? (
                        <Spinner className="h-4 w-4 animate-spin" weight="bold" />
                      ) : (
                        <Play className="h-4 w-4" weight="fill" />
                      )}
                      Quick Scan
                    </Button>
                    <Button
                      onClick={() => analyzeSemantic(reqId)}
                      disabled={isAnalyzing || !extractedText}
                      variant="outline"
                      className="rounded-[2px]"
                      size="sm"
                    >
                      {isAnalyzing ? (
                        <Spinner className="h-4 w-4 animate-spin" weight="bold" />
                      ) : (
                        <Sparkle className="h-4 w-4" weight="fill" />
                      )}
                      Deep Analysis
                    </Button>
                    {!extractedText && (
                      <span className="text-xs text-muted-foreground">
                        Upload a document first
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Results */}
              {result && (
                <>
                  {/* Score Summary */}
                  <Card className="mb-4">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <Badge className={getStatusBg(result.overall_status)}>
                          {result.overall_status}
                        </Badge>
                        <span className="text-lg font-display font-bold">
                          {formatScore(result.compliance_score)}
                        </span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary score-bar-fill rounded-full"
                          style={
                            {
                              "--score-width": `${result.compliance_score * 100}%`,
                            } as React.CSSProperties
                          }
                        />
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        {result.evidence_items.length} evidence items evaluated
                      </p>
                    </CardContent>
                  </Card>

                  {/* Evidence List */}
                  <div className="space-y-3">
                    {result.evidence_items.map((ev) => (
                      <EvidenceCard
                        key={ev.evidence_id}
                        evidence={ev}
                        onOverride={(e) =>
                          setOverrideModal({ open: true, evidence: e })
                        }
                      />
                    ))}
                  </div>

                  {/* Disclaimer */}
                  <p className="text-xs text-muted-foreground text-center py-4 mt-4 border-t border-border">
                    {result.disclaimer}
                  </p>
                </>
              )}

              {!result && !isAnalyzing && (
                <Card>
                  <CardContent className="p-12 text-center">
                    <Sparkle className="h-8 w-8 mx-auto text-muted-foreground mb-3" weight="light" />
                    <p className="text-sm text-muted-foreground">
                      Run a scan to analyze this requirement against your
                      document.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Override Modal */}
      <OverrideModal
        open={overrideModal.open}
        onOpenChange={(open) => setOverrideModal({ ...overrideModal, open })}
        evidence={overrideModal.evidence}
        onSubmit={handleOverride}
      />
    </div>
  );
}
