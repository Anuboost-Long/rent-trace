import { handleGetMyPropertyProviders } from "@/api/services/providers/serve-action";
import Skeleton from "@/components/common/loading/skeleton";
import { Suspense } from "react";

type TenantProvidersProp = Readonly<{ tenancyId: number }>;

export default function TenantProviders(props: TenantProvidersProp) {
  return (
    <section aria-labelledby="tradespeople-heading" className="mt-12">
      <h2 id="tradespeople-heading" className="text-lg font-semibold">
        Tradespeople
      </h2>
      <p className="mt-1 mb-3 text-sm text-foreground/60">
        Contacts your landlord uses for this property.
      </p>
      <Suspense fallback={<Skeleton className="h-24 w-full" />}>
        <ProviderList {...props} />
      </Suspense>
    </section>
  );
}

async function ProviderList({ tenancyId }: TenantProvidersProp) {
  const { data, error } = await handleGetMyPropertyProviders(tenancyId);
  if (error) {
    return (
      <p role="alert" className="text-sm text-red-600">
        {error.message}
      </p>
    );
  }
  if (data.length === 0) {
    return (
      <p className="text-foreground/70">
        Your landlord hasn&apos;t added any yet. Report an issue under
        Maintenance and they&apos;ll arrange someone.
      </p>
    );
  }

  return (
    <ul className="divide-y divide-foreground/15 rounded-xl border border-foreground/15">
      {data.map((provider) => (
        <li key={provider.id} className="grid gap-1 p-4">
          <p className="font-medium">
            {provider.business_name}
            {provider.is_recommended && (
              <span className="ml-2 rounded-md border border-foreground/15 px-1.5 py-0.5 text-xs font-normal text-foreground/70">
                Preferred
              </span>
            )}
          </p>
          {provider.categories.length > 0 && (
            <p className="text-sm text-foreground/60">
              {provider.categories.map((category) => category.name).join(", ")}
            </p>
          )}
          {provider.description && (
            <p className="max-w-[65ch] text-foreground/80">
              {provider.description}
            </p>
          )}
          <dl className="mt-1 grid gap-x-6 gap-y-1 text-sm sm:grid-cols-[auto_1fr]">
            {[
              ["Contact", provider.contact_name],
              ["Phone", provider.phone_number],
              ["Email", provider.email],
              ["Website", provider.website],
              ["Address", provider.address],
            ].map(
              ([label, value]) =>
                value && (
                  <div key={label} className="contents">
                    <dt className="text-foreground/60">{label}</dt>
                    <dd className="break-words whitespace-pre-line">{value}</dd>
                  </div>
                ),
            )}
          </dl>
        </li>
      ))}
    </ul>
  );
}
