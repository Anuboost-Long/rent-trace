const block =
  "animate-pulse rounded-2xl bg-foreground/5 motion-reduce:animate-none";

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
      <div className="grid gap-12 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <div className={`${block} h-16 w-4/5`} />
          <div className={`${block} mt-4 h-5 w-3/5`} />
          <div className={`${block} mt-8 h-32`} />
        </div>
        <div className={`${block} h-96 lg:col-span-5`} />
      </div>
    </div>
  );
}
