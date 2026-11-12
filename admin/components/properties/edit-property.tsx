import { handleGetProperty } from "@/api/services/properties/serve-action";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { FormSkeleton } from "@/components/layout/page-skeletons";
import { PropertyRoutes } from "@/constants/properties";
import type { PropertyAudience } from "@/types/properties/models";
import { propertyTitle } from "@/utils/property-address";
import { notFound } from "next/navigation";
import { Suspense } from "react";

import EditPropertyForm from "./edit-property-form";

type EditPropertyProp = Readonly<{
  audience: PropertyAudience;
  params: Promise<{ id: string }>;
}>;

export default function EditPropertyPage(props: EditPropertyProp) {
  return (
    <Suspense fallback={<FormSkeleton withHeader />}>
      <EditProperty {...props} />
    </Suspense>
  );
}

async function EditProperty({ audience, params }: EditPropertyProp) {
  const { id } = await params;
  const { data: property, error } = await handleGetProperty(id, audience);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }

  return (
    <div className="max-w-xl">
      <Breadcrumbs
        trail={[
          { label: "Properties", href: PropertyRoutes[audience].list },
          {
            label: propertyTitle(property),
            href: PropertyRoutes[audience].detail(property.id),
          },
          { label: "Edit" },
        ]}
      />
      <h1 className="mt-4 mb-6 text-2xl font-semibold">Edit property</h1>
      <EditPropertyForm audience={audience} property={property} />
    </div>
  );
}
