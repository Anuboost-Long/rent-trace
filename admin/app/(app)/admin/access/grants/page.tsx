import {
  handleGetGrants,
  handleGetPermissions,
} from "@/api/services/access/serve-action";
import ButtonLink from "@/components/common/button-link";
import Can from "@/components/common/can";
import LocalTime from "@/components/common/local-time";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import type { GrantListItem } from "@/types/access/models";
import { Plus } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import RevokeGrantButton from "../revoke-grant-button";
import GrantsFilter from "./grants-filter";

export const metadata: Metadata = { title: "Grants · RentTrace" };

export default function GrantsPage({
  searchParams,
}: PageProps<"/admin/access/grants">) {
  return (
    <>
      <div className="mb-4 flex justify-end">
        <Can permission="access.manage">
          <ButtonLink href={Route.admin.grant_new} className="gap-2">
            <Plus aria-hidden className="size-4" />
            New grant
          </ButtonLink>
        </Can>
      </div>
      <Suspense fallback={<ListSkeleton />}>
        <Grants searchParams={searchParams} />
      </Suspense>
    </>
  );
}

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const personName = (grant: GrantListItem) =>
  `${grant.user.first_name} ${grant.user.last_name}`;

const columns: Column<GrantListItem>[] = [
  {
    header: "Person",
    cell: (grant) => (
      <>
        <Link
          href={Route.admin.user(grant.user.id)}
          className="font-medium underline-offset-2 hover:underline"
        >
          {personName(grant)}
        </Link>
        <p className="text-xs text-foreground/60">{grant.user.email}</p>
      </>
    ),
  },
  {
    header: "Permission",
    cell: (grant) => (
      <Link
        href={Route.admin.permission(grant.permission_code)}
        className="underline-offset-2 hover:underline"
      >
        {grant.permission_name}
      </Link>
    ),
  },
  { header: "Reason", cell: (grant) => grant.reason },
  {
    header: "Granted by",
    cell: (grant) =>
      grant.granted_by
        ? `${grant.granted_by.first_name} ${grant.granted_by.last_name}`
        : "—",
  },
  { header: "Date", cell: (grant) => <LocalTime iso={grant.created_at} /> },
  {
    header: "Actions",
    className: "text-right",
    cell: (grant) => (
      <div className="flex justify-end">
        <RevokeGrantButton
          userId={grant.user.id}
          personName={personName(grant)}
          permissionCode={grant.permission_code}
          permissionName={grant.permission_name}
        />
      </div>
    ),
  },
];

async function Grants({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/access/grants">, "searchParams">>) {
  const query = await searchParams;
  const filters = { q: first(query.q), permission: first(query.permission) };
  const page = Number(first(query.page)) || 1;
  const [{ data, error }, permissions] = await Promise.all([
    handleGetGrants({ ...filters, page }),
    handleGetPermissions(),
  ]);

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ ...filters, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.admin.grants}?${params}`;
  };

  return (
    <>
      <GrantsFilter {...filters} permissions={permissions.data ?? []} />
      {error ? (
        <p role="alert" className="text-red-600">
          {error.message}
        </p>
      ) : (
        <>
          <DataTable
            caption="Individual grants"
            columns={columns}
            rows={data.results}
            rowKey={(grant) => `${grant.user.id}-${grant.permission_code}`}
            empty={
              <>
                <p className="font-medium">No grants match</p>
                <p className="mt-1 text-sm text-foreground/70">
                  Grants give one person a permission on top of their roles.
                </p>
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
