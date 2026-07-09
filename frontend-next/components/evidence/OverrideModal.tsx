"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import type { EvidenceItem } from "@/types";

interface OverrideModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  evidence: EvidenceItem | null;
  onSubmit: (evidenceId: string, newStatus: string, note: string) => void;
}

const STATUSES = ["Compliant", "Partial", "Non-Compliant", "Not Found"];

export function OverrideModal({
  open,
  onOpenChange,
  evidence,
  onSubmit,
}: OverrideModalProps) {
  const [status, setStatus] = useState<string>(evidence?.status || "Compliant");
  const [note, setNote] = useState("");

  if (!evidence) return null;

  const handleSubmit = () => {
    onSubmit(evidence.evidence_id, status, note);
    onOpenChange(false);
    setNote("");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Override Evidence Status</DialogTitle>
          <DialogDescription>
            Manually override the compliance status for{" "}
            <strong>{evidence.name}</strong> ({evidence.evidence_id})
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          <div>
            <label className="text-sm font-medium mb-1.5 block">
              New Status
            </label>
            <Select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium mb-1.5 block">
              Override Note
            </label>
            <Textarea
              placeholder="Explain why you're overriding this status..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Apply Override</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
