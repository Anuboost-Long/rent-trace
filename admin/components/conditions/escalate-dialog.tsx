"use client";
import TextArea from "@/components/common/inputs/text-area-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import type { ApiFailure } from "@/types/api/common";
import { useState } from "react";

type EscalateDialogProp = Readonly<{
  title: string;
  pending: boolean;
  error: ApiFailure | null;
  onConfirm: (reason: string) => void;
  onCancel: () => void;
}>;

export default function EscalateDialog({
  title,
  pending,
  error,
  onConfirm,
  onCancel,
}: EscalateDialogProp) {
  const [reason, setReason] = useState("");

  return (
    <ConfirmDialog
      open
      title={`Ask an admin to decide on ${title}?`}
      message="An admin reads both sides and makes the final call. Tell them why you need one."
      confirmLabel="Ask an admin to decide"
      pending={pending}
      confirmDisabled={reason.trim() === ""}
      error={error?.message}
      onConfirm={() => onConfirm(reason.trim())}
      onCancel={onCancel}
    >
      <TextArea
        label="Reason"
        name="reason"
        value={reason}
        onChange={(event) => setReason(event.target.value)}
        required
      />
    </ConfirmDialog>
  );
}
