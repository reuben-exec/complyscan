"use client";

import { cn } from "@/lib/utils";
import { SHIELD_SVG, COMPLY_SVG, SCAN_SVG } from "@/lib/svg-assets";

interface LogoProps {
  collapsed?: boolean;
}

function InlineSvg({
  svg,
  viewBox,
  className,
  ariaLabel,
}: {
  svg: string;
  viewBox: string;
  className?: string;
  ariaLabel: string;
}) {
  // Extract content between <svg> tags (same regex as before)
  const innerMatch = svg.match(/<svg[^>]*>([\s\S]*)<\/svg>/i);
  const innerHtml = innerMatch ? innerMatch[1] : svg;

  return (
    <svg
      viewBox={viewBox}
      className={className}
      role="img"
      aria-label={ariaLabel}
      dangerouslySetInnerHTML={{ __html: innerHtml }}
    />
  );
}

export function Logo({ collapsed = false }: LogoProps) {
  return (
    <div className="flex items-center gap-3">
      {/* Shield icon - always visible */}
      <InlineSvg
        svg={SHIELD_SVG}
        viewBox="431 286 448 516"
        className={cn(
          "shrink-0",
          collapsed ? "h-8 w-8" : "h-10 w-auto"
        )}
        ariaLabel="ComplyScan Shield"
      />

      {/* Wordmark - hidden when collapsed */}
      {!collapsed && (
        <span className="flex items-center gap-1 text-slate-800 dark:text-white/85">
          <InlineSvg
            svg={COMPLY_SVG}
            viewBox="0 0 832 320"
            className="h-7 w-auto"
            ariaLabel="Comply"
          />
          <InlineSvg
            svg={SCAN_SVG}
            viewBox="0 0 628 260"
            className="h-7 w-auto"
            ariaLabel="Scan"
          />
        </span>
      )}
    </div>
  );
}
