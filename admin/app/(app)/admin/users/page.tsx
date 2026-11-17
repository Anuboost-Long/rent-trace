import { handleGetRoles } from "@/api/services/access/serve-action";
import { handleGetUsers } from "@/api/services/users/serve-action";
import ButtonLink from "@/components/common/button-link";
import Can from "@/components/common/can";
import LocalTime from "@/components/common/local-time";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { BUILT_IN_PARTY_ROLES, StatusLabel } from "@/constants/roles";
import { Route } from "@/constants/web-routes";
import type { UserSummary } from "@/types/users/models";
import { Plus } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";

import UserActions from "./user-actions";
import UsersFilter from "./users-filter";

export default function UsersPage({ searchParams }: PageProps<"/admin/users">) {
  return (
    <>
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Users</h1>
          <p className="mt-1 text-foreground/70">Accounts on RentTrace.</p>
        </div>
        <Can permission="accounts.create">
          <ButtonLink href={Route.admin.users_new} className="gap-2">
            <Plus aria-hidden className="size-4" />
            New user
          </ButtonLink>
        </Can>
      </div>
      <Suspense fallback={<ListSkeleton />}>
        <UsersList searchParams={searchParams} />
      </Suspense>
    </>
  );
}

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columns: Column<UserSummary>[] = [
  {
    header: "Name",
    cell: (user) => (
      <Link
        href={Route.admin.user(user.id)}
        className="font-medium underline-offset-2 hover:underline"
      >
        {user.first_name} {user.last_name}
      </Link>
    ),
  },
  { header: "Email", cell: (user) => user.email },
  {
    header: "Role",
    cell: (user) =>
      user.role_names.join(", ") + (user.is_top_level_admin ? " (super)" : ""),
  },
  { header: "Status", cell: (user) => StatusLabel[user.account_status] },
  { header: "Joined", cell: (user) => <LocalTime iso={user.created_at} /> },
  {
    header: "Actions",
    className: "text-right",
    cell: (user) => <UserActions user={user} variant="icon" />,
  },
];

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
  const [{ data, error }, rolesResult] = await Promise.all([
    handleGetUsers({ ...filters, page }),
    handleGetRoles(),
  ]);

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ ...filters, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.admin.users}?${params}`;
  };

  return (
    <>
      <UsersFilter
        {...filters}
        roles={rolesResult.data ?? BUILT_IN_PARTY_ROLES}
      />
      {error ? (
        <p role="alert" className="text-red-600">
          {error.message}
        </p>
      ) : (
        <>
          <DataTable
            caption="Users"
            columns={columns}
            rows={data.results}
            rowKey={(user) => user.id}
            empty={
              <>
                <p className="font-medium">No users match these filters</p>
                <Link
                  href={Route.admin.users}
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
