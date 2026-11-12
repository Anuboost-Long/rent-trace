import { handleGetMyTenancy } from "@/api/services/tenancies/serve-action";
import TenantConditions from "@/components/conditions/tenant-conditions";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import ContentSkeleton from "@/components/layout/content-skeleton";
import { TenantTenancyStatusLabel } from "@/constants/tenancies";
import { Route } from "@/constants/web-routes";
import { formatDate } from "@/utils/format-date";
import { formatMoney, formatRent } from "@/utils/rent";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import { periodText, placeName } from "./my-tenancy-card";
import TenancyPeople from "./tenancy-people";
import TermChangeReview from "./term-change-review";
import TermHistory from "./term-history";

type MyTenancyDetailProp = Readonly<{ params: Promise<{ id: string }> }>;

export default function MyTenancyDetailPage(props: MyTenancyDetailProp) {
  return (
    <Suspense fallback={<ContentSkeleton />}>
      <MyTenancyDetail {...props} />
    </Suspense>
  );
}

async function MyTenancyDetail({ params }: MyTenancyDetailProp) {
  const { id } = await params;
  const { data: tenancy, error } = await handleGetMyTenancy(id);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }

  const details: [string, string][] = [
    ["Status", TenantTenancyStatusLabel[tenancy.status]],
    ["Place", `${placeName(tenancy)}, ${tenancy.unit.name}`],
    ["Suburb", `${tenancy.property.suburb} ${tenancy.property.state}`],
    ["Dates", periodText(tenancy)],
    ["You joined", formatDate(tenancy.joined_at)],
    ...(tenancy.left_at
      ? ([["You left", formatDate(tenancy.left_at)]] as [string, string][])
      : []),
    ["Landlord", tenancy.landlord ?? "—"],
    [
      "Rent",
      tenancy.rent_amount && tenancy.rent_frequency
        ? formatRent(tenancy.rent_amount, tenancy.rent_frequency)
        : "Not set yet",
    ],
    [
      "Bond",
      tenancy.bond_amount ? formatMoney(tenancy.bond_amount) : "Not set yet",
    ],
    ["Reference", tenancy.reference_no],
  ];

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Tenancies", href: Route.tenant.tenancies },
          { label: placeName(tenancy) },
        ]}
      />
      <h1 className="mt-4 mb-6 text-2xl font-semibold">
        {placeName(tenancy)}, {tenancy.unit.name}
      </h1>
      {tenancy.pending_change && (
        <TermChangeReview
          tenancyId={tenancy.id}
          change={tenancy.pending_change}
        />
      )}
      <dl className="divide-y divide-foreground/15 rounded-xl border border-foreground/15">
        {details.map(([label, value]) => (
          <div key={label} className="grid gap-1 p-4 sm:grid-cols-[12rem_1fr]">
            <dt className="text-sm text-foreground/70">{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>

      <TenancyPeople
        tenancyId={tenancy.id}
        youArePrimary={tenancy.is_primary}
        housemates={tenancy.housemates}
        requests={tenancy.housemate_requests}
        canInvite={tenancy.is_current}
        maxPeople={tenancy.max_occupants}
      />

      <TenantConditions notes={tenancy.unit_conditions} />

      <TermHistory changes={tenancy.term_history} />
    </>
  );
}
