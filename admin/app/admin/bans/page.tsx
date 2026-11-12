import { handleGetBans } from "@/api/services/bans/serve-action";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import ContentSkeleton from "@/components/layout/content-skeleton";
import { BanStatusLabel, BanTypeLabel } from "@/constants/security";
import { Route } from "@/constants/web-routes";
import type { Ban } from "@/types/security/models";
import { formatDate } from "@/utils/format-date";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import BansFilter from "./bans-filter";
import CreateBanButton from "./create-ban-button";
import UnbanButton from "./unban-button";

export const metadata: Metadata = { title: "Bans · RentTrace" };

export default function BansPage({
  searchParams,
}: Readonly<PageProps<"/admin/bans">>) {
  return (
    <>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Bans</h1>
          <p className="mt-1 text-foreground/70">
            Emails, domains, phone numbers and accounts that are blocked.
          </p>
        </div>
        <CreateBanButton />
      </div>
      <Suspense fallback={<ContentSkeleton />}>
        <BanList searchParams={searchParams} />
      </Suspense>
    </>
  );
}

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const fullName = (person: { first_name: string; last_name: string }) =>
  `${person.first_name} ${person.last_name}`;

const columns: Column<Ban>[] = [
  {
    header: "Target",
    cell: (ban) =>
      ban.user ? (
        <>
          <Link
            href={Route.admin.user(ban.user.id)}
            className="font-medium underline-offset-2 hover:underline"
          >
            {fullName(ban.user)}
          </Link>
          <p className="text-xs text-foreground/60">{ban.user.email}</p>
        </>
      ) : (
        <span className="font-mono">{ban.value}</span>
      ),
  },
  { header: "Type", cell: (ban) => BanTypeLabel[ban.ban_type] },
  { header: "Reason", cell: (ban) => ban.reason },
  {
    header: "Banned",
    cell: (ban) => (
      <>
        {formatDate(ban.created_at)}
        {ban.created_by && (
          <p className="text-xs text-foreground/60">
            by {fullName(ban.created_by)}
          </p>
        )}
      </>
    ),
  },
  {
    header: "Expires",
    cell: (ban) => (ban.expires_at ? formatDate(ban.expires_at) : "Never"),
  },
  {
    header: "Status",
    cell: (ban) => (
      <>
        {BanStatusLabel[ban.status]}
        {ban.status === "LIFTED" && (
          <p className="text-xs text-foreground/60">
            {formatDate(ban.lifted_at)}
            {ban.lift_reason && ` · ${ban.lift_reason}`}
          </p>
        )}
      </>
    ),
  },
  {
    header: "Actions",
    className: "text-right",
    cell: (ban) => (
      <div className="flex justify-end">
        <UnbanButton ban={ban} />
      </div>
    ),
  },
];

async function BanList({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/bans">, "searchParams">>) {
  const query = await searchParams;
  const filters = {
    q: first(query.q),
    status: first(query.status),
    type: first(query.type),
  };
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetBans({ ...filters, page });

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ ...filters, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.admin.bans}?${params}`;
  };

  return (
    <>
      <BansFilter {...filters} />
      {error ? (
        <p role="alert" className="text-red-600">
          {error.message}
        </p>
      ) : (
        <>
          <DataTable
            caption="Bans"
            columns={columns}
            rows={data.results}
            rowKey={(ban) => ban.id}
            empty={
              <>
                <p className="font-medium">No bans match these filters</p>
                <Link
                  href={Route.admin.bans}
                  className="mt-2 inline-block text-sm underline"
                >
                  Clear filters
                </Link>
              </>
            }
          />
          <Pagination
            page={data.page}
            totalPages={data.total_pages}
            count={data.count}
            hrefForPage={hrefForPage}
          />
        </>
      )}
    </>
  );
}
