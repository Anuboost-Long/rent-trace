import { handleGetRoles } from "@/api/services/access/serve-action";
import { handleGetUser } from "@/api/services/users/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { FormSkeleton } from "@/components/layout/page-skeletons";
import { BUILT_IN_PARTY_ROLES } from "@/constants/roles";
import { Route } from "@/constants/web-routes";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import EditUserForm from "./edit-user-form";

export default function EditUserPage({
  params,
}: PageProps<"/admin/users/[id]/edit">) {
  return (
    <Suspense fallback={<FormSkeleton withHeader />}>
      <EditUser params={params} />
    </Suspense>
  );
}

async function EditUser({
  params,
}: Readonly<Pick<PageProps<"/admin/users/[id]/edit">, "params">>) {
  const { id } = await params;
  const [{ data: user, error }, rolesResult] = await Promise.all([
    handleGetUser(id),
    handleGetRoles(),
  ]);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }

  return (
    <div className="max-w-xl">
      <Breadcrumbs
        trail={[
          { label: "Users", href: Route.admin.users },
          {
            label: `${user.first_name} ${user.last_name}`,
            href: Route.admin.user(user.id),
          },
          { label: "Edit" },
        ]}
      />
      <h1 className="mt-4 mb-6 text-2xl font-semibold">Edit user</h1>
      <EditUserForm
        user={user}
        roles={rolesResult.data ?? BUILT_IN_PARTY_ROLES}
      />
    </div>
  );
}
