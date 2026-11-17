import Breadcrumbs from "@/components/layout/breadcrumbs";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";

import PermissionForm from "../permission-form";

export const metadata: Metadata = { title: "New permission · RentTrace" };

export default function NewPermissionPage() {
  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Access", href: Route.admin.access },
          { label: "Permissions", href: Route.admin.permissions },
          { label: "New permission" },
        ]}
      />
      <h1 className="mt-4 mb-6 text-2xl font-semibold">New permission</h1>
      <PermissionForm permission={null} />
    </>
  );
}
