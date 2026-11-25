import { handleGetPermissions } from "@/api/services/access/serve-action";
import ButtonLink from "@/components/common/button-link";
import Can from "@/components/common/can";
import LoadError from "@/components/common/load-error";
import StatusBadge from "@/components/common/status-badge";
import DataTable, { type Column } from "@/components/common/table/data-table";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import type { PermissionItem } from "@/types/access/models";
import { Plus } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Permissions · RentTrace" };

export default function PermissionsPage() {
  return (
    <>
      <div className="mb-4 flex justify-end">
        <Can permission="access.manage">
          <ButtonLink href={Route.admin.permission_new} className="gap-2">
            <Plus aria-hidden className="size-4" />
            New permission
          </ButtonLink>
        </Can>
      </div>
      <Suspense fallback={<ListSkeleton />}>
        <Permissions />
      </Suspense>
    </>
  );
}

const columns: Column<PermissionItem>[] = [
  {
    header: "Permission",
    cell: (permission) => (
      <>
        <Link
          href={Route.admin.permission(permission.code)}
          className="font-medium underline-offset-2 hover:underline"
        >
          {permission.name}
        </Link>
        <p className="font-mono text-xs text-fg-tertiary">{permission.code}</p>
      </>
    ),
  },
  { header: "Module", cell: (permission) => permission.module },
  {
    header: "Available to",
    cell: (permission) => (permission.is_admin_only ? "Admins only" : "Anyone"),
  },
  {
    header: "Roles",
    cell: (permission) => permission.roles.join(", ") || "—",
  },
  {
    header: "Status",
    cell: (permission) =>
      permission.is_active ? (
        <StatusBadge tone="success">Active</StatusBadge>
      ) : (
        <StatusBadge tone="neutral">Inactive</StatusBadge>
      ),
  },
];

async function Permissions() {
  const { data, error } = await handleGetPermissions();
  if (error) {
    return <LoadError error={error} />;
  }
  return (
    <DataTable
      caption="Permissions"
      columns={columns}
      rows={data}
      rowKey={(permission) => permission.code}
      empty={<p className="font-medium">No permissions yet</p>}
    />
  );
}
