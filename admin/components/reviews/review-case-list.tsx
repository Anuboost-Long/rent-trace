import { handleGetReviewCases } from "@/api/services/evidence/serve-action";
import Pagination from "@/components/common/table/pagination";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import clsx from "clsx";
import Link from "next/link";
import { Suspense } from "react";

import ReviewCaseItem from "./review-case-item";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

const FILTERS = [
  { label: "Waiting", status: undefined },
  { label: "Approved", status: "APPROVED" },
  { label: "Rejected", status: "REJECTED" },
] as const;

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

export default function ReviewCaseList({
  searchParams,
}: Readonly<{ searchParams: SearchParams }>) {
  return (
    <Suspense fallback={<ListSkeleton />}>
      <Cases searchParams={searchParams} />
    </Suspense>
  );
}

async function Cases({
  searchParams,
}: Readonly<{ searchParams: SearchParams }>) {
  const query = await searchParams;
  const status = first(query.status);
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetReviewCases({ status, page });

  const hrefFor = (target: { status?: string; page?: number }) => {
    const params = new URLSearchParams(
      Object.entries(target).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.admin.review_cases}?${params}`;
  };

  return (
    <>
      <nav aria-label="Filter cases" className="mb-4 flex gap-1">
        {FILTERS.map((filter) => {
          const active = filter.status === status;
          return (
            <Link
              key={filter.label}
              href={hrefFor({ status: filter.status })}
              aria-current={active ? "page" : undefined}
              className={clsx(
                "flex h-9 items-center rounded-lg px-3 text-sm",
                active
                  ? "bg-foreground/10 font-semibold"
                  : "text-foreground/70 hover:bg-foreground/5",
                "focus-visible:outline-2 focus-visible:outline-foreground",
              )}
            >
              {filter.label}
            </Link>
          );
        })}
      </nav>
      {error ? (
        <p role="alert" className="text-red-600">
          {error.message}
        </p>
      ) : data.results.length === 0 ? (
        <div className="py-12 text-center">
          <p className="font-medium">
            {status ? "No cases here" : "Nothing waiting for a decision"}
          </p>
          <p className="mt-1 text-sm text-foreground/70">
            When someone asks an admin to decide on a condition report, it shows
            up here.
          </p>
        </div>
      ) : (
        <>
          <ul className="divide-y divide-foreground/15 overflow-hidden rounded-xl border border-foreground/15">
            {data.results.map((item) => (
              <li key={item.id}>
                <ReviewCaseItem item={item} />
              </li>
            ))}
          </ul>
          <Pagination
            page={data.page}
            totalPages={data.total_pages}
            count={data.count}
            hrefForPage={(target) => hrefFor({ status, page: target })}
          />
        </>
      )}
    </>
  );
}
