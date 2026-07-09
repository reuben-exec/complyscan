# ComplyScan Agent Notes

## Current Status
ComplyScan is an MVP-ready healthcare compliance analysis tool with a FastAPI backend (Python 3.12), **Next.js 16 frontend** (App Router, Tailwind v3, Phosphor icons), deterministic keyword matcher, optional LLM semantic pass, override workflow, and PDF export.

## What Changed Recently
- **[Tier 4: Matching Engine Intelligence]**: Threshold unification, fuzzy matching, cross-validation:
  - Centralized all score thresholds in `backend/core/config.py` Settings class (score_compliant=0.80, score_partial=0.50, score_noncompliant_floor=0.10, ui_compliant=0.70, ui_partial=0.40)
  - Fixed 7 threshold inconsistencies: engine.py, logic.py, analyzer.py, generator.py all now import from config instead of hardcoding
  - Fixed `>` vs `>=` inconsistency in logic.py for NON_COMPLIANT floor (standardized on `>=`)
  - Fixed PDF generator unit mismatch (was comparing 0-1 float against 80/50 percent values)
  - Added fuzzy keyword matching (difflib.SequenceMatcher) in engine.py for OCR typo tolerance (keywords >= 4 chars, threshold 0.85, no pip dependency)
  - Created  — CrossValidator boosts COMPLIANT scores by +0.03 when >=50% of related requirements are also COMPLIANT
  - Added fuzzy config settings (fuzzy_enabled, fuzzy_threshold, fuzzy_discount) to config.py
  - Frontend utils.ts getScoreColor thresholds (0.7/0.4) documented as deliberately offset from backend (0.8/0.5)
