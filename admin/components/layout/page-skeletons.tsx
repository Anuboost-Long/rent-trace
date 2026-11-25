import Skeleton from "@/components/common/loading/skeleton";

type WithHeader = Readonly<{ withHeader?: boolean }>;

function Busy({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <output aria-busy className="block">
      <span className="sr-only">Loading…</span>
      <div aria-hidden>{children}</div>
    </output>
  );
}

function TitleSkeleton() {
  return (
    <>
      <Skeleton className="h-4 w-44" />
      <Skeleton className="mt-4 mb-6 h-8 w-64 max-w-full" />
    </>
  );
}

const ROW_WIDTHS = ["w-1/3", "w-2/5", "w-1/4", "w-1/2", "w-1/3", "w-2/5"];

export function ListSkeleton({ withHeader }: WithHeader) {
  return (
    <Busy>
      {withHeader && <Skeleton className="mb-6 h-8 w-48" />}
      <div className="mb-4 flex flex-wrap gap-3">
        <Skeleton className="h-10 w-64 max-w-full" />
        <Skeleton className="h-10 w-32" />
      </div>
      <div className="divide-y divide-default rounded-xl border border-default">
        {ROW_WIDTHS.map((width, index) => (
          <div key={index} className="flex items-center gap-4 p-4">
            <div className="flex-1">
              <Skeleton className={`h-4 ${width}`} />
              <Skeleton className="mt-2 h-3 w-1/5" />
            </div>
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
        ))}
      </div>
    </Busy>
  );
}

const DETAIL_VALUES = ["w-40", "w-56", "w-32", "w-48", "w-36", "w-52", "w-28"];

export function DetailSkeleton() {
  return (
    <Busy>
      <TitleSkeleton />
      <div className="divide-y divide-default rounded-xl border border-default">
        {DETAIL_VALUES.map((width, index) => (
          <div key={index} className="grid grid-cols-3 gap-4 p-4">
            <Skeleton className="h-4 w-20" />
            <Skeleton className={`col-span-2 h-4 ${width}`} />
          </div>
        ))}
      </div>
      <Skeleton className="mt-10 mb-3 h-6 w-32" />
      <div className="divide-y divide-default rounded-xl border border-default">
        {[0, 1].map((index) => (
          <div key={index} className="flex items-center gap-3 p-4">
            <Skeleton className="size-9 rounded-full" />
            <Skeleton className="h-4 w-40" />
          </div>
        ))}
      </div>
    </Busy>
  );
}

export function FormSkeleton({ withHeader }: WithHeader) {
  return (
    <Busy>
      {withHeader && <TitleSkeleton />}
      <div className="max-w-xl space-y-5">
        {[0, 1, 2, 3].map((index) => (
          <div key={index}>
            <Skeleton className="h-4 w-24" />
            <Skeleton className="mt-2 h-11 w-full" />
          </div>
        ))}
        <Skeleton className="h-11 w-32" />
      </div>
    </Busy>
  );
}

export function DashboardSkeleton() {
  return (
    <Busy>
      <div className="grid gap-10 lg:grid-cols-3 lg:gap-12">
        <div className="lg:col-span-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="mt-3 h-14 w-40" />
          <Skeleton className="mt-3 h-4 w-72 max-w-full" />
          <Skeleton className="mt-6 h-2 w-full rounded-full" />
          <div className="mt-4 flex flex-wrap gap-x-8 gap-y-2">
            {[0, 1, 2, 3].map((index) => (
              <Skeleton key={index} className="h-4 w-20" />
            ))}
          </div>
        </div>
        <div className="space-y-6">
          {[0, 1, 2].map((index) => (
            <div key={index}>
              <Skeleton className="h-4 w-28" />
              <Skeleton className="mt-2 h-8 w-16" />
            </div>
          ))}
        </div>
      </div>
    </Busy>
  );
}

export function CardsSkeleton({ count = 3 }: Readonly<{ count?: number }>) {
  return (
    <Busy>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: count }, (_, index) => (
          <div key={index} className="rounded-xl border border-default p-5">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="mt-3 h-6 w-3/4" />
            <Skeleton className="mt-2 h-4 w-1/2" />
            <div className="mt-5 space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
            </div>
          </div>
        ))}
      </div>
    </Busy>
  );
}

export function HomePanelSkeleton() {
  return (
    <Busy>
      <div className="overflow-hidden rounded-2xl border border-default">
        <div className="p-6 sm:p-8">
          <Skeleton className="h-4 w-16" />
          <Skeleton className="mt-3 h-9 w-2/3" />
          <Skeleton className="mt-3 h-4 w-1/2" />
          <Skeleton className="mt-5 h-4 w-40" />
        </div>
        <div className="grid grid-cols-2 gap-px border-t border-default bg-muted sm:grid-cols-4">
          {[0, 1, 2, 3].map((index) => (
            <div key={index} className="bg-background p-4 sm:p-5">
              <Skeleton className="h-4 w-14" />
              <Skeleton className="mt-2 h-5 w-24" />
            </div>
          ))}
        </div>
        <div className="flex gap-3 border-t border-default p-4 sm:px-8">
          <Skeleton className="h-11 w-40" />
          <Skeleton className="h-11 w-32" />
        </div>
      </div>
    </Busy>
  );
}
