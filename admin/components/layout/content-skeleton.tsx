import Skeleton from "@/components/common/loading/skeleton";
import SkeletonRows from "@/components/common/loading/skeleton-rows";

export default function ContentSkeleton() {
  return (
    <div role="status" aria-busy>
      <span className="sr-only">Loading…</span>
      <div aria-hidden className="mb-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="mt-2 h-4 w-72 max-w-full" />
      </div>
      <SkeletonRows />
    </div>
  );
}
