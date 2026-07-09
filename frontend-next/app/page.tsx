"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  ArrowRight,
  CheckCircle,
  Warning,
  TrendUp,
  FileText,
  Files,
  ShieldCheck,
  ArrowSquareOut,
  X,
} from "@phosphor-icons/react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ComplianceGauge } from "@/components/charts/ComplianceGauge";
import { StatusDonut } from "@/components/charts/StatusDonut";
import { Sidebar } from "@/components/layout/Sidebar";
import { formatScore, getComplianceColor } from "@/lib/utils";
import { useAppStore } from "@/lib/store";
import { getDashboardStats } from "@/lib/api";
import type { DashboardStats } from "@/types";

export default function DashboardPage() {
  const { sidebarCollapsed, results, clearDocument } = useAppStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);

  // Recompute stats whenever results change
  const recompute = useCallback(() => {
    setStats(getDashboardStats());
  }, []);

  useEffect(() => {
    recompute();
  }, [recompute, results]);

  // Also recompute on focus (in case localStorage changed from another tab)
  useEffect(() => {
    const handler = () => recompute();
    window.addEventListener("focus", handler);
    return () => window.removeEventListener("focus", handler);
  }, [recompute]);

  const isEmpty = !stats || (stats.compliant === 0 && stats.partial === 0 && stats.nonCompliant === 0 && stats.notFound === 0);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main
        className={`flex-1 transition-all duration-300 ${
          sidebarCollapsed ? "ml-16" : "ml-64"
        }`}
      >
        <div className="max-w-[1200px] mx-auto px-6 py-8 pt-20">
          {/* Hero Band */}
          <Card className="mb-8 animate-fade-in overflow-hidden">
            <div className="relative bg-white dark:bg-slate-900 bg-gradient-to-br from-primary/5 via-primary/10 to-primary/5 p-8">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-2xl font-display font-bold tracking-tight text-foreground">
                    Welcome to ComplyScan
                  </h1>
                  <p className="text-sm text-muted-foreground mt-1.5 max-w-xl">
                    NABH compliance analysis engine. Upload a policy document,
                    analyze it against accreditation requirements, and generate
                    audit-ready reports.
                  </p>
                </div>
                <ShieldCheck className="h-10 w-10 text-primary/20 shrink-0" weight="fill" />
              </div>
              {stats?.documentName && (
                <div className="mt-4 flex items-center gap-2">
                  <Badge variant="secondary" className="font-mono text-xs gap-1.5">
                    <FileText className="h-3 w-3" />
                    {stats.documentName}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {results.length} requirement{results.length !== 1 ? "s" : ""} analyzed
                  </Badge>
                  <button
                    onClick={() => {
                      clearDocument();
                      setStats(null);
                    }}
                    className="ml-1 flex items-center justify-center h-5 w-5 rounded-full text-muted-foreground/50 hover:text-destructive hover:bg-destructive/10 transition-colors"
                    aria-label="Remove document"
                    title="Remove document and clear all analysis"
                  >
                    <X className="h-3 w-3" weight="bold" />
                  </button>
                </div>
              )}
              {!stats?.documentName && (
                <div className="mt-4">
                  <Link
                    href="/upload"
                    className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
                  >
                    <FileText className="h-4 w-4" />
                    Upload a document to get started
                  </Link>
                </div>
              )}
            </div>
          </Card>

          {isEmpty ? (
            /* Empty state */
            <div className="grid grid-cols-1 gap-8">
              <Card className="animate-fade-in">
                <CardContent className="p-12 flex flex-col items-center text-center gap-4">
                  <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                    <Files className="h-8 w-8 text-primary/40" weight="bold" />
                  </div>
                  <div>
                    <h3 className="font-display font-semibold text-foreground text-lg">
                      No Data Analyzed Yet
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1 max-w-md">
                      Upload a healthcare policy document and run compliance
                      analysis to see your dashboard populate with real data.
                    </p>
                  </div>
                  <Link
                    href="/upload"
                    className="mt-2 inline-flex items-center gap-2 px-4 py-2 rounded-[2px] bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
                  >
                    <FileText className="h-4 w-4" />
                    Upload Document
                  </Link>
                </CardContent>
              </Card>
            </div>
          ) : (
            /* Dashboard with data */
            <div className="space-y-8">
              {/* Gauge + Donut Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="animate-fade-in stagger-1">
                  <CardContent className="p-6 flex flex-col items-center">
                    <h3 className="text-sm font-display font-semibold text-foreground mb-2 self-start">
                      Overall Compliance
                    </h3>
                    <ComplianceGauge score={stats!.avgScore} size={220} />
                  </CardContent>
                </Card>

                <Card className="animate-fade-in stagger-2">
                  <CardContent className="p-6">
                    <h3 className="text-sm font-display font-semibold text-foreground mb-4">
                      Status Breakdown
                    </h3>
                    <StatusDonut
                      compliant={stats!.compliant}
                      partial={stats!.partial}
                      nonCompliant={stats!.nonCompliant}
                      notFound={stats!.notFound}
                    />
                  </CardContent>
                </Card>
              </div>

              {/* KPI Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card className="animate-fade-in stagger-3">
                  <CardContent className="p-5 flex items-center gap-3">
                    <div className="h-10 w-10 rounded-[2px] bg-primary/10 flex items-center justify-center shrink-0">
                      <Files className="h-5 w-5 text-primary" weight="bold" />
                    </div>
                    <div>
                      <p className="text-xl font-display font-bold text-foreground">
                        {stats!.totalRequirements}
                      </p>
                      <p className="text-[11px] text-muted-foreground">Evidence Items</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="animate-fade-in stagger-4">
                  <CardContent className="p-5 flex items-center gap-3">
                    <div className="h-10 w-10 rounded-[2px] bg-green-500/10 flex items-center justify-center shrink-0">
                      <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" weight="fill" />
                    </div>
                    <div>
                      <p className="text-xl font-display font-bold text-foreground">
                        {stats!.compliant}
                      </p>
                      <p className="text-[11px] text-muted-foreground">Compliant</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="animate-fade-in stagger-5">
                  <CardContent className="p-5 flex items-center gap-3">
                    <div className="h-10 w-10 rounded-[2px] bg-yellow-500/10 flex items-center justify-center shrink-0">
                      <Warning className="h-5 w-5 text-yellow-600 dark:text-yellow-400" weight="fill" />
                    </div>
                    <div>
                      <p className="text-xl font-display font-bold text-foreground">
                        {stats!.partial}
                      </p>
                      <p className="text-[11px] text-muted-foreground">Partial</p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="animate-fade-in stagger-6">
                  <CardContent className="p-5 flex items-center gap-3">
                    <div className="h-10 w-10 rounded-[2px] bg-red-500/10 flex items-center justify-center shrink-0">
                      <Warning className="h-5 w-5 text-red-600 dark:text-red-400" weight="fill" />
                    </div>
                    <div>
                      <p className="text-xl font-display font-bold text-foreground">
                        {stats!.nonCompliant}
                      </p>
                      <p className="text-[11px] text-muted-foreground">Non-Compliant</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Chapter Progress */}
              {stats!.chapters.length > 0 && (
                <Card className="animate-fade-in stagger-7">
                  <CardContent className="p-6">
                    <h3 className="text-sm font-display font-semibold text-foreground mb-4">
                      Chapter Progress
                    </h3>
                    <div className="space-y-4">
                      {stats!.chapters.map((ch) => (
                        <Link
                          key={ch.code}
                          href={`/chapter/${ch.code}`}
                          className="block group"
                        >
                          <div className="flex items-center justify-between mb-1.5">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
                                {ch.code}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {ch.name}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-[10px] font-mono">
                                {ch.totalRequirements} items
                              </Badge>
                              <span className="text-sm font-mono font-semibold" style={{ color: getComplianceColor(ch.avgScore) }}>
                                {formatScore(ch.avgScore)}
                              </span>
                            </div>
                          </div>
                          <div className="h-2.5 bg-secondary rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-700 ease-out"
                              style={{
                                width: `${Math.max(Math.round(ch.avgScore * 100), 2)}%`,
                                backgroundColor: getComplianceColor(ch.avgScore),
                              }}
                            />
                          </div>
                        </Link>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Chapter Explorer */}
              <Card className="animate-fade-in stagger-8">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-display font-semibold text-foreground">
                      Chapter Explorer
                    </h3>
                    <TrendUp className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {[
                      { code: "HIC", name: "Hospital Infection Control" },
                      { code: "PRE", name: "Patient Rights & Education" },
                    ].map((ch) => (
                      <Link
                        key={ch.code}
                        href={`/chapter/${ch.code}`}
                        className="flex items-center justify-between p-4 rounded-[2px] bg-secondary/50 hover:bg-secondary transition-colors group border border-transparent hover:border-border"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-[2px] bg-primary/10 flex items-center justify-center">
                            <FileText className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-display font-semibold text-foreground text-sm">
                              {ch.code}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {ch.name}
                            </p>
                          </div>
                        </div>
                        <ArrowSquareOut className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                      </Link>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