- **[Dashboard Chapter Progress Bars Fixed]**: Chapter progress bars now display a continuous red→amber→green temperature gradient instead of being invisible (the `getScoreColor` function was returning Tailwind class names used in inline `style` props, which don't resolve). Added `getComplianceColor()` in `utils.ts` — performs HSL interpolation through the same 3 color stops as the compliance gauge (red hsl(0,72%,51%) → amber hsl(38,92%,50%) → green hsl(142,71%,45%)). Updated `page.tsx` to use the new function for both the bar fill and percentage text color.

- **[Dashboard Overhaul Complete]**: Comprehensive dashboard redesign with live data:
  - Installed `react-gauge-component` v2.0.29 — semicircle gauge with color zones (red 0-30, amber 30-70, green 70-100)
  - Rewrote `ComplianceGauge.tsx` with elastic needle, theme-aware CSS variable colors, dynamic import (SSR-safe)
  - Rewrote `page.tsx` — new layout: Hero → Gauge+Donut 2-col → 4 KPI cards → Chapter progress bars → Chapter Explorer
  - Rewrote `getDashboardStats()` in `api.ts` — reads from Zustand localStorage instead of stale API data
  - Rewrote `getChapterStats()` — computes per-chapter stats from localStorage results
  - Added `documentName` to `DashboardStats` type — displays in hero badge
  - Hero description fixed from outdated text to "NABH compliance analysis engine..."
  - StatusDonut now uses CSS variable colors (theme-aware, different for light/dark)
  - Chapter progress bars with color-coded scores replacing ScoreBarChart
  - Empty state with upload CTA when no data exists
  - Auto-refresh on window focus
- **[PDF Report Enhanced]**: Multi-page report with full justifications:
  - Evidence items displayed as full cards instead of truncated table rows
  - Full justification text with `multi_cell` wrapping (no more 30-char truncation)
  - Page breaks between evidence cards when content overflows
  - LLM Assessment section included when available
- **[PDF Report Fix: Pydantic Compatibility]**: All evidence field accesses in report generator converted to dual dict/Pydantic pattern:
  - Added `_get_attr()` helper function that handles both dict `.get()` and Pydantic `getattr()` access
  - `_draw_evidence_cards()`: replaced all `ev.get()` calls with `_get_attr(ev, ...)` — fields: name, type, critical, status, justification
  - Added `_draw_llm_assessment()`: dedicated section showing per-evidence LLM confidence bar (color-coded), justification, and disagreement warnings — excludes chain-of-thought reasoning
  - Fixed `_draw_overall_assessment()` LLM notes: replaced dict-only `ev.get("llm_justification")` with `_get_attr()`
  - Wired `_draw_llm_assessment()` into `build()` method
  - Tested with mixed evidence (LLM-enabled + LLM-disabled items) — PDF generated successfully (50KB)
- **[Stale Server Bytecode Fix]**: Server was running cached `.pyc` bytecode from before the generator.py rewrite. Killed stale process, cleared all `__pycache__` directories, restarted with `--reload`. PDF now correctly displays evidence names, types, statuses, and justifications instead of "Unnamed"/"N/A".
- **[SVG Optimization & Logo Rewrite]**: Drastically reduced SVG size and fixed build errors:
  - Installed SVGO v4.0.1, added `svgo.config.js` (multipass, aggressive optimization)
  - Optimized master SVG from 71KB → 21KB (70.6% reduction, all transforms collapsed to absolutes)
  - Regenerated `shield-icon.svg` (48 paths, 12KB, down from 133KB) — standalone shield glyph used via `<image>` in Logo.tsx
  - Rewrote `Logo.tsx` with all 31 wordmark paths: 15 letter bodies (`fill="currentColor"` for dark sidebar) + 16 accent paths (hardcoded teal/blue)
  - Cleaned orphan SVGs from `public/`: deleted `complyscan-logo.svg`, `complyscan-text.svg`
  - Build verified — `npm run build` passes with zero errors (42 pages)
- **[UI Refresh Complete]**: Comprehensive visual overhaul:
  - Font: Quicksand (single font for headings + body) replacing Lora + Inter
  - Icons: Phosphor Icons (`@phosphor-icons/react`) replacing lucide-react
  - Logo: SVG logo in sidebar (shield icon + "ComplyScan" text), ICO favicon
  - Theme toggle: Moved to Sidebar (shared across all pages), not duplicated per-page
  - Default theme: Light mode on first visit (no system preference detection)
  - Dark mode: SVG logo with transparent background works on dark sidebar
- **[Tier 1: Spec Compliance]**: Fixed scoring, disclaimer, and PDF bugs:
  - NON_COMPLIANT score changed from 0.2 to 0.0 in all 3 scoring files
  - Global advisory disclaimer banner on every page (fixed bottom bar)
  - PDF report footer now shows advisory disclaimer
  - Fixed 8 critical PDF generator bugs (wrong enum names, mismatched fields, broken imports)
  - Added summary scorecard to PDF reports (FR-4.2 compliance)
- **[Tier 2: Knowledge Base Hardening]**: Matching engine improvements:
  - Expanded PRE keywords across all 12 files (289 total keywords, avg 4.8/item)
  - Added EXCLUSION_KEYWORDS (18 generic terms) to filter false positives
  - Wired up confidence_weight from KB as score multiplier (0.75-0.95)
  - Wired up validation_rules from KB as additional matching signals (+0.05/rule, capped +0.15)
  - Increased MIN_TOTAL_HITS from 2 to 4 (more rigorous evidence requirements)
- **[Tier 3: LLM Upgrade + Structured Output]**: Comprehensive LLM system rewrite:
  - Default model upgraded to Llama 3.3 70B Instruct FP8 (from 8B) for better reasoning
  - llm_client.py rewritten: model-agnostic, timeout 60s, concurrency 5, 5-layer JSON fallback, enforce_schema(), max_tokens=512
  - prompts.py rewritten: modular prompt architecture, chain-of-thought instructions, max_text_length 8000, validate_llm_response()
  - analyzer.py rewritten: expanded excerpts (3K->8K chars), chain-of-thought extraction, tiered override thresholds (0.85/0.75/0.80), aligned score thresholds with engine.py
  - Schema: added llm_reasoning field (EvidenceItem, TypeScript type)
  - Frontend: EvidenceCard displays chain-of-thought reasoning in collapsible section + high-disagreement indicator
- **[Next.js Migration Complete]**: Ported from Svelte 5 to Next.js 16 with App Router. Includes:
  - Static export (`output: 'export'`) with `basePath: "/app"`
  - `generateStaticParams` for chapter/requirement routes (38 static pages)
  - SPA catch-all serving from FastAPI backend
  - All pages: Dashboard (`/`), Upload (`/upload`), Chapter listing (`/chapter/$code`), Requirement Analysis (`/chapter/$code/$req`)
  - Evidence override modal on requirement analysis page
  - Drag-and-drop PDF upload with progress indicator
  - Theme toggle (light/dark with localStorage persistence)
- **[Render CI: Frontend Build Pipeline]**: Added `render-build.sh` — installs Node.js 20 via nvm (pre-installed in Render Python images), runs `npm ci && npm run build` in `frontend-next/`, then `pip install -r requirements.txt`. Updated `render.yaml` build command from `pip install -r requirements.txt` → `bash render-build.sh`. Render now automatically builds the frontend on every deploy — no more manual local builds.
- **[Favicon BasePath Fix]**: metadata icons/manifest paths now include `/app` prefix:
  - `layout.tsx` metadata: `icon`, `apple`, `manifest` paths changed from `/favicon.ico` → `/app/favicon.ico`, etc.
  - `site.webmanifest`: icon `src` paths changed from `/favicon-96x96.png` → `/app/favicon-96x96.png`, etc.
  - `backend/main.py`: added dedicated root-level routes for `/favicon-96x96.png`, `/web-app-manifest-192x192.png`, `/web-app-manifest-512x512.png`
  - Root cause: Next.js `basePath` auto-prefixes framework-managed assets (JS/CSS) but NOT user-defined metadata `icons`/`manifest` paths

## Core Architecture
- **Backend API**: backend/api/main.py (FastAPI) — serves from `frontend-next/out/`, mounts `_next` assets
- **Frontend**: frontend-next/ (Next.js 16, App Router, Tailwind v3, Phosphor Icons)
- **Matching engine**: backend/matcher/engine.py (exclusion keywords, validation_rules, confidence_weight scaling, fuzzy matching via difflib)
- **Score thresholds**: backend/core/config.py (centralized: score_compliant=0.80, score_partial=0.50, score_noncompliant_floor=0.10)
- **OCR extraction**: backend/ocr/client.py
- **Semantic analyzer**: backend/semantic/analyzer.py (tiered thresholds, chain-of-thought extraction, expanded excerpts)
- **Cross-validation**: backend/scorer/cross_validation.py (corroborating evidence boost across related requirements)
- **Scorer utilities**: backend/scorer/logic.py (standalone scoring functions using centralized config)
- **Report generation**: backend/report/generator.py
- **Knowledge base**: data/knowledge_base/
- **Design assets**: icons/ (SVG logo, ICO favicon, JPEG screenshot)

## Next.js Frontend ("/app" base path, static SPA)
- **Root layout**: `app/layout.tsx` — Quicksand + JetBrains Mono fonts, ThemeProvider, inline script for theme flash prevention, Sidebar wrapping
- **Theme**: `lib/theme.ts` — `useTheme()` hook, defaults to light, reads/writes `localStorage("complyscan-theme")`
- **Dashboard**: `app/page.tsx` — hero band with document name badge, Gauge+Donut 2-col layout, 4 KPI cards, chapter progress bars, chapter explorer. Live data from localStorage via `getDashboardStats()`
- **Upload**: `app/upload/page.tsx` — FileUpload with drag-and-drop
- **Chapter page**: `app/chapter/[code]/ChapterClient.tsx` — requirement list with status badges
- **Requirement page**: `app/chapter/[code]/[req]/RequirementClient.tsx` — split layout (document text + analysis results), override modal
- **Sidebar**: `components/layout/Sidebar.tsx` — fixed dark left nav, collapsible, SVG logo branding, theme toggle, chapter navigation
- **Charts**: `components/charts/ComplianceGauge.tsx` (`react-gauge-component`, semicircle, elastic needle, CSS variable colors), `StatusDonut.tsx` (Recharts PieChart donut with theme-aware colors)
- **UI Components**: `components/ui/` — Badge, Button, Card, Input, Textarea, Skeleton (shadcn/ui-style)
- **Icons**: All from `@phosphor-icons/react` with `weight` prop (regular, bold, fill, light)
- **Build**: `npm run build` → 38 static pages in `out/`
- **Known quirk**: `basePath` does NOT auto-prefix metadata `icons`/`manifest` paths — these MUST be hardcoded with `/app` prefix in `layout.tsx` and `site.webmanifest`

## Verification Checklist
- Run `npm run build` from `frontend-next/` to verify frontend compilation
- Run `pytest tests/test_edge_cases.py` for backend edge-case tests
- Run `pytest tests/test_analyze_e2e.py` when the local API server is running
- Keep README, AGENTS.md, and project docs aligned with current scope and deployment status

## Team Credits
- Reuben RL — Project Lead / Healthcare Analytics & AI
- Aakash Karna — Project Co-Lead (Knowledge Base & Documentation)
