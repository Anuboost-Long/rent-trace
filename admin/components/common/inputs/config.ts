import clsx from "clsx";

export const InputBoxClassName = clsx(
  "flex h-11 w-full items-center gap-2",
  "rounded-lg bg-background",
  "border border-foreground/15",
  "px-3",
  "focus-within:outline-2 focus-within:outline-offset-1 focus-within:outline-foreground",
);

export const InputInvalidClassName = "border-red-600";

export const InputClassName = clsx(
  "h-full min-w-0 flex-1",
  "bg-transparent outline-hidden",
  "text-base placeholder:text-foreground/40",
  "disabled:opacity-60",
);

export const LabelClassName = "text-sm font-medium";

export const ErrorClassName = "text-sm text-red-600";
