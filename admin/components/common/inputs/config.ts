import clsx from "clsx";

export const InputBoxClassName = clsx(
  "flex h-11 w-full items-center gap-2",
  "rounded-lg bg-background transition-colors",
  "border border-strong",
  "px-3",
  "hover:border-fg-tertiary focus-within:border-brand-border focus-within:outline-2 focus-within:outline-offset-0 focus-within:outline-brand-border/25",
);

export const InputInvalidClassName = "border-error-accent";

export const InputClassName = clsx(
  "h-full min-w-0 flex-1",
  "bg-transparent outline-hidden",
  "text-base placeholder:text-fg-tertiary",
  "disabled:opacity-60",
);

export const LabelClassName = "text-body-sm font-medium text-fg-primary";

export const ErrorClassName = "text-sm text-error";
