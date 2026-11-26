import {
  handleGetPermissions,
  handleGetUserPermissions,
} from "@/api/services/access/serve-action";
import { handleGetUser } from "@/api/services/users/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { DetailSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import { getMe } from "@/utils/viewer";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import PermissionsEditor from "./permissions-editor";

export default function EditAdminPermissionsPage({
  params,
}: PageProps<"/admin/access/admins/[id]">) {
  return (
    <Suspense fallback={<DetailSkeleton />}>
      <EditAdminPermissions params={params} />
    </Suspense>
  );
}

async function EditAdminPermissions({
  params,
}: Readonly<Pick<PageProps<"/admin/access/admins/[id]">, "params">>) {
  const { id } = await params;
  const [user, access, catalogue, { data: me }] = await Promise.all([
    handleGetUser(id),
    handleGetUserPermissions(id),
    handleGetPermissions(),
    getMe(),
  ]);
  if (user.error?.status === 404) notFound();
  if (user.error || access.error || catalogue.error) {
    return (
      <p role="alert" className="text-error">
        {(user.error ?? access.error ?? catalogue.error)?.message}
      </p>
    );
  }
  const admin = user.data;
  if (!admin.is_admin) notFound();

  const name = `${admin.first_name} ${admin.last_name}`;
  const isSelf = me?.id === admin.id;

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Team and permissions", href: Route.admin.access },
          { label: name },
        ]}
      />
      <h1 className="mt-4 mb-5 text-heading">Edit permissions · {name}</h1>
      <PermissionsEditor
        userId={admin.id}
        firstName={admin.first_name}
        access={access.data}
        catalogue={catalogue.data.filter(
          (permission) => permission.is_admin_only && permission.is_active,
        )}
        readOnly={isSelf || admin.is_top_level_admin}
        readOnlyReason={
          isSelf
            ? "You can't change your own permissions."
            : admin.is_top_level_admin
              ? "A super admin has every permission."
              : undefined
        }
      />
    </>
  );
}
