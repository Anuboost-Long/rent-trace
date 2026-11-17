import { handleGetMyTenancies } from "@/api/services/tenancies/serve-action";
import ButtonLink from "@/components/common/button-link";
import { TenantTenancyStatusLabel } from "@/constants/tenancies";
import { Route } from "@/constants/web-routes";
import { formatDate } from "@/utils/format-date";
import Link from "next/link";

import MyTenancyCard, { periodText, placeName } from "./my-tenancy-card";

type MyTenanciesProp = Readonly<{ showHistory: boolean }>;

export default async function MyTenancies({ showHistory }: MyTenanciesProp) {
  const { data, error } = await handleGetMyTenancies();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }

  const current = data.filter((tenancy) => tenancy.is_current);
  const history = data.filter((tenancy) => !tenancy.is_current);

  return (
    <>
      <section aria-labelledby="current-heading">
        <h2 id="current-heading" className="text-lg font-semibold">
          Where you live
        </h2>
        {current.length === 0 ? (
          <div className="mt-3 rounded-xl border border-foreground/15 p-6">
            <p className="font-medium">No current tenancy yet</p>
            <p className="mt-1 text-sm text-foreground/70">
              When a landlord adds you to a tenancy it shows up here. Looking
              for a place?
            </p>
            <ButtonLink href={Route.listings} className="mt-4">
              Browse rentals
            </ButtonLink>
          </div>
        ) : (
          <ul className="mt-3 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {current.map((tenancy) => (
              <li key={tenancy.id}>
                <MyTenancyCard tenancy={tenancy} />
              </li>
            ))}
          </ul>
        )}
      </section>

      {showHistory && history.length > 0 && (
        <section aria-labelledby="history-heading" className="mt-10">
          <h2 id="history-heading" className="text-lg font-semibold">
            Rental history
          </h2>
          <ul className="mt-3 divide-y divide-foreground/15 rounded-xl border border-foreground/15">
            {history.map((tenancy) => (
              <li key={tenancy.id}>
                <Link
                  href={Route.tenant.tenancy(tenancy.id)}
                  className="flex flex-wrap items-center justify-between gap-2 p-4 hover:bg-foreground/5 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-foreground"
                >
                  <span>
                    <span className="block font-medium">
                      {placeName(tenancy)}, {tenancy.unit.name}
                    </span>
                    <span className="block text-sm text-foreground/70">
                      {periodText(tenancy)}
                      {tenancy.left_at &&
                        ` · you left ${formatDate(tenancy.left_at)}`}
                    </span>
                  </span>
                  <span className="text-sm text-foreground/60">
                    {TenantTenancyStatusLabel[tenancy.status]}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
