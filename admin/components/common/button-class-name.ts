import clsx from "clsx";

export type ButtonVariant = "primary" | "quiet";
export type ButtonSize = "md" | "sm" | "icon";

const SIZE_CLASS: Record<ButtonSize, string> = {
  md: "h-11 px-5",
  sm: "h-9 px-3",
  icon: "size-9 px-0",
};

export const buttonClassName = (
  variant: ButtonVariant = "primary",
  size: ButtonSize = "md",
) =>
  clsx(
    "relative inline-flex items-center justify-center overflow-hidden rounded-lg",
    variant === "primary" && "bg-foreground text-background",
    variant === "quiet" && "border border-foreground/15",
    SIZE_CLASS[size],
    "text-sm font-semibold",
    "hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-foreground disabled:opacity-60",
  );
