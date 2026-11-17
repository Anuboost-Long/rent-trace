import {
  handleGetPermissions,
  handleGetUserPermissions,
} from "@/api/services/access/serve-action";
import { handleGetUser } from "@/api/services/users/serve-action";
import LocalTime from "@/components/common/local-time";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { DetailSkeleton } from "@/components/layout/page-skeletons";
import { StatusLabel } from "@/constants/roles";
import { Route } from "@/constants/web-routes";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { Suspense } from "react";

import UserActions from "../user-actions";
import ResetAuthenticatorButton from "./reset-authenticator-button";
import UserPermissionsSection from "./user-permissions";

export default function UserDetailPage({
  params,
}: PageProps<"/admin/users/[id]">) {
  return (
    <Suspense fallback={<DetailSkeleton />}>
      <UserDetail params={params} />
    </Suspense>
  );
}

async function UserDetail({
  params,
}: Readonly<Pick<PageProps<"/admin/users/[id]">, "params">>) {
  const { id } = await params;
  const [{ data: user, error }, access, catalogue] = await Promise.all([
    handleGetUser(id),
    handleGetUserPermissions(id),
    handleGetPermissions(),
  ]);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }

  const details: [string, ReactNode][] = [
    ["Email", user.email],
    [
      "Role",
      user.role_names.join(", ") +
        (user.is_top_level_admin ? " (super admin)" : ""),
    ],
    ["Status", StatusLabel[user.account_status]],
    ["Phone", user.phone_number ?? "—"],
    [
      "Two-step verification",
      user.has_authenticator ? "Authenticator set up" : "Not set up",
    ],
    [
      "Sign-in method",
      user.auth_method === "GOOGLE" ? "Google" : "Email and password",
    ],
    [
      "Email verified",
      <LocalTime key="Email verified" iso={user.email_verified_at} />,
    ],
    ["Last sign-in", <LocalTime key="Last sign-in" iso={user.last_login_at} />],
    ["Joined", <LocalTime key="Joined" iso={user.created_at} />],
  ];

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Users", href: Route.admin.users },
          { label: `${user.first_name} ${user.last_name}` },
        ]}
      />
      <div className="mt-4 mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">
          {user.first_name} {user.last_name}
        </h1>
        <div className="flex flex-wrap gap-2">
          <ResetAuthenticatorButton
            userId={user.id}
            name={user.first_name}
            hasAuthenticator={user.has_authenticator}
          />
          <UserActions user={user} variant="full" />
        </div>
      </div>
      <dl className="divide-y divide-foreground/15 rounded-xl border border-foreground/15">
        {details.map(([label, value]) => (
          <div key={label} className="grid gap-1 p-4 sm:grid-cols-[12rem_1fr]">
            <dt className="text-sm text-foreground/70">{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      {access.data && catalogue.data && (
        <UserPermissionsSection
          userId={user.id}
          name={user.first_name}
          data={access.data}
          allPermissions={catalogue.data}
        />
      )}
    </>
  );
}
