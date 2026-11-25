import clsx from "clsx";

export type StatusTone =
  "success" | "warning" | "error" | "attention" | "neutral";

const TONE_CLASS: Record<StatusTone, { badge: string; dot: string }> = {
  success: {
    badge: "border-success-border bg-success-background text-success",
    dot: "bg-success-accent",
  },
  warning: {
    badge: "border-warning-border bg-warning-background text-warning",
    dot: "bg-warning-accent",
  },
  error: {
    badge: "border-error-border bg-error-background text-error",
    dot: "bg-error-accent",
  },
  attention: {
    badge: "border-attention-border bg-attention-background text-attention",
    dot: "bg-attention-accent",
  },
  neutral: {
    badge: "border-neutral-border bg-neutral-background text-neutral",
    dot: "bg-neutral-accent",
  },
};

type StatusBadgeProp = Readonly<{
  tone: StatusTone;
  children: React.ReactNode;
  className?: string;
}>;

export default function StatusBadge({
  tone,
  children,
  className,
}: StatusBadgeProp) {
  const { badge, dot } = TONE_CLASS[tone];
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-caption whitespace-nowrap",
        badge,
        className,
      )}
    >
      <span aria-hidden className={clsx("size-1.5 rounded-full", dot)} />
      {children}
    </span>
  );
}
