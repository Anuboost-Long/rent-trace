import { handleGetPermissions } from "@/api/services/access/serve-action";
import { handleGetAllUsers } from "@/api/services/users/serve-action";
import LoadError from "@/components/common/load-error";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { FormSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import { Suspense } from "react";

import GrantForm from "./grant-form";

export const metadata: Metadata = { title: "New grant · RentTrace" };

export default function NewGrantPage({
  searchParams,
}: PageProps<"/admin/access/grants/new">) {
  return (
    <div className="max-w-xl">
      <Breadcrumbs
        trail={[
          { label: "Team and permissions", href: Route.admin.access },
          { label: "Grants", href: Route.admin.grants },
          { label: "New grant" },
        ]}
      />
      <h1 className="mt-4 text-2xl font-semibold">New grant</h1>
      <p className="mt-1 mb-6 text-fg-secondary">
        Give one person a permission on top of what their roles already give
        them. A reason is required and is kept in their history.
      </p>
      <Suspense fallback={<FormSkeleton />}>
        <NewGrant searchParams={searchParams} />
      </Suspense>
    </div>
  );
}

async function NewGrant({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/access/grants/new">, "searchParams">>) {
  const { permission } = await searchParams;
  const [users, permissions] = await Promise.all([
    handleGetAllUsers(),
    handleGetPermissions(),
  ]);
  const error = users.error ?? permissions.error;
  if (error) {
    return <LoadError error={error} />;
  }
  return (
    <GrantForm
      users={users.data!}
      permissions={permissions.data!.filter((item) => item.is_active)}
      defaultPermission={
        typeof permission === "string" ? permission : undefined
      }
    />
  );
}
