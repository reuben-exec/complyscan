"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { CloudArrowUp, FileText, CheckCircle, X } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/lib/store";
import { extractText } from "@/lib/api";
import { toast } from "sonner";

const SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".docx"];

export function FileUpload() {
  const router = useRouter();
  const { setExtractedText } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [fileName, setFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isExtensionAllowed = useCallback((name: string) => {
    const lower = name.toLowerCase();
    return SUPPORTED_EXTENSIONS.some((ext) => lower.endsWith(ext));
  }, []);

  const handleFile = useCallback(
    async (file: File) => {
      if (!isExtensionAllowed(file.name)) {
        setError("Only PDF, TXT, and DOCX files are supported");
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        setError("File size must be under 50MB");
        return;
      }

      setError(null);
      setFileName(file.name);
      setIsUploading(true);
      setProgress(10);

      try {
        // Simulate progress
        const progressInterval = setInterval(() => {
          setProgress((p) => Math.min(p + 15, 85));
        }, 300);

        const response = await extractText(file);

        clearInterval(progressInterval);
        setProgress(100);

        setExtractedText(response.text, response.filename, response.char_count);
        toast.success("Document uploaded successfully", {
          description: `${response.filename} — ${response.char_count.toLocaleString()} characters of text extracted`,
        });

        setTimeout(() => router.push("/app/"), 800);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
        setFileName(null);
      } finally {
        setIsUploading(false);
      }
    },
    [setExtractedText, router, isExtensionAllowed]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  return (
    <div className="w-full">
      {/* Label */}
      <p className="text-sm font-medium text-foreground mb-2">
        Upload a File
      </p>

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        className={`
          relative border-2 border-dashed rounded-[2px] p-6 text-center cursor-pointer
          transition-all duration-200
          ${
            isDragging
              ? "border-primary bg-primary/5"
              : "border-border hover:border-primary/50 hover:bg-muted/50"
          }
          ${isUploading ? "pointer-events-none" : ""}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.docx"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
          }}
        />

        {isUploading ? (
          <div className="space-y-4">
            <FileText className="h-10 w-10 mx-auto text-primary animate-pulse" weight="fill" />
            <p className="text-sm font-medium">{fileName}</p>
            <div className="w-full max-w-xs mx-auto">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all duration-300 rounded-full"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                {progress < 100 ? "Extracting text..." : "Complete!"}
              </p>
            </div>
          </div>
        ) : fileName && !error ? (
          <div className="space-y-2">
            <CheckCircle className="h-10 w-10 mx-auto text-status-compliant" weight="fill" />
            <p className="text-sm font-medium">{fileName}</p>
            <p className="text-xs text-muted-foreground">Uploaded successfully</p>
          </div>
        ) : (
          <div className="space-y-3">
            <CloudArrowUp className="h-10 w-10 mx-auto text-muted-foreground" weight="light" />
            <div>
              <p className="text-sm font-medium">
                Drop your file here, or{" "}
                <span className="text-primary underline">browse</span>
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                PDF, TXT, DOCX — up to 50MB
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 flex items-center justify-center gap-2 text-sm text-destructive">
            <X className="h-4 w-4" weight="bold" />
            {error}
          </div>
        )}
      </div>

      {fileName && !isUploading && !error && (
        <div className="mt-3 text-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              setFileName(null);
              setError(null);
              if (fileInputRef.current) fileInputRef.current.value = "";
            }}
          >
            Upload a different file
          </Button>
        </div>
      )}
    </div>
  );
}
