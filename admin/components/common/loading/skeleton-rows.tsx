import Skeleton from "./skeleton";

type SkeletonRowsProp = Readonly<{ count?: number }>;

export default function SkeletonRows({ count = 4 }: SkeletonRowsProp) {
  return (
    <div
      aria-hidden
      className="divide-y divide-default rounded-xl border border-default"
    >
      {Array.from({ length: count }, (_, index) => (
        <div key={index} className="flex items-center gap-4 p-4">
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="ml-auto h-4 w-1/5" />
        </div>
      ))}
    </div>
  );
}
