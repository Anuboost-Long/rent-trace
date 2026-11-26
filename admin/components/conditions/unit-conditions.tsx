"use client";
import Button from "@/components/common/button";
import CheckInput from "@/components/common/inputs/check-input";
import LocalTime from "@/components/common/local-time";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useConditionActions from "@/hooks/form/useConditionActions";
import type { UnitCondition } from "@/types/conditions/models";
import { Plus } from "lucide-react";
import { useState } from "react";

import ConditionDialog from "./condition-dialog";

type UnitConditionsProp = Readonly<{
  unitId: number;
  notes: UnitCondition[];
}>;

type Editing = UnitCondition | "new" | null;

export default function UnitConditions({ unitId, notes }: UnitConditionsProp) {
  const { pending, error, clearError, save, setShown, remove } =
    useConditionActions(unitId);
  const [editing, setEditing] = useState<Editing>(null);
  const [deleting, setDeleting] = useState<UnitCondition | null>(null);
  const shownCount = notes.filter((note) => note.is_shown_to_tenants).length;

  const closeEditor = () => {
    setEditing(null);
    clearError();
  };

  const closeDelete = () => {
    setDeleting(null);
    clearError();
  };

  return (
    <section aria-labelledby="conditions-heading" className="mt-12">
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3">
        <div className="flex items-baseline gap-3">
          <h2 id="conditions-heading" className="text-section">
            Condition
          </h2>
          {notes.length > 0 && (
            <p className="text-sm text-fg-tertiary tabular-nums">
              {shownCount} of {notes.length} shown to tenants
            </p>
          )}
        </div>
        <Button size="sm" className="gap-2" onClick={() => setEditing("new")}>
          <Plus aria-hidden className="size-4" />
          Add note
        </Button>
      </div>

      {notes.length === 0 ? (
        <p className="mt-3 max-w-[65ch] text-sm text-fg-secondary">
          Write down what shape this unit is in, room by room. Tenants only see
          the notes you choose to show them.
        </p>
      ) : (
        <ul className="mt-2 divide-y divide-default">
          {notes.map((note) => (
            <li key={note.id} className="py-4">
              <div className="flex flex-wrap items-start justify-between gap-x-6 gap-y-3">
                <div className="min-w-0 max-w-[65ch] flex-1">
                  <p className="font-medium">{note.title}</p>
                  {note.description && (
                    <p className="mt-1 whitespace-pre-line text-fg-secondary">
                      {note.description}
                    </p>
                  )}
                  <p className="mt-1.5 text-sm text-fg-tertiary">
                    Checked <LocalTime iso={note.observed_at} />
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
                  <CheckInput
                    label="Shown to tenants"
                    checked={note.is_shown_to_tenants}
                    disabled={pending}
                    onChange={(event) =>
                      void setShown(note.id, event.target.checked)
                    }
                  />
                  <div className="flex gap-1">
                    <Button
                      variant="quiet"
                      size="sm"
                      onClick={() => setEditing(note)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="quiet"
                      size="sm"
                      onClick={() => setDeleting(note)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      {editing && (
        <ConditionDialog
          note={editing === "new" ? null : editing}
          pending={pending}
          error={error}
          onCancel={closeEditor}
          onSave={async (body) => {
            const id = editing === "new" ? null : editing.id;
            if (await save(id, body)) closeEditor();
          }}
        />
      )}

      {deleting && (
        <ConfirmDialog
          open
          title={`Delete ${deleting.title}?`}
          message="Tenants stop seeing this note straight away. This can't be undone."
          confirmLabel="Delete"
          pending={pending}
          error={error?.message}
          onConfirm={async () => {
            if (await remove(deleting.id)) closeDelete();
          }}
          onCancel={closeDelete}
        />
      )}
    </section>
  );
}
