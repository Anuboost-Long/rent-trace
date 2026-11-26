import clsx from "clsx";

type SpinnerProp = Readonly<{ className?: string }>;

export default function Spinner({ className }: SpinnerProp) {
  return (
    <span
      aria-hidden
      className={clsx(
        "inline-block size-6 rounded-full",
        "border-2 border-default border-t-brand-border",
        "motion-safe:animate-spin motion-reduce:border-t-default",
        className,
      )}
    />
  );
}
