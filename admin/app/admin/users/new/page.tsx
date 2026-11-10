import { handleGetRoles } from "@/api/services/access/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import ContentSkeleton from "@/components/layout/content-skeleton";
import { BUILT_IN_PARTY_ROLES } from "@/constants/roles";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import { Suspense } from "react";

import CreateUserForm from "./create-user-form";

export const metadata: Metadata = { title: "New user · RentTrace" };

export default function NewUserPage() {
  return (
    <div className="max-w-xl">
      <Breadcrumbs
        trail={[
          { label: "Users", href: Route.admin.users },
          { label: "New user" },
        ]}
      />
      <h1 className="mt-4 text-2xl font-semibold">New user</h1>
      <p className="mt-1 mb-6 text-foreground/70">
        The account is created verified. Share the starting password with the
        person securely; no email is sent.
      </p>
      <Suspense fallback={<ContentSkeleton />}>
        <NewUser />
      </Suspense>
    </div>
  );
}

async function NewUser() {
  const { data } = await handleGetRoles();
  return <CreateUserForm roles={data ?? BUILT_IN_PARTY_ROLES} />;
}
