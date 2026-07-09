"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  TextAlignLeft,
  CheckCircle,
  PaperPlaneTilt,
  X,
  Spinner,
} from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/lib/store";
import { toast } from "sonner";

export function TextInput() {
  const router = useRouter();
  const { setExtractedText } = useAppStore();
  const [text, setText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async () => {
    const trimmed = text.trim();
    if (!trimmed) return;

    setError(null);
    setIsSubmitting(true);

    try {
      // Brief processing step for visual feedback
      await new Promise((resolve) => setTimeout(resolve, 500));

      setExtractedText(trimmed, "Manual Input", trimmed.length);
      toast.success("Text submitted successfully", {
        description: `${trimmed.length.toLocaleString()} characters ready for analysis`,
      });
      setIsSubmitted(true);
      setTimeout(() => router.push("/app/"), 800);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setIsSubmitting(false);
    }
  }, [text, setExtractedText, router]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.ctrlKey && e.key === "Enter") {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <div className="w-full">
      {/* Label */}
      <p className="text-sm font-medium text-foreground mb-2">
        Paste Text
      </p>

      <div
        className={`
          relative border-2 border-dashed rounded-[2px] p-6
          transition-all duration-200
          ${
            isSubmitting
              ? "pointer-events-none opacity-70"
              : ""
          }
          ${
            error
              ? "border-destructive"
              : "border-border hover:border-primary/50 hover:bg-muted/50"
          }
        `}
      >
        {/* Submitting state */}
        {isSubmitting && (
          <div className="flex flex-col items-center justify-center min-h-[160px] space-y-3">
            <Spinner
              className="h-10 w-10 text-primary animate-spin"
              weight="bold"
            />
            <p className="text-sm font-medium text-muted-foreground">
              Processing text...
            </p>
          </div>
        )}

        {/* Submitted state */}
        {isSubmitted && (
          <div className="flex flex-col items-center justify-center min-h-[160px] space-y-2">
            <CheckCircle
              className="h-10 w-10 text-status-compliant"
              weight="fill"
            />
            <p className="text-sm font-medium">Text submitted successfully</p>
          </div>
        )}

        {/* Idle / editing state */}
        {!isSubmitting && !isSubmitted && (
          <div className="flex flex-col min-h-[160px]">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Paste or type your compliance document text here..."
              className="flex-1 w-full bg-transparent border-none outline-none resize-none text-sm text-foreground placeholder:text-muted-foreground/50 leading-relaxed"
            />
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="mt-3 flex items-center justify-center gap-2 text-sm text-destructive">
            <X className="h-4 w-4" weight="bold" />
            {error}
          </div>
        )}
      </div>

      {/* Controls below the box — idle/has-text */}
      {!isSubmitting && !isSubmitted && (
        <div className="mt-3 flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            {text.length > 0
              ? `${text.length.toLocaleString()} characters — Ctrl+Enter to submit`
              : "0 characters"}
          </span>
          <Button
            size="sm"
            onClick={handleSubmit}
            disabled={!text.trim()}
          >
            <PaperPlaneTilt className="h-4 w-4 mr-1.5" weight="bold" />
            Submit Text
          </Button>
        </div>
      )}

      {/* Controls — submitted */}
      {isSubmitted && (
        <div className="mt-3 text-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setIsSubmitted(false);
              setText("");
              setError(null);
            }}
          >
            Enter new text
          </Button>
        </div>
      )}
    </div>
  );
}
