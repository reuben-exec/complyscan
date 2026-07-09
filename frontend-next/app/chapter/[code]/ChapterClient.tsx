"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ArrowRight } from "@phosphor-icons/react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sidebar } from "@/components/layout/Sidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAppStore } from "@/lib/store";
import { getRequirements } from "@/lib/api";
import { formatScore, getStatusBg } from "@/lib/utils";

interface Requirement {
  requirement_id: string;
  title: string;
  criticality: string;
}

const criticalityColors: Record<string, string> = {
  Critical: "destructive",
  High: "secondary",
  Medium: "outline",
  Low: "outline",
};

export default function ChapterClient({ code }: { code: string }) {
  const { sidebarCollapsed, results, setActiveChapter } = useAppStore();
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [disclaimer, setDisclaimer] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setActiveChapter(code);
    setLoading(true);
    getRequirements(code)
      .then((res) => {
        setRequirements(res.requirements);
        setDisclaimer(res.disclaimer);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [code, setActiveChapter]);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main
        className={`flex-1 transition-all duration-300 ${
          sidebarCollapsed ? "ml-16" : "ml-64"
        }`}
      >
        <div className="p-6 pt-20 max-w-[1400px] mx-auto">
          <div className="mb-4">
            <Link
              href="/"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1"
            >
              <ArrowLeft className="h-3 w-3" weight="bold" />
              Dashboard
            </Link>
          </div>

          <PageHeader
            title={`${code} — Requirements`}
            subtitle={disclaimer}
          />

          {loading && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="h-32 bg-muted rounded-[2px] animate-shimmer bg-[length:200%_100%]"
                />
              ))}
            </div>
          )}

          {error && (
            <div className="text-center py-12 text-destructive">{error}</div>
          )}

          {!loading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {requirements.map((req, i) => {
                const result = results.find(
                  (r) => r.requirement_id === req.requirement_id
                );
                return (
                  <Link
                    key={req.requirement_id}
                    href={`/chapter/${code}/${req.requirement_id}/`}
                  >
                    <Card
                      className={`glass-hover cursor-pointer animate-fade-in h-full ${
                        i < 6 ? `stagger-${i + 1}` : ""
                      }`}
                    >
                      <CardContent className="p-5">
                        <div className="flex items-start justify-between gap-2 mb-3">
                          <span className="font-mono text-xs text-muted-foreground">
                            {req.requirement_id}
                          </span>
                          <Badge
                            variant={
                              (criticalityColors[req.criticality] as
                                | "destructive"
                                | "secondary"
                                | "outline") || "outline"
                            }
                            className="text-[10px]"
                          >
                            {req.criticality}
                          </Badge>
                        </div>
                        <h3 className="text-sm font-medium leading-snug mb-3">
                          {req.title}
                        </h3>

                        {result ? (
                          <div className="flex items-center justify-between">
                            <Badge
                              className={getStatusBg(result.overall_status)}
                            >
                              {result.overall_status}
                            </Badge>
                            <span className="text-xs font-medium">
                              {formatScore(result.compliance_score)}
                            </span>
                          </div>
                        ) : (
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-muted-foreground">
                              Not analyzed
                            </span>
                            <ArrowRight className="h-3 w-3 text-muted-foreground" weight="bold" />
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
