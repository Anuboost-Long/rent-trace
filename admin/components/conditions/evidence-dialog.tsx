"use client";
import DateInput from "@/components/common/inputs/date-input";
import TextArea from "@/components/common/inputs/text-area-input";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import type { ApiFailure } from "@/types/api/common";
import type { EvidenceBody } from "@/types/evidence/models";
import { todayIso } from "@/utils/calendar";
import { useState } from "react";

type EvidenceDialogProp = Readonly<{
  pending: boolean;
  error: ApiFailure | null;
  onSend: (body: EvidenceBody) => void;
  onCancel: () => void;
}>;

export default function EvidenceDialog({
  pending,
  error,
  onSend,
  onCancel,
}: EvidenceDialogProp) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [seenOn, setSeenOn] = useState(todayIso());
  const fields = error?.fields ?? {};

  return (
    <ConfirmDialog
      open
      title="Report a condition"
      message="Your landlord reviews it. You can withdraw it until they answer."
      confirmLabel="Send report"
      pending={pending}
      confirmDisabled={title.trim() === "" || seenOn === ""}
      error={
        error && Object.keys(fields).length === 0 ? error.message : undefined
      }
      onConfirm={() =>
        onSend({
          title: title.trim(),
          description: description.trim(),
          observed_at: `${seenOn}T00:00:00Z`,
        })
      }
      onCancel={onCancel}
    >
      <div className="space-y-4">
        <TextInput
          label="What it is"
          name="title"
          placeholder="Damp patch in the bedroom"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          error={fields.title}
          required
        />
        <TextArea
          label="What you saw"
          name="description"
          placeholder="On the wall near the window, about the size of a plate"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          error={fields.description}
        />
        <DateInput
          label="Seen on"
          name="observed_at"
          defaultValue={seenOn}
          required
          onValueChange={setSeenOn}
          error={fields.observed_at}
        />
      </div>
    </ConfirmDialog>
  );
}
