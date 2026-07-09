"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { RequirementResult } from "@/types";
import * as api from "./api";

interface AppState {
  // Session data
  extractedText: string;
  documentName: string;
  documentLength: number;
  results: RequirementResult[];
  activeChapter: string;

  // UI state
  sidebarCollapsed: boolean;
  isAnalyzing: boolean;
  error: string | null;

  // Actions
  setExtractedText: (text: string, name: string, length: number) => void;
  addResult: (result: RequirementResult) => void;
  getResult: (id: string) => RequirementResult | undefined;
  analyzeKeyword: (requirementId: string) => Promise<void>;
  analyzeSemantic: (requirementId: string) => Promise<void>;
  overrideEvidence: (
    result: RequirementResult,
    evidenceId: string,
    newStatus: string,
    note: string
  ) => Promise<void>;
  exportReport: (result: RequirementResult) => Promise<void>;
  clearDocument: () => void;
  clearResults: () => void;
  clearError: () => void;
  setActiveChapter: (code: string) => void;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      extractedText: "",
      documentName: "",
      documentLength: 0,
      results: [],
      activeChapter: "",
      sidebarCollapsed: false,
      isAnalyzing: false,
      error: null,

      setExtractedText: (text, name, length) =>
        set({ extractedText: text, documentName: name, documentLength: length }),

      addResult: (result) =>
        set((state) => {
          const filtered = state.results.filter(
            (r) => r.requirement_id !== result.requirement_id
          );
          return { results: [...filtered, result] };
        }),

      getResult: (id) => get().results.find((r) => r.requirement_id === id),

      analyzeKeyword: async (requirementId) => {
        const { extractedText } = get();
        if (!extractedText) {
          set({ error: "No document uploaded. Please upload a PDF first." });
          return;
        }
        set({ isAnalyzing: true, error: null });
        try {
          const result = await api.analyzeText(requirementId, extractedText);
          get().addResult(result);
        } catch (err) {
          set({ error: err instanceof Error ? err.message : "Analysis failed" });
        } finally {
          set({ isAnalyzing: false });
        }
      },

      analyzeSemantic: async (requirementId) => {
        const { extractedText } = get();
        if (!extractedText) {
          set({ error: "No document uploaded. Please upload a PDF first." });
          return;
        }
        set({ isAnalyzing: true, error: null });
        try {
          const result = await api.analyzeSemantic(requirementId, extractedText);
          get().addResult(result);
        } catch (err) {
          set({ error: err instanceof Error ? err.message : "Semantic analysis failed" });
        } finally {
          set({ isAnalyzing: false });
        }
      },

      overrideEvidence: async (result, evidenceId, newStatus, note) => {
        set({ isAnalyzing: true, error: null });
        try {
          const response = await api.overrideEvidence(result, evidenceId, newStatus, note);
          get().addResult(response.result);
        } catch (err) {
          set({ error: err instanceof Error ? err.message : "Override failed" });
        } finally {
          set({ isAnalyzing: false });
        }
      },

      exportReport: async (result) => {
        try {
          const blob = await api.generateReport(result);
          const { downloadBlob } = await import("./utils");
          downloadBlob(blob, `${result.requirement_id}_compliance_report.pdf`);
        } catch (err) {
          set({ error: err instanceof Error ? err.message : "Export failed" });
        }
      },

      clearDocument: () =>
        set({
          extractedText: "",
          documentName: "",
          documentLength: 0,
          results: [],
        }),

      clearResults: () => set({ results: [] }),

      clearError: () => set({ error: null }),

      setActiveChapter: (code) => set({ activeChapter: code }),

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    }),
    {
      name: "complyscan-storage",
      partialize: (state) => ({
        extractedText: state.extractedText,
        documentName: state.documentName,
        documentLength: state.documentLength,
        results: state.results,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
