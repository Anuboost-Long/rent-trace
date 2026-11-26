import clsx from "clsx";

type SkeletonProp = Readonly<{ className?: string }>;

export default function Skeleton({ className }: SkeletonProp) {
  return (
    <div
      aria-hidden
      className={clsx(
        "rounded-md bg-muted",
        "motion-safe:animate-pulse",
        className,
      )}
    />
  );
}
