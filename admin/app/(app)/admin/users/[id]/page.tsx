import {
  handleGetPermissions,
  handleGetUserPermissions,
} from "@/api/services/access/serve-action";
import { handleGetTenancies } from "@/api/services/tenancies/serve-action";
import { handleGetUser } from "@/api/services/users/serve-action";
import Card from "@/components/common/card";
import LocalTime from "@/components/common/local-time";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { DetailSkeleton } from "@/components/layout/page-skeletons";
import { TenancyStatusLabel } from "@/constants/tenancies";
import { Route } from "@/constants/web-routes";
import type { TenancySummary } from "@/types/tenancies/models";
import type { UserDetail } from "@/types/users/models";
import { formatDate } from "@/utils/format-date";
import { getMe } from "@/utils/viewer";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { Suspense } from "react";

import AccountStatusBadge from "../account-status-badge";
import UserActions from "../user-actions";
import ResetAuthenticatorButton from "./reset-authenticator-button";
import UserPermissionsSection from "./user-permissions";

export default function UserDetailPage({
  params,
}: PageProps<"/admin/users/[id]">) {
  return (
    <Suspense fallback={<DetailSkeleton />}>
      <UserDetailContent params={params} />
    </Suspense>
  );
}

const signInMethod = (user: UserDetail) =>
  user.auth_method === "GOOGLE" ? "Google" : "Email and password";

async function UserDetailContent({
  params,
}: Readonly<Pick<PageProps<"/admin/users/[id]">, "params">>) {
  const { id } = await params;
  const [{ data: user, error }, access, catalogue, { data: me }] =
    await Promise.all([
      handleGetUser(id),
      handleGetUserPermissions(id),
      handleGetPermissions(),
      getMe(),
    ]);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-error">
        {error.message}
      </p>
    );
  }

  // Tenancy search matches a tenant's email, so this lists the tenancies this person is on.
  const showsTenancies =
    user.roles.includes("TENANT") &&
    (me?.permissions.includes("tenancies.admin_view") ?? false);
  const tenancies = showsTenancies
    ? (await handleGetTenancies({ q: user.email, page_size: 20 })).data
    : null;

  const name = `${user.first_name} ${user.last_name}`;
  const role =
    user.role_names.join(", ") +
    (user.is_top_level_admin ? " (super admin)" : "");
  const details: [string, ReactNode][] = [
    ["Phone", user.phone_number ?? "—"],
    [
      "Two-step sign-in",
      user.has_authenticator ? "Authenticator set up" : "Not set up",
    ],
    [
      "Email verified",
      <LocalTime key="Email verified" iso={user.email_verified_at} />,
    ],
    [
      "Last log in",
      user.last_login_at ? (
        <LocalTime key="Last log in" iso={user.last_login_at} withTime />
      ) : (
        "Never"
      ),
    ],
  ];

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Accounts", href: Route.admin.users },
          { label: name },
        ]}
      />
      <div className="mt-4 grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start">
        <div className="flex flex-col gap-5">
          <header>
            <AccountStatusBadge status={user.account_status} />
            <h1 className="mt-2 text-display">{name}</h1>
            <p className="mt-1 text-body-sm text-fg-secondary">
              {user.email} · {role} · {signInMethod(user)} · Joined{" "}
              <LocalTime iso={user.created_at} />
            </p>
          </header>
          <Card title="Details">
            <dl className="divide-y divide-default">
              {details.map(([label, value]) => (
                <div
                  key={label}
                  className="grid gap-1 py-3 first:pt-0 last:pb-0 sm:grid-cols-[12rem_1fr]"
                >
                  <dt className="text-body-sm text-fg-secondary">{label}</dt>
                  <dd className="text-body-sm">{value}</dd>
                </div>
              ))}
            </dl>
          </Card>
          {tenancies && (
            <Card title="Tenancies">
              {tenancies.results.length === 0 ? (
                <p className="text-body-sm text-fg-secondary">
                  Not on any tenancy.
                </p>
              ) : (
                <ul className="flex flex-col gap-2">
                  {tenancies.results.map((tenancy) => (
                    <TenancyLine key={tenancy.id} tenancy={tenancy} />
                  ))}
                </ul>
              )}
            </Card>
          )}
          {access.data && catalogue.data && (
            <UserPermissionsSection
              userId={user.id}
              name={user.first_name}
              data={access.data}
              allPermissions={catalogue.data}
            />
          )}
        </div>
        <Card
          title="Account actions"
          description="Suspending and banning need a reason, which is saved in the account's history."
        >
          <UserActions
            user={user}
            footer={
              <ResetAuthenticatorButton
                userId={user.id}
                name={user.first_name}
                hasAuthenticator={user.has_authenticator}
                authenticatorWasReset={user.authenticator_was_reset}
              />
            }
          />
        </Card>
      </div>
    </>
  );
}

function TenancyLine({ tenancy }: Readonly<{ tenancy: TenancySummary }>) {
  const place = [
    tenancy.unit.name,
    tenancy.property.name,
    tenancy.property.suburb,
  ]
    .filter(Boolean)
    .join(", ");
  const since = formatDate(tenancy.start_date);
  return (
    <li className="text-body">
      <Link
        href={Route.admin.tenancy(tenancy.id)}
        className="font-medium text-fg-brand hover:underline"
      >
        {place}
      </Link>
      <span className="text-fg-secondary">
        {" "}
        · {TenancyStatusLabel[tenancy.status] ?? tenancy.status} · since {since}
      </span>
    </li>
  );
}
