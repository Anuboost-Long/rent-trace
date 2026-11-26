"use client";
import Button from "@/components/common/button";
import type { ButtonVariant } from "@/components/common/button-class-name";
import TextAreaInput from "@/components/common/inputs/text-area-input";
import { useEffect, useRef, useState } from "react";

type ConfirmDialogProp = Readonly<{
  open: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel?: string;
  confirmVariant?: ButtonVariant;
  pending?: boolean;
  error?: string;
  confirmDisabled?: boolean;
  // Asks for a reason, which must be filled in before confirming. It is passed to onConfirm.
  reasonLabel?: string;
  children?: React.ReactNode;
  onConfirm: (reason: string) => void;
  onCancel: () => void;
}>;

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel,
  cancelLabel = "Cancel",
  confirmVariant = "primary",
  pending,
  error,
  confirmDisabled,
  reasonLabel,
  children,
  onConfirm,
  onCancel,
}: ConfirmDialogProp) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [reason, setReason] = useState("");
  const missingReason = reasonLabel !== undefined && reason.trim() === "";

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) {
      setReason("");
      dialog.showModal();
    }
    if (!open && dialog.open) dialog.close();
  }, [open]);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    const closeOnBackdropClick = (event: MouseEvent) => {
      if (event.target === dialog && !pending) onCancel();
    };
    dialog.addEventListener("click", closeOnBackdropClick);
    return () => dialog.removeEventListener("click", closeOnBackdropClick);
  }, [pending, onCancel]);

  return (
    <dialog
      ref={dialogRef}
      onClose={onCancel}
      aria-labelledby="confirm-title"
      className="m-auto w-[calc(100%-2rem)] max-w-md rounded-xl border border-default bg-background p-0 text-left text-foreground shadow-medium backdrop:bg-black/40"
    >
      <div className="p-6">
        <h2 id="confirm-title" className="text-section">
          {title}
        </h2>
        <p className="mt-2 text-body-sm text-fg-secondary">{message}</p>
        {children && <div className="mt-4">{children}</div>}
        {reasonLabel !== undefined && (
          <div className="mt-4">
            <TextAreaInput
              name="confirm-reason"
              label={reasonLabel}
              required
              maxLength={500}
              value={reason}
              onChange={(event) => setReason(event.target.value)}
            />
          </div>
        )}
        {error && (
          <p role="alert" className="mt-3 text-sm text-error">
            {error}
          </p>
        )}
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="secondary" onClick={onCancel} disabled={pending}>
            {cancelLabel}
          </Button>
          <Button
            variant={confirmVariant}
            onClick={() => onConfirm(reason.trim())}
            pending={pending}
            disabled={confirmDisabled || missingReason}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </dialog>
  );
}
