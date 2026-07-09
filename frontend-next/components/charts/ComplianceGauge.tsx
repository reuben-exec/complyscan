"use client";

import dynamic from "next/dynamic";
import { formatScore } from "@/lib/utils";

const GaugeComponent = dynamic(() => import("react-gauge-component"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center" style={{ width: 200, height: 130 }}>
      <div className="animate-pulse text-muted-foreground text-sm">Loading gauge...</div>
    </div>
  ),
});

interface ComplianceGaugeProps {
  score: number; // 0-1
  size?: number;
  label?: string;
}

export function ComplianceGauge({
  score,
  size = 200,
  label = "Compliance",
}: ComplianceGaugeProps) {
  const percentage = Math.round(score * 100);

  // Height is ~65% of width for semicircle + label space
  const height = Math.round(size * 0.65);

  return (
    <div
      className="flex flex-col items-center"
      style={{ width: size, height }}
    >
      <GaugeComponent
        type="semicircle"
        arc={{
          width: 0.2,
          padding: 0.005,
          subArcs: [
            {
              limit: 30,
              color: "hsl(var(--status-noncompliant))",
              showTick: true,
              tooltip: { text: "Non-Compliant" },
            },
            {
              limit: 70,
              color: "hsl(var(--status-partial))",
              showTick: true,
              tooltip: { text: "Partial" },
            },
            {
              color: "hsl(var(--status-compliant))",
              showTick: true,
              tooltip: { text: "Compliant" },
            },
          ],
        }}
        pointer={{
          color: "hsl(var(--foreground))",
          length: 0.80,
          width: 8,
          elastic: true,
        }}
        labels={{
          valueLabel: {
            formatTextValue: (val: number) => `${Math.round(val)}%`,
            style: {
              fontSize: size > 150 ? 35 : 20,
              fontWeight: 700,
              fontFamily: "var(--font-quicksand)",
              fill: "hsl(var(--foreground))",
            },
          },
          tickLabels: {
            type: "outer",
            defaultTickValueConfig: {
              formatTextValue: (val: number) => `${val}`,
              style: {
                fontSize: size > 150 ? 10 : 7,
                fill: "hsl(var(--muted-foreground))",
              },
            },
            defaultTickLineConfig: {
              length: 6,
              color: "hsl(var(--muted-foreground))",
            },
          },
        }}
        value={percentage}
        minValue={0}
        maxValue={100}
        style={{ width: size, height }}
      />
      {label && (
        <span className="text-xs font-medium text-muted-foreground -mt-1">
          {label}
        </span>
      )}
    </div>
  );
}
