import { handleGetTenancy } from "@/api/services/tenancies/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import ContentSkeleton from "@/components/layout/content-skeleton";
import { PropertyRoutes } from "@/constants/properties";
import { TenancyRoutes, TenancyStatusLabel } from "@/constants/tenancies";
import { Route } from "@/constants/web-routes";
import type { TenancyAudience } from "@/types/tenancies/models";
import { formatDate } from "@/utils/format-date";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import InvitationsSection from "./invitations-section";

type TenancyDetailProp = Readonly<{
  audience: TenancyAudience;
  params: Promise<{ id: string }>;
}>;

export default function TenancyDetailPage(props: TenancyDetailProp) {
  return (
    <Suspense fallback={<ContentSkeleton />}>
      <TenancyDetail {...props} />
    </Suspense>
  );
}

async function TenancyDetail({ audience, params }: TenancyDetailProp) {
  const { id } = await params;
  const { data: tenancy, error } = await handleGetTenancy(id, audience);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }

  const details: [string, React.ReactNode][] = [
    ["Status", TenancyStatusLabel[tenancy.status]],
    [
      "Property",
      <Link
        key="property"
        href={PropertyRoutes[audience].detail(tenancy.property.id)}
        className="underline-offset-2 hover:underline"
      >
        {tenancy.property.name ?? tenancy.property.suburb}
      </Link>,
    ],
    ["Unit", tenancy.unit.name],
    ["Starts", formatDate(tenancy.start_date)],
    ["Ends", tenancy.end_date ? formatDate(tenancy.end_date) : "Open-ended"],
    ["Notes", tenancy.notes ?? "—"],
  ];

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Tenancies", href: TenancyRoutes[audience].list },
          { label: tenancy.reference_no },
        ]}
      />
      <h1 className="mt-4 mb-6 text-2xl font-semibold">
        {tenancy.reference_no}
      </h1>
      <dl className="divide-y divide-foreground/15 rounded-xl border border-foreground/15">
        {details.map(([label, value]) => (
          <div key={label} className="grid gap-1 p-4 sm:grid-cols-[12rem_1fr]">
            <dt className="text-sm text-foreground/70">{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">Tenants</h2>
        {tenancy.tenants.length === 0 ? (
          <p className="mt-2 text-foreground/70">
            No one has joined yet. Invite a tenant below.
          </p>
        ) : (
          <ul className="mt-3 divide-y divide-foreground/15 rounded-xl border border-foreground/15">
            {tenancy.tenants.map((tenant) => (
              <li
                key={tenant.user_id}
                className="flex flex-wrap items-center justify-between gap-2 p-4"
              >
                {audience === "admin" ? (
                  <Link
                    href={Route.admin.user(tenant.user_id)}
                    className="font-medium underline-offset-2 hover:underline"
                  >
                    {tenant.first_name} {tenant.last_name}
                  </Link>
                ) : (
                  <span className="font-medium">
                    {tenant.first_name} {tenant.last_name}
                  </span>
                )}
                <span className="text-sm text-foreground/70">
                  {tenant.is_primary && "Primary · "}Joined{" "}
                  {formatDate(tenant.joined_at)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <InvitationsSection
        audience={audience}
        tenancyId={tenancy.id}
        invitations={tenancy.invitations}
        closed={tenancy.status === "ENDED" || tenancy.status === "CANCELLED"}
      />
    </>
  );
}
