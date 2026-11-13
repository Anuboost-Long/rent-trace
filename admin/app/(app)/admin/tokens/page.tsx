import { handleGetTokens } from "@/api/services/tokens/serve-action";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { TokenStatusLabel } from "@/constants/security";
import { Route } from "@/constants/web-routes";
import type { AccessToken } from "@/types/security/models";
import { formatDateTime } from "@/utils/format-date";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import RevokeTokenButton from "./revoke-token-button";
import TokensFilter from "./tokens-filter";

export const metadata: Metadata = { title: "Access tokens · RentTrace" };

export default function TokensPage({
  searchParams,
}: PageProps<"/admin/tokens">) {
  return (
    <>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Access tokens</h1>
        <p className="mt-1 text-foreground/70">
          Every signed-in session. Revoking one signs that device out straight
          away.
        </p>
      </div>
      <Suspense fallback={<ListSkeleton />}>
        <TokenList searchParams={searchParams} />
      </Suspense>
    </>
  );
}

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columns: Column<AccessToken>[] = [
  {
    header: "Person",
    cell: (token) => (
      <>
        <Link
          href={Route.admin.user(token.user.id)}
          className="font-medium underline-offset-2 hover:underline"
        >
          {token.user.first_name} {token.user.last_name}
        </Link>
        <p className="text-xs text-foreground/60">{token.user.email}</p>
      </>
    ),
  },
  {
    header: "Device",
    cell: (token) => (
      <>
        {token.device_name ?? "Unknown device"}
        {token.is_current && (
          <span className="ml-2 text-xs font-semibold">This session</span>
        )}
        {token.user_agent && (
          <p
            className="max-w-56 truncate text-xs text-foreground/60"
            title={token.user_agent}
          >
            {token.user_agent}
          </p>
        )}
      </>
    ),
  },
  {
    header: "IP address",
    cell: (token) => (
      <span className="font-mono">{token.ip_address ?? "—"}</span>
    ),
  },
  { header: "Signed in", cell: (token) => formatDateTime(token.created_at) },
  { header: "Last used", cell: (token) => formatDateTime(token.last_used_at) },
  { header: "Expires", cell: (token) => formatDateTime(token.expires_at) },
  { header: "Status", cell: (token) => TokenStatusLabel[token.status] },
  {
    header: "Actions",
    className: "text-right",
    cell: (token) => (
      <div className="flex justify-end">
        <RevokeTokenButton token={token} />
      </div>
    ),
  },
];

async function TokenList({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/tokens">, "searchParams">>) {
  const query = await searchParams;
  const filters = { q: first(query.q), status: first(query.status) };
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetTokens({ ...filters, page });

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ ...filters, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.admin.tokens}?${params}`;
  };

  return (
    <>
      <TokensFilter {...filters} />
      {error ? (
        <p role="alert" className="text-red-600">
          {error.message}
        </p>
      ) : (
        <>
          <DataTable
            caption="Access tokens"
            columns={columns}
            rows={data.results}
            rowKey={(token) => token.id}
            empty={
              <>
                <p className="font-medium">No sessions match these filters</p>
                <Link
                  href={Route.admin.tokens}
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
