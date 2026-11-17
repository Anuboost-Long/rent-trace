import { TenantTenancyStatusLabel } from "@/constants/tenancies";
import { Route } from "@/constants/web-routes";
import type { MyTenancy } from "@/types/tenancies/models";
import { formatDate } from "@/utils/format-date";
import { formatRent } from "@/utils/rent";
import Link from "next/link";

export const placeName = (tenancy: MyTenancy) =>
  tenancy.property.name ?? tenancy.property.suburb;

export const addressText = ({ property }: MyTenancy) =>
  [
    property.address_line_1,
    property.address_line_2,
    `${property.suburb} ${property.state} ${property.postcode}`,
  ]
    .filter(Boolean)
    .join(", ");

export const periodText = (tenancy: MyTenancy) =>
  tenancy.end_date
    ? `${formatDate(tenancy.start_date)} – ${formatDate(tenancy.end_date)}`
    : `From ${formatDate(tenancy.start_date)}`;

export default function MyTenancyCard({
  tenancy,
}: Readonly<{ tenancy: MyTenancy }>) {
  return (
    <Link
      href={Route.tenant.tenancy(tenancy.id)}
      className="block rounded-xl border border-foreground/15 p-5 hover:bg-foreground/5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-foreground"
    >
      <p className="text-xs text-foreground/60">
        {TenantTenancyStatusLabel[tenancy.status]}
      </p>
      <p className="mt-1 text-lg font-semibold">{placeName(tenancy)}</p>
      <p className="text-sm text-foreground/70">
        {tenancy.unit.name} · {tenancy.property.suburb} {tenancy.property.state}
      </p>
      <dl className="mt-4 space-y-1 text-sm">
        <div className="flex justify-between gap-4">
          <dt className="text-foreground/60">Dates</dt>
          <dd>{periodText(tenancy)}</dd>
        </div>
        {tenancy.rent_amount && tenancy.rent_frequency && (
          <div className="flex justify-between gap-4">
            <dt className="text-foreground/60">Rent</dt>
            <dd>{formatRent(tenancy.rent_amount, tenancy.rent_frequency)}</dd>
          </div>
        )}
        {tenancy.landlord && (
          <div className="flex justify-between gap-4">
            <dt className="text-foreground/60">Landlord</dt>
            <dd>{tenancy.landlord}</dd>
          </div>
        )}
      </dl>
    </Link>
  );
}
