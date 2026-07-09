"use client";

import { Sidebar } from "@/components/layout/Sidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { FileUpload } from "@/components/upload/FileUpload";
import { TextInput } from "@/components/upload/TextInput";
import { useAppStore } from "@/lib/store";

export default function UploadPage() {
  const { sidebarCollapsed, documentName } = useAppStore();

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main
        className={`flex-1 transition-all duration-300 ${
          sidebarCollapsed ? "ml-16" : "ml-64"
        }`}
      >
        <div className="p-6 pt-20 max-w-[1400px] mx-auto">
          <PageHeader
            title="Upload Document"
            subtitle="Upload a file or paste text for NABH compliance analysis"
          />

          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
            <FileUpload />
            <TextInput />
          </div>

          {documentName && (
            <div className="mt-6 text-center text-sm text-muted-foreground">
              Current document: <strong>{documentName}</strong>
              <p className="text-xs mt-1">
                Upload or paste new content to replace it
              </p>
            </div>
          )}

          <div className="mt-12 max-w-md mx-auto text-center text-xs text-muted-foreground space-y-2">
            <p>
              Supported formats: PDF, TXT, DOCX (up to 50MB for files)
            </p>
            <p>
              Your document text is extracted locally and stored in your browser
              session. No data is persisted on our servers.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
