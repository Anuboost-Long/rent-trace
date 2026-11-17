"use client";
import CheckInput from "@/components/common/inputs/check-input";
import DateInput from "@/components/common/inputs/date-input";
import TextArea from "@/components/common/inputs/text-area-input";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import type { ApiFailure } from "@/types/api/common";
import type { ConditionBody, UnitCondition } from "@/types/conditions/models";
import { todayIso } from "@/utils/calendar";
import { useState } from "react";

type ConditionDialogProp = Readonly<{
  note: UnitCondition | null;
  pending: boolean;
  error: ApiFailure | null;
  onSave: (body: ConditionBody) => void;
  onCancel: () => void;
}>;

export default function ConditionDialog({
  note,
  pending,
  error,
  onSave,
  onCancel,
}: ConditionDialogProp) {
  const [title, setTitle] = useState(note?.title ?? "");
  const [description, setDescription] = useState(note?.description ?? "");
  const [checkedOn, setCheckedOn] = useState(
    note?.observed_at.slice(0, 10) ?? todayIso(),
  );
  const [shown, setShown] = useState(false);
  const fields = error?.fields ?? {};

  return (
    <ConfirmDialog
      open
      title={note ? "Edit condition note" : "Add a condition note"}
      message={
        note
          ? "The earlier wording is kept. Tenants see the newest wording."
          : "Tenants only see this note if you show it to them."
      }
      confirmLabel={note ? "Save note" : "Add note"}
      pending={pending}
      confirmDisabled={title.trim() === "" || checkedOn === ""}
      error={
        error && Object.keys(fields).length === 0 ? error.message : undefined
      }
      onConfirm={() =>
        onSave({
          title: title.trim(),
          description: description.trim(),
          observed_at: `${checkedOn}T00:00:00Z`,
          ...(note ? {} : { is_shown_to_tenants: shown }),
        })
      }
      onCancel={onCancel}
    >
      <div className="space-y-4">
        <TextInput
          label="What it is"
          name="title"
          placeholder="Kitchen benchtop"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          error={fields.title}
          required
        />
        <TextArea
          label="Condition"
          name="description"
          placeholder="Small chip near the sink, no other marks"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          error={fields.description}
        />
        <DateInput
          label="Checked on"
          name="observed_at"
          defaultValue={checkedOn}
          required
          onValueChange={setCheckedOn}
          error={fields.observed_at}
        />
        {!note && (
          <CheckInput
            label="Show to tenants"
            name="is_shown_to_tenants"
            checked={shown}
            onChange={(event) => setShown(event.target.checked)}
          />
        )}
      </div>
    </ConfirmDialog>
  );
}
