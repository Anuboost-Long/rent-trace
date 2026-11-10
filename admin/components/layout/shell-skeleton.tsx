import Skeleton from "@/components/common/loading/skeleton";

import ContentSkeleton from "./content-skeleton";

export default function ShellSkeleton() {
  return (
    <div aria-busy className="flex min-h-screen">
      <aside
        aria-hidden
        className="hidden w-60 shrink-0 flex-col gap-6 border-r border-foreground/15 p-4 md:flex"
      >
        <div>
          <Skeleton className="h-6 w-28" />
          <Skeleton className="mt-2 h-4 w-16" />
        </div>
        <div className="flex flex-col gap-1">
          {Array.from({ length: 3 }, (_, index) => (
            <Skeleton key={index} className="h-10" />
          ))}
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <div
          aria-hidden
          className="flex h-14 shrink-0 items-center justify-end border-b border-foreground/15 px-4"
        >
          <Skeleton className="h-9 w-28" />
        </div>
        <main className="flex-1 p-4 md:p-8">
          <ContentSkeleton />
        </main>
      </div>
    </div>
  );
}
