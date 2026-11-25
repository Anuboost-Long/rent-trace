import {
  handleGetPermissions,
  handleGetRoleMembers,
  handleGetRoles,
} from "@/api/services/access/serve-action";
import { handleGetAllUsers } from "@/api/services/users/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { FormSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import RoleEditor from "../../role-editor";
import RoleMembers from "./role-members";

export default function EditRolePage({
  params,
}: PageProps<"/admin/access/roles/[code]">) {
  return (
    <>
      <Suspense fallback={<FormSkeleton withHeader />}>
        <EditRole params={params} />
      </Suspense>
    </>
  );
}

async function EditRole({
  params,
}: Readonly<Pick<PageProps<"/admin/access/roles/[code]">, "params">>) {
  const { code } = await params;
  const [roles, permissions] = await Promise.all([
    handleGetRoles(),
    handleGetPermissions(),
  ]);
  const error = roles.error ?? permissions.error;
  if (error) {
    return (
      <p role="alert" className="mt-4 text-error">
        {error.message}
      </p>
    );
  }
  const role = roles.data!.find((candidate) => candidate.code === code);
  if (!role) notFound();
  const showMembers = role.kind === "ADMIN";
  const [members, everyone] = showMembers
    ? await Promise.all([handleGetRoleMembers(code), handleGetAllUsers()])
    : [null, null];
  const heldIds = new Set(members?.data?.results.map((member) => member.id));
  const candidates = (everyone?.data ?? []).filter(
    (user) =>
      !heldIds.has(user.id) &&
      !user.roles.includes("TENANT") &&
      !user.roles.includes("LANDLORD"),
  );
  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Access", href: Route.admin.access },
          { label: role.name },
        ]}
      />
      <h1 className="mt-4 mb-6 text-2xl font-semibold">{role.name}</h1>
      <RoleEditor
        role={role}
        roles={roles.data!}
        permissions={permissions.data!}
      />
      {members?.data && (
        <RoleMembers
          roleCode={role.code}
          roleName={role.name}
          members={members.data.results}
          total={members.data.count}
          candidates={candidates}
          canChange
        />
      )}
    </>
  );
}
