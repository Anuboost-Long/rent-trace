import { handleGetRoles } from "@/api/services/access/serve-action";
import ButtonLink from "@/components/common/button-link";
import Can from "@/components/common/can";
import DataTable, { type Column } from "@/components/common/table/data-table";
import ContentSkeleton from "@/components/layout/content-skeleton";
import { Route } from "@/constants/web-routes";
import type { RoleItem } from "@/types/access/models";
import { Plus } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Access · RentTrace" };

export default function AccessPage() {
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
      <Suspense fallback={<ContentSkeleton />}>
        <Roles />
      </Suspense>
    </>
  );
}

async function Roles() {
  const { data: roles, error } = await handleGetRoles();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
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
            <span className="ml-2 text-xs text-foreground/60">Built in</span>
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
