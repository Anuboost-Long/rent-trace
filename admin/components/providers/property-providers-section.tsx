import {
  handleGetPropertyProviders,
  handleGetProviders,
  handleGetServiceCategories,
} from "@/api/services/providers/serve-action";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { Suspense } from "react";

import PropertyProviders from "./property-providers";

type PropertyProvidersSectionProp = Readonly<{ propertyId: number }>;

export default function PropertyProvidersSection(
  props: PropertyProvidersSectionProp,
) {
  return (
    <Suspense fallback={<ListSkeleton />}>
      <Loaded {...props} />
    </Suspense>
  );
}

async function Loaded({ propertyId }: PropertyProvidersSectionProp) {
  const [linked, saved, categories] = await Promise.all([
    handleGetPropertyProviders(propertyId),
    handleGetProviders({ page_size: 100 }),
    handleGetServiceCategories(),
  ]);
  if (linked.error) {
    return (
      <p role="alert" className="mt-10 text-red-600">
        {linked.error.message}
      </p>
    );
  }

  const linkedIds = new Set(linked.data.map((provider) => provider.id));
  const available = (saved.data?.results ?? []).filter(
    (provider) => !linkedIds.has(provider.id),
  );

  return (
    <PropertyProviders
      propertyId={propertyId}
      linked={linked.data}
      available={available}
      hasSavedProviders={(saved.data?.count ?? 0) > 0}
      categories={categories.data ?? []}
    />
  );
}
