import clsx from "clsx";

// "quiet" is the older name for "secondary"; both draw the outlined Figma button.
export type ButtonVariant = "primary" | "secondary" | "quiet" | "danger";
export type ButtonSize = "md" | "sm" | "icon";

const SIZE_CLASS: Record<ButtonSize, string> = {
  md: "h-11 px-5",
  sm: "h-9 px-3",
  icon: "size-9 px-0",
};

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  primary: "bg-brand text-on-brand hover:bg-admin-text",
  secondary:
    "border border-strong bg-background text-fg-brand hover:bg-brand-subtle",
  quiet:
    "border border-strong bg-background text-fg-brand hover:bg-brand-subtle",
  danger: "bg-error text-on-brand hover:bg-error-accent",
};

export const buttonClassName = (
  variant: ButtonVariant = "primary",
  size: ButtonSize = "md",
) =>
  clsx(
    "relative inline-flex items-center justify-center overflow-hidden rounded-lg",
    VARIANT_CLASS[variant],
    SIZE_CLASS[size],
    "text-sm font-semibold transition-colors motion-reduce:transition-none",
    "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border disabled:opacity-60",
  );
