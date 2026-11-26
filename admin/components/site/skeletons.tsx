const block = "animate-pulse rounded-2xl bg-subtle motion-reduce:animate-none";

export function CardGridSkeleton({ count = 6 }: Readonly<{ count?: number }>) {
  return (
    <ul
      aria-hidden
      className="grid gap-x-6 gap-y-10 sm:grid-cols-2 lg:grid-cols-3"
    >
      {Array.from({ length: count }, (_, index) => (
        <li key={index}>
          <div className={`${block} aspect-4/3`} />
          <div className={`${block} mt-3 h-4 w-2/3`} />
          <div className={`${block} mt-2 h-4 w-1/2`} />
        </li>
      ))}
    </ul>
  );
}

export function HomeSkeleton() {
  return (
    <div aria-hidden className="mx-auto w-full max-w-7xl px-4 pt-16 sm:px-6">
      <div className={`${block} h-16 w-4/5`} />
      <div className={`${block} mt-4 h-5 w-3/5`} />
      <div className={`${block} mt-8 h-32`} />
      <div
        className={`${block} mt-10 aspect-4/5 sm:aspect-video lg:aspect-21/9`}
      />
    </div>
  );
}

export function ListingDetailSkeleton() {
  return (
    <div aria-hidden>
      <div className={`${block} h-4 w-40`} />
      <div className="mt-6 grid gap-10 lg:grid-cols-12 lg:gap-14">
        <div className="lg:col-span-8">
          <div className={`${block} aspect-16/10`} />
          <div className="mt-3 grid grid-cols-5 gap-2 sm:grid-cols-6">
            {[0, 1, 2, 3].map((index) => (
              <div key={index} className={`${block} aspect-4/3`} />
            ))}
          </div>
          <div className={`${block} mt-8 h-9 w-2/3`} />
          <div className={`${block} mt-3 h-4 w-1/3`} />
          <div className={`${block} mt-6 h-4 w-full max-w-prose`} />
          <div className={`${block} mt-2 h-4 w-4/5 max-w-prose`} />
          <div className={`${block} mt-10 h-6 w-40`} />
          <div className="mt-4 divide-y divide-default rounded-2xl border border-default">
            {[0, 1].map((index) => (
              <div key={index} className="flex justify-between gap-6 p-5">
                <div className="flex-1">
                  <div className={`${block} h-4 w-1/3`} />
                  <div className={`${block} mt-2 h-4 w-1/2`} />
                </div>
                <div className={`${block} h-4 w-28`} />
              </div>
            ))}
          </div>
        </div>
        <div className={`${block} h-56 lg:col-span-4`} />
      </div>
    </div>
  );
}
