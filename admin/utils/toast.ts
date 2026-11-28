export type ToastKind = "success" | "error";
export type ToastItem = { id: number; kind: ToastKind; message: string };

const SHOWN_MS: Record<ToastKind, number> = { success: 4000, error: 7000 };
const MAX_SHOWN = 4;
const NONE: readonly ToastItem[] = [];

let toasts: readonly ToastItem[] = NONE;
let nextId = 1;
const listeners = new Set<() => void>();

const emit = () => listeners.forEach((listener) => listener());

export const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
};

export const getToasts = () => toasts;
export const getServerToasts = () => NONE;

export const dismiss = (id: number) => {
  toasts = toasts.filter((item) => item.id !== id);
  emit();
};

const show = (kind: ToastKind, message: string) => {
  if (toasts.some((item) => item.kind === kind && item.message === message))
    return;
  const id = nextId++;
  toasts = [...toasts.slice(-(MAX_SHOWN - 1)), { id, kind, message }];
  emit();
  setTimeout(() => dismiss(id), SHOWN_MS[kind]);
};

export const toast = {
  success: (message: string) => show("success", message),
  error: (message: string) => show("error", message),
};
