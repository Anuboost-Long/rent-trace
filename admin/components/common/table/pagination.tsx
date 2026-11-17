import clsx from "clsx";
import { ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";

import { buttonClassName } from "../button-class-name";

type PaginationProp = Readonly<{
  page: number;
  totalPages: number;
  count: number;
  hrefForPage: (page: number) => string;
}>;

const pageLink = (enabled: boolean) =>
  clsx(
    buttonClassName("quiet", "sm"),
    "gap-1",
    !enabled && "pointer-events-none opacity-40",
  );

export default function Pagination({
  page,
  totalPages,
  count,
  hrefForPage,
}: PaginationProp) {
  const hasPrevious = page > 1;
  const hasNext = page < totalPages;

  return (
    <nav
      aria-label="Pagination"
      className="mt-4 flex items-center justify-between gap-4 text-sm"
    >
      <p className="text-foreground/70">
        {count} {count === 1 ? "result" : "results"} · Page {page} of{" "}
        {totalPages}
      </p>
      <div className="flex gap-2">
        <Link
          href={hrefForPage(page - 1)}
          aria-disabled={!hasPrevious}
          tabIndex={hasPrevious ? undefined : -1}
          className={pageLink(hasPrevious)}
        >
          <ChevronLeft aria-hidden className="size-4" />
          Previous
        </Link>
        <Link
          href={hrefForPage(page + 1)}
          aria-disabled={!hasNext}
          tabIndex={hasNext ? undefined : -1}
          className={pageLink(hasNext)}
        >
          Next
          <ChevronRight aria-hidden className="size-4" />
        </Link>
      </div>
    </nav>
  );
}
