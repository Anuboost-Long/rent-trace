"use client";
import { dismiss, getServerToasts, getToasts, subscribe } from "@/utils/toast";
import clsx from "clsx";
import { CircleAlert, CircleCheck, X } from "lucide-react";
import { useEffect, useRef, useSyncExternalStore } from "react";

const TONE = {
  success: "border-success-border bg-success-background text-success",
  error: "border-error-border bg-error-background text-error",
} as const;

export default function ToastHost() {
  const toasts = useSyncExternalStore(subscribe, getToasts, getServerToasts);
  const host = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = host.current;
    if (!element || toasts.length === 0) return;
    // The popover layer sits above an open dialog, so a message is never hidden behind one.
    if (element.matches(":popover-open")) element.hidePopover();
    element.showPopover();
  }, [toasts]);

  return (
    <div
      ref={host}
      popover="manual"
      className="pointer-events-none fixed inset-auto right-4 bottom-4 left-4 m-0 flex flex-col items-end gap-2 overflow-visible border-0 bg-transparent p-0 sm:left-auto sm:w-96"
    >
      {toasts.map((item) => (
        <div
          key={item.id}
          role={item.kind === "error" ? "alert" : "status"}
          className={clsx(
            "pointer-events-auto flex w-full items-start gap-3 rounded-xl border p-3 text-body-sm shadow-medium",
            "animate-panel-in motion-reduce:animate-none",
            TONE[item.kind],
          )}
        >
          {item.kind === "error" ? (
            <CircleAlert aria-hidden className="mt-0.5 size-5 shrink-0" />
          ) : (
            <CircleCheck aria-hidden className="mt-0.5 size-5 shrink-0" />
          )}
          <p className="min-w-0 flex-1 text-fg-primary">{item.message}</p>
          <button
            type="button"
            aria-label="Dismiss"
            onClick={() => dismiss(item.id)}
            className="grid size-6 shrink-0 place-items-center rounded-md hover:bg-foreground/5 focus-visible:outline-2 focus-visible:outline-brand-border"
          >
            <X aria-hidden className="size-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
