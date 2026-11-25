import { handleGetIssueCategories } from "@/api/services/maintenance/serve-action";
import { handleGetMyTenancies } from "@/api/services/tenancies/serve-action";
import ButtonLink from "@/components/common/button-link";
import ReportIssueButton from "@/components/maintenance/report-issue-button";
import { UnitTypeLabel } from "@/constants/properties";
import { TenantTenancyStatusLabel } from "@/constants/tenancies";
import { Route } from "@/constants/web-routes";
import type { ServiceCategory } from "@/types/providers/models";
import type { MyTenancy } from "@/types/tenancies/models";
import { formatDate } from "@/utils/format-date";
import { formatMoney, formatRent } from "@/utils/rent";
import Link from "next/link";

import { addressText, placeName } from "./my-tenancy-card";

export default async function TenantHome() {
  const [{ data, error }, categories] = await Promise.all([
    handleGetMyTenancies(),
    handleGetIssueCategories(),
  ]);
  if (error) {
    return (
      <p role="alert" className="text-error">
        {error.message}
      </p>
    );
  }

  const current = data.filter((tenancy) => tenancy.is_current);
  const hasHistory = data.some((tenancy) => !tenancy.is_current);

  return (
    <section aria-labelledby="home-heading">
      <h2 id="home-heading" className="sr-only">
        Where you live
      </h2>
      {current.length === 0 ? (
        <NoTenancy />
      ) : (
        <ul className="space-y-6">
          {current.map((tenancy) => (
            <li key={tenancy.id}>
              <HomePanel tenancy={tenancy} categories={categories.data ?? []} />
            </li>
          ))}
        </ul>
      )}
      {hasHistory && (
        <p className="mt-6 text-sm text-fg-secondary">
          Looking for somewhere you lived before?{" "}
          <Link
            href={Route.tenant.tenancies}
            className="font-medium text-foreground underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border"
          >
            See your rental history
          </Link>
        </p>
      )}
    </section>
  );
}

function NoTenancy() {
  return (
    <div className="rounded-2xl border border-default p-8">
      <p className="text-lg font-semibold">No current tenancy yet</p>
      <p className="mt-1 max-w-prose text-fg-secondary">
        When a landlord adds you to a tenancy, your home shows up here. Looking
        for a place?
      </p>
      <ButtonLink href={Route.listings} className="mt-6">
        Browse rentals
      </ButtonLink>
    </div>
  );
}

function HomePanel({
  tenancy,
  categories,
}: Readonly<{ tenancy: MyTenancy; categories: ServiceCategory[] }>) {
  const facts: [string, string][] = [
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
    ["Landlord", tenancy.landlord ?? "—"],
    ["Moved in", formatDate(tenancy.joined_at)],
  ];

  return (
    <article className="overflow-hidden rounded-2xl border border-default">
      <div className="p-6 sm:p-8">
        <p className="text-sm text-fg-tertiary">
          {TenantTenancyStatusLabel[tenancy.status]}
        </p>
        <h3 className="mt-1 text-2xl font-semibold tracking-tight sm:text-3xl">
          {placeName(tenancy)}
        </h3>
        <p className="mt-1 text-fg-secondary">{addressText(tenancy)}</p>
        <p className="mt-4 text-sm">
          <span className="font-medium">{tenancy.unit.name}</span>
          <span className="text-fg-tertiary">
            {" "}
            · {UnitTypeLabel[tenancy.unit.unit_type]}
          </span>
        </p>
      </div>
      <dl className="grid grid-cols-2 gap-px border-t border-default bg-muted sm:grid-cols-4">
        {facts.map(([label, value]) => (
          <div key={label} className="bg-background p-4 sm:p-5">
            <dt className="text-sm text-fg-tertiary">{label}</dt>
            <dd className="mt-1 font-medium">{value}</dd>
          </div>
        ))}
      </dl>
      <div className="flex flex-wrap items-center gap-3 border-t border-default p-4 sm:px-8">
        {tenancy.status === "ACTIVE" && (
          <ReportIssueButton
            categories={categories}
            tenancies={[
              {
                id: tenancy.id,
                label: `${placeName(tenancy)}, ${tenancy.unit.name}`,
              },
            ]}
          />
        )}
        <ButtonLink href={Route.tenant.tenancy(tenancy.id)} variant="quiet">
          View tenancy
        </ButtonLink>
      </div>
    </article>
  );
}
