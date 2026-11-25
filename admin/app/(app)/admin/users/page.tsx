import { handleGetUsers } from "@/api/services/users/serve-action";
import ButtonLink from "@/components/common/button-link";
import Can from "@/components/common/can";
import FilterChips from "@/components/common/filter-chips";
import LoadError from "@/components/common/load-error";
import LocalTime from "@/components/common/local-time";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import type { UserFilters, UserSummary } from "@/types/users/models";
import { Plus } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";

import AccountStatusBadge from "./account-status-badge";
import UsersFilter from "./users-filter";

export default function UsersPage({ searchParams }: PageProps<"/admin/users">) {
  return (
    <Suspense fallback={<ListSkeleton />}>
      <UsersList searchParams={searchParams} />
    </Suspense>
  );
}

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

// The chips across the top of the list. Each one is a role or status filter the API supports.
const CHIPS: { label: string; filter: Pick<UserFilters, "role" | "status"> }[] =
  [
    { label: "All", filter: {} },
    { label: "Tenants", filter: { role: "TENANT" } },
    { label: "Landlords", filter: { role: "LANDLORD" } },
    { label: "Admins", filter: { role: "ADMIN" } },
    { label: "Suspended", filter: { status: "SUSPENDED" } },
  ];

const columns: Column<UserSummary>[] = [
  {
    header: "Name",
    cell: (user) => (
      <>
        <span className="block font-medium">
          {user.first_name} {user.last_name}
        </span>
        <span className="block text-caption font-normal text-fg-secondary">
          {user.email}
        </span>
      </>
    ),
  },
  {
    header: "Role",
    cell: (user) =>
      user.role_names.join(", ") + (user.is_top_level_admin ? " (super)" : ""),
  },
  {
    header: "Status",
    cell: (user) => <AccountStatusBadge status={user.account_status} />,
  },
  {
    header: "Last active",
    cell: (user) =>
      user.last_login_at ? <LocalTime iso={user.last_login_at} /> : "Never",
  },
];

const hrefFor = (params: UserFilters) => {
  const query = new URLSearchParams(
    Object.entries(params).flatMap(([key, value]) =>
      value ? [[key, String(value)]] : [],
    ),
  ).toString();
  return query ? `${Route.admin.users}?${query}` : Route.admin.users;
};

async function UsersList({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/users">, "searchParams">>) {
  const query = await searchParams;
  const filters = {
    q: first(query.q),
    role: first(query.role),
    status: first(query.status),
  };
  const page = Number(first(query.page)) || 1;
  const [{ data, error }, ...chipCounts] = await Promise.all([
    handleGetUsers({ ...filters, page }),
    ...CHIPS.map(({ filter }) =>
      handleGetUsers({ q: filters.q, ...filter, page_size: 1 }),
    ),
  ]);

  const chips = CHIPS.map(({ label, filter }, index) => ({
    label,
    href: hrefFor({ q: filters.q, ...filter }),
    count: chipCounts[index].data?.count,
    active: filters.role === filter.role && filters.status === filter.status,
  }));

  return (
    <>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <FilterChips label="Filter accounts" chips={chips} />
        <div className="flex flex-wrap items-center gap-3">
          <UsersFilter {...filters} />
          <Can permission="accounts.create">
            <ButtonLink
              href={Route.admin.users_new}
              variant="secondary"
              className="gap-2"
            >
              <Plus aria-hidden className="size-4" />
              Add account
            </ButtonLink>
          </Can>
        </div>
      </div>
      {error ? (
        <LoadError error={error} />
      ) : (
        <>
          <DataTable
            caption="Accounts"
            columns={columns}
            rows={data.results}
            rowKey={(user) => user.id}
            rowHref={(user) => Route.admin.user(user.id)}
            empty={
              <>
                <p className="font-medium">No accounts match these filters</p>
                <Link
                  href={Route.admin.users}
                  className="mt-2 inline-block text-body-sm font-semibold text-fg-brand hover:underline"
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
            hrefForPage={(target) => hrefFor({ ...filters, page: target })}
          />
        </>
      )}
    </>
  );
}
