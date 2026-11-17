import clsx from "clsx";

import Skeleton from "./skeleton";

type SkeletonTextProp = Readonly<{ lines?: number; className?: string }>;

export default function SkeletonText({
  lines = 3,
  className,
}: SkeletonTextProp) {
  return (
    <div aria-hidden className={clsx("flex flex-col gap-2", className)}>
      {Array.from({ length: lines }, (_, index) => (
        <Skeleton
          key={index}
          className={clsx("h-4", index === lines - 1 && lines > 1 && "w-2/3")}
        />
      ))}
    </div>
  );
}
