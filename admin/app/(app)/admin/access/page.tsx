import { handleGetPermissions } from "@/api/services/access/serve-action";
import LocalTime from "@/components/common/local-time";
import StatusBadge from "@/components/common/status-badge";
import DataTable, { type Column } from "@/components/common/table/data-table";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import { getMe } from "@/utils/viewer";
import type { Metadata } from "next";
import { Suspense } from "react";

import { getAdminTeam, type TeamMember } from "./admin-team";

export const metadata: Metadata = { title: "Team and permissions · RentTrace" };

// How many permission chips a row shows before "+ N more".
const SHOWN_PERMISSIONS = 6;

export default function TeamPage() {
  return (
    <>
      <p className="mb-5 rounded-xl border border-default bg-background px-4 py-3 text-body-sm text-fg-secondary">
        Admin accounts are created by RentTrace operations, not through sign-up.
        Each admin only has the permissions shown here. You can&apos;t change
        your own permissions.
      </p>
      <Suspense fallback={<ListSkeleton />}>
        <Team />
      </Suspense>
    </>
  );
}

async function Team() {
  const [{ data: team, error }, catalogue, { data: me }] = await Promise.all([
    getAdminTeam(),
    handleGetPermissions(),
    getMe(),
  ]);
  if (error) {
    return (
      <p role="alert" className="text-error">
        {error.message}
      </p>
    );
  }
  const nameOf = (code: string) =>
    catalogue.data?.find((permission) => permission.code === code)?.name ??
    code;

  const columns: Column<TeamMember>[] = [
    {
      header: "Admin",
      cell: ({ user }) => (
        <>
          <span className="block font-medium">
            {user.first_name} {user.last_name}
            {user.id === me?.id && " (you)"}
          </span>
          <span className="block text-caption font-normal text-fg-secondary">
            {user.email}
          </span>
        </>
      ),
    },
    {
      header: "Permissions",
      cell: ({ user, access }) => {
        if (user.is_top_level_admin)
          return <PermissionChip>All permissions (super admin)</PermissionChip>;
        const codes = access?.effective ?? [];
        if (codes.length === 0)
          return <span className="text-fg-tertiary">None</span>;
        return (
          <ul className="flex flex-wrap gap-1.5">
            {codes.slice(0, SHOWN_PERMISSIONS).map((code) => (
              <li key={code}>
                <PermissionChip>{nameOf(code)}</PermissionChip>
              </li>
            ))}
            {codes.length > SHOWN_PERMISSIONS && (
              <li className="self-center text-caption text-fg-secondary">
                + {codes.length - SHOWN_PERMISSIONS} more
              </li>
            )}
          </ul>
        );
      },
    },
    {
      header: "MFA",
      cell: ({ user }) =>
        user.has_authenticator ? (
          <StatusBadge tone="success">On</StatusBadge>
        ) : (
          <StatusBadge tone="warning">Setup pending</StatusBadge>
        ),
    },
    {
      header: "Last active",
      className: "whitespace-nowrap",
      cell: ({ user }) =>
        user.last_login_at ? <LocalTime iso={user.last_login_at} /> : "Never",
    },
  ];

  return (
    <DataTable
      caption="Admins"
      columns={columns}
      rows={team}
      rowKey={({ user }) => user.id}
      rowHref={({ user }) => Route.admin.admin_permissions(user.id)}
      empty={<p className="font-medium">No admins yet</p>}
    />
  );
}

function PermissionChip({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <StatusBadge tone="neutral" className="font-normal">
      {children}
    </StatusBadge>
  );
}
