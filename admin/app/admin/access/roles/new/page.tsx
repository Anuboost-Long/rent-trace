import {
  handleGetPermissions,
  handleGetRoles,
} from "@/api/services/access/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import ContentSkeleton from "@/components/layout/content-skeleton";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import { Suspense } from "react";

import RoleEditor from "../../role-editor";

export const metadata: Metadata = { title: "New role · RentTrace" };

export default function NewRolePage() {
  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Access", href: Route.admin.access },
          { label: "New role" },
        ]}
      />
      <h1 className="mt-4 mb-6 text-2xl font-semibold">New role</h1>
      <Suspense fallback={<ContentSkeleton />}>
        <NewRole />
      </Suspense>
    </>
  );
}

async function NewRole() {
  const [roles, permissions] = await Promise.all([
    handleGetRoles(),
    handleGetPermissions(),
  ]);
  const error = roles.error ?? permissions.error;
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }
  return (
    <RoleEditor
      role={null}
      roles={roles.data!}
      permissions={permissions.data!}
    />
  );
}
