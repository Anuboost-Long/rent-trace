import { handleGetOwnerOptions } from "@/api/services/properties/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { FormSkeleton } from "@/components/layout/page-skeletons";
import { PropertyRoutes } from "@/constants/properties";
import type { PropertyAudience } from "@/types/properties/models";
import { Suspense } from "react";

import CreatePropertyForm from "./create-property-form";

type NewPropertyProp = Readonly<{ audience: PropertyAudience }>;

const COPY = {
  admin:
    "Set up a property for a landlord. They become its primary owner. You can add units once it is created.",
  landlord:
    "Add a property you own. You can add units and more photos once it is created.",
};

export default function NewPropertyPage({ audience }: NewPropertyProp) {
  return (
    <div className="max-w-xl">
      <Breadcrumbs
        trail={[
          { label: "Properties", href: PropertyRoutes[audience].list },
          { label: "New property" },
        ]}
      />
      <h1 className="mt-4 text-2xl font-semibold">New property</h1>
      <p className="mt-1 mb-6 text-fg-secondary">{COPY[audience]}</p>
      <Suspense fallback={<FormSkeleton />}>
        <NewProperty audience={audience} />
      </Suspense>
    </div>
  );
}

async function NewProperty({ audience }: NewPropertyProp) {
  if (audience === "landlord") {
    return <CreatePropertyForm audience="landlord" />;
  }
  const { data, error } = await handleGetOwnerOptions();
  if (error) {
    return (
      <p role="alert" className="text-error">
        {error.message}
      </p>
    );
  }
  return <CreatePropertyForm audience="admin" owners={data} />;
}
