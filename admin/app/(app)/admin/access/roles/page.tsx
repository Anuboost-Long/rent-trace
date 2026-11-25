import { handleGetRoles } from "@/api/services/access/serve-action";
import ButtonLink from "@/components/common/button-link";
import Can from "@/components/common/can";
import DataTable, { type Column } from "@/components/common/table/data-table";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import type { RoleItem } from "@/types/access/models";
import { Plus } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Roles · RentTrace" };

export default function RolesPage() {
  return (
    <>
      <div className="mb-4 flex justify-end">
        <Can permission="access.manage">
          <ButtonLink href={Route.admin.role_new} className="gap-2">
            <Plus aria-hidden className="size-4" />
            New role
          </ButtonLink>
        </Can>
      </div>
      <Suspense fallback={<ListSkeleton />}>
        <Roles />
      </Suspense>
    </>
  );
}

async function Roles() {
  const { data: roles, error } = await handleGetRoles();
  if (error) {
    return (
      <p role="alert" className="text-error">
        {error.message}
      </p>
    );
  }
  const nameOf = (code: string | null) =>
    roles.find((role) => role.code === code)?.name ?? "—";

  const columns: Column<RoleItem>[] = [
    {
      header: "Role",
      cell: (role) => (
        <>
          <Link
            href={Route.admin.role(role.code)}
            className="font-medium underline-offset-2 hover:underline"
          >
            {role.name}
          </Link>
          {role.is_system && (
            <span className="ml-2 text-xs text-fg-tertiary">Built in</span>
          )}
        </>
      ),
    },
    {
      header: "Type",
      cell: (role) => (role.kind === "ADMIN" ? "Admin" : "Tenant or landlord"),
    },
    { header: "Inherits from", cell: (role) => nameOf(role.parent) },
    {
      header: "Permissions",
      cell: (role) =>
        role.permissions.length + role.inherited_permissions.length,
    },
    { header: "People", cell: (role) => role.holder_count },
    {
      header: "Status",
      cell: (role) => (role.is_active ? "Active" : "Inactive"),
    },
  ];

  return (
    <DataTable
      caption="Roles"
      columns={columns}
      rows={roles}
      rowKey={(role) => role.code}
      empty={<p className="font-medium">No roles yet</p>}
    />
  );
}
