import { handleGetPermissionHolders } from "@/api/services/access/serve-action";
import ButtonLink from "@/components/common/button-link";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { DetailSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import { formatDate } from "@/utils/format-date";
import { UserPlus } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import RevokeGrantButton from "../../revoke-grant-button";
import PermissionForm from "../permission-form";

export default function PermissionDetailPage({
  params,
}: PageProps<"/admin/access/permissions/[code]">) {
  return (
    <>
      <Suspense fallback={<DetailSkeleton />}>
        <PermissionDetail params={params} />
      </Suspense>
    </>
  );
}

async function PermissionDetail({
  params,
}: Readonly<Pick<PageProps<"/admin/access/permissions/[code]">, "params">>) {
  const { code } = await params;
  const { data, error } = await handleGetPermissionHolders(code);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="mt-4 text-red-600">
        {error.message}
      </p>
    );
  }

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Access", href: Route.admin.access },
          { label: "Permissions", href: Route.admin.permissions },
          { label: data.permission.name },
        ]}
      />
      <h1 className="mt-4 mb-6 text-2xl font-semibold">
        {data.permission.name}
      </h1>
      <PermissionForm permission={data.permission} />

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Who has it</h2>
        <div className="mt-3 divide-y divide-foreground/15 rounded-xl border border-foreground/15">
          <div className="p-4">
            <h3 className="mb-2 text-sm font-medium">Through roles</h3>
            {data.roles.length === 0 ? (
              <p className="text-sm text-foreground/70">
                No role gives it yet.
              </p>
            ) : (
              <>
                <ul className="flex flex-wrap gap-2">
                  {data.roles.map((role) => (
                    <li key={role.code}>
                      <Link
                        href={Route.admin.role(role.code)}
                        className="rounded-full border border-foreground/15 px-3 py-1 text-sm hover:bg-foreground/5"
                      >
                        {role.name}
                        {role.inherited && (
                          <span className="ml-1 text-foreground/60">
                            (inherited)
                          </span>
                        )}
                      </Link>
                    </li>
                  ))}
                </ul>
                <p className="mt-3 text-sm text-foreground/70">
                  {data.people_through_roles}{" "}
                  {data.people_through_roles === 1
                    ? "person has"
                    : "people have"}{" "}
                  it through these roles.
                </p>
              </>
            )}
          </div>
          <div className="p-4">
            <div className="mb-2 flex items-center justify-between gap-4">
              <h3 className="text-sm font-medium">Individual grants</h3>
              <ButtonLink
                href={`${Route.admin.grant_new}?permission=${data.permission.code}`}
                variant="quiet"
                size="sm"
                className="gap-2"
              >
                <UserPlus aria-hidden className="size-4" />
                Grant to someone
              </ButtonLink>
            </div>
            {data.grants.length === 0 ? (
              <p className="text-sm text-foreground/70">
                No individual grants.
              </p>
            ) : (
              <ul className="divide-y divide-foreground/15">
                {data.grants.map((grant) => {
                  const name = `${grant.user.first_name} ${grant.user.last_name}`;
                  return (
                    <li
                      key={grant.user.id}
                      className="flex items-start justify-between gap-4 py-2"
                    >
                      <div className="text-sm">
                        <Link
                          href={Route.admin.user(grant.user.id)}
                          className="font-medium underline-offset-2 hover:underline"
                        >
                          {name}
                        </Link>
                        <p className="text-foreground/70">
                          {grant.reason} · {formatDate(grant.created_at)}
                        </p>
                      </div>
                      <RevokeGrantButton
                        userId={grant.user.id}
                        personName={name}
                        permissionCode={data.permission.code}
                        permissionName={data.permission.name}
                      />
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
