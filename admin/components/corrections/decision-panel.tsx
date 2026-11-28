"use client";
import Button from "@/components/common/button";
import Card from "@/components/common/card";
import TextArea from "@/components/common/inputs/text-area-input";
import useCorrectionDecision from "@/hooks/form/useCorrectionDecision";
import type { Correction } from "@/types/corrections/models";
import { useState } from "react";

export default function DecisionPanel({
  correction,
}: Readonly<{ correction: Correction }>) {
  const { pending, error, decide } = useCorrectionDecision(correction.id);
  const [reason, setReason] = useState("");

  if (correction.status !== "PENDING_REVIEW")
    return (
      <Card title="Decision" className="self-start">
        <p className="text-body-sm text-fg-secondary">
          {correction.status === "APPROVED"
            ? "Approved. The new wording is the current version."
            : "Rejected. The record stays as it was."}
        </p>
        {correction.admin_reason && (
          <p className="mt-2 whitespace-pre-line">{correction.admin_reason}</p>
        )}
      </Card>
    );

  return (
    <Card
      title="Decision"
      description="Choose one. A reason is required and both parties will see it."
      className="self-start"
    >
      <TextArea
        label="Reason (required)"
        name="reason"
        value={reason}
        onChange={(event) => setReason(event.target.value)}
        error={error?.fields.reason ?? error?.message}
      />
      <div className="mt-4 flex flex-col gap-2">
        <Button
          type="button"
          pending={pending}
          disabled={reason.trim() === ""}
          onClick={() => decide("approve", reason)}
        >
          Approve correction
        </Button>
        <Button
          type="button"
          variant="secondary"
          disabled={pending || reason.trim() === ""}
          onClick={() => decide("reject", reason)}
        >
          Reject
        </Button>
      </div>
      <p className="mt-4 rounded-lg border border-default px-3 py-2 text-body-sm text-fg-secondary">
        You can only decide between what the parties submitted. You can&apos;t
        add new claims or edit evidence.
      </p>
    </Card>
  );
}
