import { handleGetProperty } from "@/api/services/properties/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { TenancyRoutes } from "@/constants/tenancies";
import type { InitialProperty } from "@/hooks/form/useCreateTenancy";
import type { TenancyAudience } from "@/types/tenancies/models";
import { propertyTitle } from "@/utils/property-address";

import CreateTenancyForm from "./create-tenancy-form";

type NewTenancyProp = Readonly<{
  audience: TenancyAudience;
  propertyId?: string;
}>;

const initialProperty = async (
  audience: TenancyAudience,
  propertyId?: string,
): Promise<InitialProperty | null> => {
  if (!propertyId || !/^\d+$/.test(propertyId)) return null;
  const { data } = await handleGetProperty(propertyId, audience);
  if (!data) return null;
  return {
    option: {
      value: String(data.id),
      label: propertyTitle(data),
      hint: `${data.suburb} ${data.state}`,
    },
    units: data.units,
  };
};

export default async function NewTenancyPage({
  audience,
  propertyId,
}: NewTenancyProp) {
  const initial = await initialProperty(audience, propertyId);

  return (
    <div className="max-w-xl">
      <Breadcrumbs
        trail={[
          { label: "Tenancies", href: TenancyRoutes[audience].list },
          { label: "New tenancy" },
        ]}
      />
      <h1 className="mt-4 text-2xl font-semibold">New tenancy</h1>
      <p className="mt-1 mb-6 text-fg-secondary">
        It starts as a draft. Invite tenants from its page afterwards.
      </p>
      <CreateTenancyForm audience={audience} initial={initial} />
    </div>
  );
}
