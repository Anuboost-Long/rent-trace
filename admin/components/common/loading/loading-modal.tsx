"use client";
import { useEffect, useRef } from "react";

import Spinner from "./spinner";

type LoadingModalProp = Readonly<{ visible: boolean; message?: string }>;

export default function LoadingModal({
  visible,
  message = "Loading…",
}: LoadingModalProp) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (visible && !dialog.open) dialog.showModal();
    if (!visible && dialog.open) dialog.close();
  }, [visible]);

  return (
    <dialog
      ref={dialogRef}
      onCancel={(event) => event.preventDefault()}
      aria-label={message}
      className="m-auto rounded-xl border border-foreground/15 bg-background p-6 text-foreground backdrop:bg-black/40"
    >
      <div role="status" className="flex items-center gap-3">
        <Spinner />
        <p className="text-sm font-medium">{message}</p>
      </div>
    </dialog>
  );
}
