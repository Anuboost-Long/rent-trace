"use client";
import Button from "@/components/common/button";
import Card from "@/components/common/card";
import TextArea from "@/components/common/inputs/text-area-input";
import useRemovalDecision from "@/hooks/form/useRemovalDecision";
import type { Removal } from "@/types/removals/models";
import { useState } from "react";

export default function DecisionPanel({
  removal,
}: Readonly<{ removal: Removal }>) {
  const { pending, error, decide } = useRemovalDecision(removal.id);
  const [reason, setReason] = useState("");

  if (removal.status !== "PENDING_REVIEW")
    return (
      <Card title="Decision" className="self-start">
        <p className="text-body-sm text-fg-secondary">
          {removal.status === "APPROVED"
            ? "Approved. The records are hidden."
            : "Rejected. The records stay visible."}
        </p>
        {removal.admin_reason && (
          <p className="mt-2 whitespace-pre-line">{removal.admin_reason}</p>
        )}
      </Card>
    );

  return (
    <Card title="Decision" className="self-start">
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
          Approve and hide
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
        Hiding is reversible. Nothing is deleted.
      </p>
    </Card>
  );
}
