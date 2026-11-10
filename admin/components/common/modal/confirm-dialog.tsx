"use client";
import Button from "@/components/common/button";
import { useEffect, useRef } from "react";

type ConfirmDialogProp = Readonly<{
  open: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  pending?: boolean;
  error?: string;
  confirmDisabled?: boolean;
  children?: React.ReactNode;
  onConfirm: () => void;
  onCancel: () => void;
}>;

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel,
  pending,
  error,
  confirmDisabled,
  children,
  onConfirm,
  onCancel,
}: ConfirmDialogProp) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={dialogRef}
      onClose={onCancel}
      onClick={(event) => {
        if (event.target === event.currentTarget && !pending) onCancel();
      }}
      aria-labelledby="confirm-title"
      className="m-auto w-[calc(100%-2rem)] max-w-md rounded-xl border border-foreground/15 bg-background p-0 text-foreground backdrop:bg-black/40"
    >
      <div className="p-6">
        <h2 id="confirm-title" className="text-lg font-semibold">
          {title}
        </h2>
        <p className="mt-2 text-foreground/70">{message}</p>
        {children && <div className="mt-4">{children}</div>}
        {error && (
          <p role="alert" className="mt-3 text-sm text-red-600">
            {error}
          </p>
        )}
        <div className="mt-6 flex justify-end gap-3">
          <Button variant="quiet" onClick={onCancel} disabled={pending}>
            Cancel
          </Button>
          <Button
            onClick={onConfirm}
            pending={pending}
            disabled={confirmDisabled}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </dialog>
  );
}
