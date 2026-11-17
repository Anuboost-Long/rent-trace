import clsx from "clsx";

type SpinnerProp = Readonly<{ className?: string }>;

export default function Spinner({ className }: SpinnerProp) {
  return (
    <span
      aria-hidden
      className={clsx(
        "inline-block size-6 rounded-full",
        "border-2 border-foreground/15 border-t-foreground",
        "motion-safe:animate-spin motion-reduce:border-t-foreground/15",
        className,
      )}
    />
  );
}
